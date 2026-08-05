// BM25 ranking for token filter (ADR-0232).
// Ported from internal/barcli/bm25.go.

import { stemmer } from 'stemmer';
import type { TokenMeta } from './grammar.js';

const BM25_K1 = 1.5;
const BM25_B = 0.75;
const TITLE_WEIGHT = 5;

export interface RankedToken {
	token: TokenMeta;
	score: number;
}

function tokenize(s: string): string[] {
	return s
		.toLowerCase()
		.split(/[^a-z0-9_]+/)
		.filter((w) => w.length > 1)
		.map(stemmer);
}

function docTitle(t: TokenMeta): string {
	return t.token + ' ' + t.label;
}

function docBody(t: TokenMeta): string {
	const parts: string[] = [t.description];
	if (t.metadata?.definition) parts.push(t.metadata.definition);
	if (t.metadata?.heuristics?.length) parts.push(t.metadata.heuristics.join(' '));
	if (t.metadata?.distinctions?.length)
		parts.push(t.metadata.distinctions.map((d) => d.token + ' ' + d.note).join(' '));
	return parts.join(' ');
}

// bm25Score returns a Map from token name to BM25 score.
// Tokens with score 0 are excluded from the map.
export function bm25Score(tokens: TokenMeta[], query: string): Map<string, number> {
	const terms = tokenize(query);
	if (terms.length === 0) return new Map();

	// Build per-doc term frequency maps.
	type DocInfo = { tf: Map<string, number>; len: number };
	const docs: DocInfo[] = tokens.map((t) => {
		const tf = new Map<string, number>();
		for (const term of tokenize(docTitle(t))) tf.set(term, (tf.get(term) ?? 0) + TITLE_WEIGHT);
		for (const term of tokenize(docBody(t))) tf.set(term, (tf.get(term) ?? 0) + 1);
		const len = tokenize(docTitle(t)).length * TITLE_WEIGHT + tokenize(docBody(t)).length;
		return { tf, len };
	});

	const N = docs.length;
	const totalLen = docs.reduce((s, d) => s + d.len, 0);
	const avgdl = totalLen / Math.max(N, 1);

	// IDF per term.
	const idf = new Map<string, number>();
	for (const term of terms) {
		const df = docs.filter((d) => (d.tf.get(term) ?? 0) > 0).length;
		idf.set(term, Math.log((N - df + 0.5) / (df + 0.5) + 1));
	}

	const scores = new Map<string, number>();
	tokens.forEach((t, i) => {
		const d = docs[i];
		let score = 0;
		for (const term of terms) {
			const tf = d.tf.get(term) ?? 0;
			if (tf === 0) continue;
			const dl = d.len;
			score +=
				(idf.get(term) ?? 0) *
				(tf * (BM25_K1 + 1)) /
				(tf + BM25_K1 * (1 - BM25_B + BM25_B * (dl / avgdl)));
		}
		if (score > 0) scores.set(t.token, score);
	});
	return scores;
}

const RRF_K = 60;

function cosineSimilarity(a: Float32Array, b: Float32Array): number {
	if (a.length !== b.length) return 0;
	let dot = 0;
	for (let i = 0; i < a.length; i++) dot += a[i] * b[i];
	return dot;
}

// Full text used to embed a token: description + heuristics + distinctions + routing_concept.
function tokenDocText(t: TokenMeta): string {
	const parts: string[] = [t.description];
	if (t.routing_concept) parts.push(t.routing_concept);
	if (t.metadata?.definition) parts.push(t.metadata.definition);
	if (t.metadata?.heuristics?.length) parts.push(t.metadata.heuristics.join(' '));
	if (t.metadata?.distinctions?.length)
		parts.push(t.metadata.distinctions.map((d) => d.token + ' ' + d.note).join(' '));
	return parts.join(' ');
}

// rrfFuse merges ranked lists via Reciprocal Rank Fusion: Σ 1/(k + rank_i(d)).
function rrfFuse(lists: string[][], k: number): Map<string, number> {
	const scores = new Map<string, number>();
	for (const list of lists) {
		list.forEach((id, idx) => {
			scores.set(id, (scores.get(id) ?? 0) + 1 / (k + idx + 1));
		});
	}
	return scores;
}

// Shared production cache: token name → embedding vector. Populated lazily on first hybrid search.
export const sharedTokenEmbCache = new Map<string, Float32Array>();

// hybridRankTokens fuses three ranked lists via RRF(k=60):
//   1. BM25-title (token name + label only)
//   2. BM25-body (definition + heuristics + distinctions only)
//   3. Cosine similarity (embeddings)
// embedder returns a unit-norm Float32Array or null to degrade to BM25-only.
// Token embeddings are cached in tokenEmbCache (pass a fresh Map in tests).
export async function hybridRankTokens(
	tokens: TokenMeta[],
	query: string,
	embedder: ((q: string) => Promise<Float32Array | null>) | null,
	tokenEmbCache: Map<string, Float32Array> = sharedTokenEmbCache
): Promise<RankedToken[]> {
	// BM25-title corpus: score using token+label as the entire document text.
	const titleOnlyTokens = tokens.map((t) => ({
		...t,
		description: t.token + ' ' + t.label,
		metadata: { definition: '', heuristics: [], distinctions: [] }
	} as unknown as TokenMeta));
	const titleScores = bm25Score(titleOnlyTokens, query);
	const titleList = [...titleScores.entries()].sort((a, b) => b[1] - a[1]).map(([id]) => id);

	// BM25-body corpus: score using definition+heuristics+distinctions only.
	const bodyText = (t: TokenMeta): string => {
		const parts: string[] = [];
		if (t.metadata?.definition) parts.push(t.metadata.definition);
		if (t.metadata?.heuristics?.length) parts.push(t.metadata.heuristics.join(' '));
		if (t.metadata?.distinctions?.length)
			parts.push(t.metadata.distinctions.map((d) => d.token + ' ' + d.note).join(' '));
		return parts.join(' ');
	};
	const bodyOnlyTokens = tokens.map((t) => ({
		...t,
		description: bodyText(t),
		metadata: { definition: '', heuristics: [], distinctions: [] }
	} as unknown as TokenMeta));
	const bodyScores = bm25Score(bodyOnlyTokens, query);
	const bodyList = [...bodyScores.entries()].sort((a, b) => b[1] - a[1]).map(([id]) => id);

	// Cosine similarity list.
	let queryVec: Float32Array | null = null;
	if (embedder) {
		try { queryVec = await embedder(query); } catch { queryVec = null; }
	}
	if (queryVec && embedder) {
		await Promise.all(tokens.map(async (t) => {
			if (tokenEmbCache.has(t.token)) return;
			const precomputed = (t.metadata as { embedding?: number[] } | null)?.embedding;
			if (precomputed) {
				tokenEmbCache.set(t.token, new Float32Array(precomputed));
				return;
			}
			try {
				const vec = await embedder(tokenDocText(t));
				if (vec) tokenEmbCache.set(t.token, vec);
			} catch { /* leave uncached */ }
		}));
	}
	const cosineList: string[] = queryVec
		? tokens
			.map((t) => {
				const vec = tokenEmbCache.get(t.token);
				return { id: t.token, score: vec ? Math.max(0, cosineSimilarity(queryVec!, vec)) : 0 };
			})
			.filter((x) => x.score > 0)
			.sort((a, b) => b.score - a.score)
			.map((x) => x.id)
		: [];

	// RRF fusion across all three lists.
	const fused = rrfFuse([titleList, bodyList, cosineList], RRF_K);
	const ranked: RankedToken[] = [];
	for (const t of tokens) {
		const score = fused.get(t.token) ?? 0;
		if (score > 0) ranked.push({ token: t, score });
	}
	ranked.sort((a, b) => b.score - a.score);
	return ranked;
}

// bm25RankTokens ranks tokens via RRF across four per-field corpora:
// title, heuristics, distinctions, definition. Tokens absent from all field rankings are excluded.
export function bm25RankTokens(tokens: TokenMeta[], query: string): RankedToken[] {
	const titleList = [...bm25Score(tokens.map((t) => ({
		...t,
		description: t.token + ' ' + t.label,
		metadata: { definition: '', heuristics: [], distinctions: [] }
	} as unknown as TokenMeta)), query).entries()].sort((a, b) => b[1] - a[1]).map(([id]) => id);

	const heuristicsList = [...bm25Score(tokens.map((t) => ({
		...t,
		description: t.metadata?.heuristics?.join(' ') ?? '',
		metadata: { definition: '', heuristics: [], distinctions: [] }
	} as unknown as TokenMeta)), query).entries()].sort((a, b) => b[1] - a[1]).map(([id]) => id);

	const distinctionsList = [...bm25Score(tokens.map((t) => ({
		...t,
		description: t.metadata?.distinctions?.map((d) => d.token + ' ' + d.note).join(' ') ?? '',
		metadata: { definition: '', heuristics: [], distinctions: [] }
	} as unknown as TokenMeta)), query).entries()].sort((a, b) => b[1] - a[1]).map(([id]) => id);

	const definitionList = [...bm25Score(tokens.map((t) => ({
		...t,
		description: t.metadata?.definition ?? '',
		metadata: { definition: '', heuristics: [], distinctions: [] }
	} as unknown as TokenMeta)), query).entries()].sort((a, b) => b[1] - a[1]).map(([id]) => id);

	const fused = rrfFuse([titleList, heuristicsList, distinctionsList, definitionList], RRF_K);
	const ranked: RankedToken[] = [];
	for (const t of tokens) {
		const score = fused.get(t.token) ?? 0;
		if (score > 0) ranked.push({ token: t, score });
	}
	ranked.sort((a, b) => b.score - a.score);
	return ranked;
}
