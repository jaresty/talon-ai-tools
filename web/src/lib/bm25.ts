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

const HYBRID_BM25_WEIGHT = 0.4;
const HYBRID_EMB_WEIGHT = 0.6;

function cosineSimilarity(a: Float32Array, b: number[]): number {
	if (a.length !== b.length) return 0;
	let dot = 0;
	for (let i = 0; i < a.length; i++) dot += a[i] * b[i];
	return dot;
}

// hybridRankTokens merges BM25 and cosine similarity scores (0.4/0.6 weighted).
// embedder is an async function that returns a unit-norm Float32Array for the query,
// or null to degrade to BM25-only. Tokens without an embedding field are scored
// by BM25 only.
export async function hybridRankTokens(
	tokens: TokenMeta[],
	query: string,
	embedder: ((q: string) => Promise<Float32Array>) | null
): Promise<RankedToken[]> {
	const bm25Scores = bm25Score(tokens, query);
	let maxBM25 = 0;
	bm25Scores.forEach((s) => { if (s > maxBM25) maxBM25 = s; });

	let queryVec: Float32Array | null = null;
	if (embedder) {
		try { queryVec = await embedder(query); } catch { queryVec = null; }
	}

	const ranked: RankedToken[] = [];
	for (const t of tokens) {
		const b = maxBM25 > 0 ? (bm25Scores.get(t.token) ?? 0) / maxBM25 : 0;
		const emb = (t.metadata as { embedding?: number[] }).embedding;
		const c = queryVec && emb ? cosineSimilarity(queryVec, emb) : 0;
		const score = HYBRID_BM25_WEIGHT * b + HYBRID_EMB_WEIGHT * Math.max(0, c);
		if (score > 0) ranked.push({ token: t, score });
	}
	ranked.sort((a, b) => b.score - a.score);
	return ranked;
}

// bm25RankTokens returns tokens sorted by BM25 score descending.
// Tokens with score 0 are excluded.
export function bm25RankTokens(tokens: TokenMeta[], query: string): RankedToken[] {
	const scores = bm25Score(tokens, query);
	const ranked: RankedToken[] = [];
	for (const t of tokens) {
		const score = scores.get(t.token) ?? 0;
		if (score > 0) ranked.push({ token: t, score });
	}
	ranked.sort((a, b) => b.score - a.score);
	return ranked;
}
