import { describe, it, expect } from 'vitest';
import { bm25Score, bm25RankTokens, hybridRankTokens } from './bm25.js';
// Each hybrid test gets its own empty cache to avoid cross-test cache pollution.
const freshCache = () => new Map<string, Float32Array>();
import type { TokenMeta } from './grammar.js';

function makeMeta(token: string, label: string, description: string, heuristics: string[] = [], distinctions: string[] = []): TokenMeta {
	return {
		token,
		label,
		description,
		guidance: '',
		use_when: '',
		kanji: '',
		category: '',
		routing_concept: '',
		metadata: { definition: description, heuristics, distinctions: distinctions.map(d => ({ token: d, note: '' })) }
	} as unknown as TokenMeta;
}

const corpus: TokenMeta[] = [
	makeMeta('gate', 'Evaluation before implementation', 'Enforces that a FAIL observation per assertion exists before implementation proceeds.', ['TDD', 'red-green-refactor'], ['chain', 'atomic']),
	makeMeta('chain', 'Derivation chain enforcement', 'Each step must reproduce its predecessor actual output verbatim before proceeding.', ['reasoning chain', 'continuity'], ['gate']),
	makeMeta('ground', 'Establish correctness through evidence', 'The gap between apparent completion and actual completion is the optimizer attack surface.', ['enforcement process', 'governing artifact'], ['verify']),
	makeMeta('probe', 'Structural diagnosis', 'Surface hidden assumptions and root causes before planning.', ['root cause', 'diagnose']),
];

// Assertion A: bm25Score returns score > 0 for tokens matching any query term (OR semantics)
describe('bm25Score', () => {
	it('A1: returns positive score for a token matching a query term', () => {
		const scores = bm25Score(corpus, 'TDD');
		expect(scores.get('gate')).toBeGreaterThan(0);
	});

	it('A2: returns 0 (or no entry) for a token not matching any query term', () => {
		const scores = bm25Score(corpus, 'TDD');
		expect(scores.get('probe') ?? 0).toBe(0);
	});

	it('A3: OR semantics — token matching one of two words scores positively', () => {
		const scores = bm25Score(corpus, 'verbatim xyzzzz');
		// 'chain' has 'verbatim' in its description; 'xyzzzz' matches nothing
		expect(scores.get('chain')).toBeGreaterThan(0);
	});
});

// Assertion B: bm25RankTokens returns tokens sorted by score descending
describe('bm25RankTokens — ordering', () => {
	it('B1: top result is most relevant token for specific query', () => {
		const ranked = bm25RankTokens(corpus, 'TDD assertion');
		expect(ranked.length).toBeGreaterThan(0);
		expect(ranked[0].token.token).toBe('gate');
	});

	it('B2: results are sorted by score descending', () => {
		const ranked = bm25RankTokens(corpus, 'predecessor output');
		// chain has 'predecessor' and 'output' in description — should rank high
		for (let i = 0; i < ranked.length - 1; i++) {
			expect(ranked[i].score).toBeGreaterThanOrEqual(ranked[i + 1].score);
		}
	});
});

// Assertion S: Porter stemming — inflected query form matches doc containing root form
describe('bm25Score — stemming', () => {
	it('S1: query with inflected form matches doc containing root form', () => {
		const stemCorpus = [
			makeMeta('routeplanner', 'Route Planner', 'optimizes route planning for navigation'),
			makeMeta('other', 'Other', 'completely unrelated content about databases'),
		];
		const scores = bm25Score(stemCorpus, 'routing');
		expect(scores.get('routeplanner')).toBeGreaterThan(0);
	});
});

// Assertion C: multi-word query where no single token matches all words still returns results
describe('bm25RankTokens — multi-word OR fallback', () => {
	it('C1: query with terms spread across different tokens returns results for each', () => {
		// 'TDD' matches gate; 'optimizer' matches ground; no single token has both in heuristics
		const ranked = bm25RankTokens(corpus, 'TDD optimizer');
		const tokenNames = ranked.map((r) => r.token.token);
		expect(tokenNames).toContain('gate');
		expect(tokenNames).toContain('ground');
	});
});

// Assertion H: hybridRankTokens — embedding-weighted hybrid search
describe('hybridRankTokens', () => {
	it('H1: with null embedder degrades to BM25-only ordering', async () => {
		const hybrid = await hybridRankTokens(corpus, 'TDD assertion', null, freshCache());
		const bm25Only = bm25RankTokens(corpus, 'TDD assertion');
		expect(hybrid.map(r => r.token.token)).toEqual(bm25Only.map(r => r.token.token));
	});

	it('H2: embedder is called with token doc text and cosine similarity influences ranking', async () => {
		// Stub returns [1,0] for the query and for text containing "root cause" (probe's heuristic),
		// [0,1] otherwise. probe should rank first despite zero BM25 overlap with the query.
		const stubEmbedder = async (text: string) =>
			(text === 'unrelated query xyz' || text.includes('root cause'))
				? new Float32Array([1, 0])
				: new Float32Array([0, 1]);
		const hybrid = await hybridRankTokens(corpus, 'unrelated query xyz', stubEmbedder, freshCache());
		expect(hybrid.length).toBeGreaterThan(0);
		expect(hybrid[0].token.token).toBe('probe');
	});

	it('H4: embedder is NOT called for tokens that have pre-computed metadata.embedding; only the query is embedded', async () => {
		// All tokens have pre-computed embeddings: probe=[1,0], others=[0,1].
		const corpusWithEmb = corpus.map(t => ({
			...t,
			metadata: { ...t.metadata, embedding: t.token === 'probe' ? [1, 0] : [0, 1] }
		})) as unknown as TokenMeta[];

		let embedderCallCount = 0;
		const stubEmbedder = async (text: string) => {
			embedderCallCount++;
			// Query returns [1,0]; token texts would return [0,1] if mistakenly called
			return text === 'unrelated query xyz' ? new Float32Array([1, 0]) : new Float32Array([0, 1]);
		};
		const hybrid = await hybridRankTokens(corpusWithEmb, 'unrelated query xyz', stubEmbedder, freshCache());
		// Only the query should have been embedded (1 call), not any token texts
		expect(embedderCallCount).toBe(1);
		// probe's pre-computed [1,0] matches query [1,0] → cosine=1, ranks first
		expect(hybrid[0].token.token).toBe('probe');
	});

	it('H3: embedder is called to embed token doc text (description+heuristics+distinctions+routing_concept) when no pre-computed embedding exists', async () => {
		// corpus tokens have NO .embedding field in metadata.
		// We use a stub embedder that returns a high-similarity vector only for
		// text containing "root cause" (the probe heuristic). Query is unrelated to
		// BM25 terms so BM25 alone would not rank probe first.
		const embeddedTexts: string[] = [];
		const stubEmbedder = async (text: string) => {
			embeddedTexts.push(text);
			// Return high similarity for text mentioning "root cause"
			return text.includes('root cause') ? new Float32Array([1, 0]) : new Float32Array([0, 1]);
		};
		// Query vector matches [1, 0] → probe should win over gate/chain/ground on cosine
		const queryEmbedder = async (text: string) => {
			if (text === 'unrelated query xyz') return new Float32Array([1, 0]);
			return stubEmbedder(text);
		};
		const hybrid = await hybridRankTokens(corpus, 'unrelated query xyz', queryEmbedder, freshCache());
		// Embedder must have been called for token descriptions (not just the query)
		expect(embeddedTexts.length).toBeGreaterThan(1);
		// probe should rank first because its doc text contains "root cause"
		expect(hybrid[0].token.token).toBe('probe');
	});
});
