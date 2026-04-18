import { describe, it, expect } from 'vitest';
import { bm25Score, bm25RankTokens } from './bm25.js';
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
