export interface StarterPack {
	name: string;
	framing: string;
	command: string;
}

export interface PersonaPreset {
	key: string;
	label: string;
	voice: string;
	audience: string;
	tone: string;
	spoken: string;
}

export interface GrammarPattern {
  title: string;
  command: string;
  example: string;
  desc: string;
  tokens: Record<string, string[]>;
}

// CrossAxisPair holds natural/cautionary composition data for one axis_a+token_a+axis_b triple (ADR-0148).
export interface CrossAxisPair {
	natural: string[];
	cautionary: Record<string, string>;
}

export interface Grammar {
	axes: {
		definitions: Record<string, Record<string, string>>;
		labels: Record<string, Record<string, string>>;
		guidance: Record<string, Record<string, string>>;
		use_when: Record<string, Record<string, string>>;
		kanji: Record<string, Record<string, string>>; // ADR-0143
		categories?: Record<string, Record<string, string>>; // ADR-0144: semantic family groupings for method tokens
		routing_concept?: Record<string, Record<string, string>>; // ADR-0146: distilled routing concept phrases
		cross_axis_composition?: Record<string, Record<string, Record<string, CrossAxisPair>>>; // ADR-0148
		axis_descriptions?: Record<string, string>; // axis-level empty-state descriptions
	};
	tasks: {
		descriptions: Record<string, string>;
		labels: Record<string, string>;
		guidance: Record<string, string>;
		use_when?: Record<string, string>;           // ADR-0142
		kanji?: Record<string, string>;              // ADR-0143
		routing_concept?: Record<string, string>;    // ADR-0146
	};
	hierarchy: {
		axis_priority: string[];
		axis_soft_caps: Record<string, number>;
		axis_incompatibilities: Record<string, Record<string, string[]>>;
	};
	persona: {
		presets: Record<string, PersonaPreset>;
		axes: {
			voice: string[];
			audience: string[];
			tone: string[];
		};
		docs?: Record<string, Record<string, string>>;
		use_when?: Record<string, Record<string, string>>;
		guidance?: Record<string, Record<string, string>>;
		kanji?: Record<string, Record<string, string>>;              // ADR-0143
		routing_concept?: Record<string, Record<string, string>>;    // ADR-0146
		intent?: {
			axis_tokens?: Record<string, string[]>;
		};
	};
	patterns?: GrammarPattern[];
	starter_packs?: StarterPack[]; // ADR-0144 Phase 2
}

export interface TokenMeta {
	token: string;
	label: string;
	description: string;
	guidance: string;
	use_when: string;
	kanji: string;
	category: string; // ADR-0144: semantic family for method tokens; empty for other axes
	routing_concept: string; // ADR-0146: distilled routing concept phrase
}

import { base } from '$app/paths';

let cached: Grammar | null = null;

export async function loadGrammar(): Promise<Grammar> {
	if (cached) return cached;
	const res = await fetch(`${base}/prompt-grammar.json`, { cache: 'no-cache' });
	if (!res.ok) throw new Error(`Failed to load grammar: ${res.status}`);
	cached = await res.json();
	return cached!;
}

export function getAxisTokens(grammar: Grammar, axis: string): TokenMeta[] {
	const defs = grammar.axes.definitions[axis] ?? {};
	const labels = grammar.axes.labels?.[axis] ?? {};
	const guidance = grammar.axes.guidance?.[axis] ?? {};
	const use_when = grammar.axes.use_when?.[axis] ?? {};
	const kanji = grammar.axes.kanji?.[axis] ?? {};
	const categories = grammar.axes.categories?.[axis] ?? {};
	const routing_concepts = grammar.axes.routing_concept?.[axis] ?? {};
	return Object.keys(defs)
		.sort()
		.map((token) => ({
			token,
			label: labels[token] ?? '',
			description: defs[token] ?? '',
			guidance: guidance[token] ?? '',
			use_when: use_when[token] ?? '',
			kanji: kanji[token] ?? '',
			category: categories[token] ?? '',
			routing_concept: routing_concepts[token] ?? ''
		}));
}

// Category order for method axis (ADR-0144)
export const METHOD_CATEGORY_ORDER = [
	'Reasoning', 'Exploration', 'Structural', 'Diagnostic',
	'Actor-centered', 'Temporal/Dynamic', 'Comparative', 'Generative'
];

// Returns method tokens grouped by category in canonical order (ADR-0144).
// Each entry is { category: string, tokens: TokenMeta[] }.
export function getMethodTokensByCategory(grammar: Grammar): { category: string; tokens: TokenMeta[] }[] {
	const all = getAxisTokens(grammar, 'method');
	const byCategory = new Map<string, TokenMeta[]>();
	const uncategorized: TokenMeta[] = [];
	for (const t of all) {
		if (!t.category) { uncategorized.push(t); continue; }
		if (!byCategory.has(t.category)) byCategory.set(t.category, []);
		byCategory.get(t.category)!.push(t);
	}
	const result: { category: string; tokens: TokenMeta[] }[] = [];
	for (const cat of METHOD_CATEGORY_ORDER) {
		const tokens = byCategory.get(cat);
		if (tokens && tokens.length > 0) result.push({ category: cat, tokens });
	}
	if (uncategorized.length > 0) result.push({ category: '', tokens: uncategorized });
	return result;
}

export function getTaskTokens(grammar: Grammar): TokenMeta[] {
	const descs = grammar.tasks.descriptions ?? {};
	const labels = grammar.tasks.labels ?? {};
	const guidance = grammar.tasks.guidance ?? {};
	const use_when = grammar.tasks.use_when ?? {};
	const kanji = grammar.tasks.kanji ?? {};
	const routing_concepts = grammar.tasks.routing_concept ?? {};
	return Object.keys(descs)
		.sort()
		.map((token) => ({
			token,
			label: labels[token] ?? '',
			description: descs[token] ?? '',
			guidance: guidance[token] ?? '',
			use_when: use_when[token] ?? '',
			kanji: kanji[token] ?? '',
			category: '',
			routing_concept: routing_concepts[token] ?? ''
		}));
}

export const AXES = ['completeness', 'scope', 'method', 'form', 'channel', 'directional'];

/** Convert a human-readable persona value to a bar slug ("as designer" → "as-designer"). */
export function toPersonaSlug(s: string): string {
	return s.toLowerCase().replace(/\s+/g, '-');
}

export function getPersonaPresets(grammar: Grammar): PersonaPreset[] {
	return Object.values(grammar.persona?.presets ?? {}).sort((a, b) =>
		a.label.localeCompare(b.label)
	);
}

export function getPersonaIntentTokens(grammar: Grammar): string[] {
	return [...(grammar.persona?.intent?.axis_tokens?.intent ?? [])].sort();
}

export function getPersonaAxisTokens(grammar: Grammar, axis: 'voice' | 'audience' | 'tone'): string[] {
	return [...(grammar.persona?.axes?.[axis] ?? [])].sort();
}

export function getPersonaAxisTokensMeta(grammar: Grammar, axis: 'voice' | 'audience' | 'tone'): TokenMeta[] {
	const tokens = getPersonaAxisTokens(grammar, axis);
	const docs = grammar.persona?.docs?.[axis] ?? {};
	const use_when = grammar.persona?.use_when?.[axis] ?? {};
	const guidance = grammar.persona?.guidance?.[axis] ?? {};
	const kanji = grammar.persona?.kanji?.[axis] ?? {};
	const routing_concepts = grammar.persona?.routing_concept?.[axis] ?? {};
	return tokens.map((token) => ({
		token,
		label: token,
		description: docs[token] ?? '',
		guidance: guidance[token] ?? '',
		use_when: use_when[token] ?? '',
		kanji: kanji[token] ?? '',
		category: '',
		routing_concept: routing_concepts[token] ?? ''
	}));
}

export function getUsagePatterns(grammar: Grammar): GrammarPattern[] {
	return grammar.patterns ?? [];
}

export function getStarterPacks(grammar: Grammar): StarterPack[] {
	return grammar.starter_packs ?? [];
}

// getCompositionData returns the cross-axis composition entry for a channel/form token (ADR-0148).
// Returns null if no entry is defined. The result is keyed by partner axis, each value being a
// CrossAxisPair with natural token lists and cautionary token→warning maps.
export function getCompositionData(
	grammar: Grammar,
	axis: string,
	token: string
): Record<string, CrossAxisPair> | null {
	const cac = grammar.axes.cross_axis_composition;
	if (!cac) return null;
	const byToken = cac[axis];
	if (!byToken) return null;
	const entry = byToken[token];
	return entry ?? null;
}

// getChipState returns the traffic-light state for a chip token given active selections (ADR-0148).
// Iterates all channel and form entries in activeTokensByAxis. Returns 'cautionary' if any active
// channel/form has a cautionary entry for the chip token on the given axis; 'natural' if any has
// a natural listing; null if none match. Cautionary takes precedence over natural.
// Scope: intended for task and completeness axes only (audience excluded per ADR-0148 §Chip scope).
export function getChipState(
	grammar: Grammar,
	activeTokensByAxis: Record<string, string[]>,
	chipAxis: string,
	chipToken: string
): 'natural' | 'cautionary' | null {
	const cac = grammar.axes.cross_axis_composition;
	if (!cac) return null;
	let hasNatural = false;
	for (const channelAxis of ['channel', 'form']) {
		const activeTokens = activeTokensByAxis[channelAxis] ?? [];
		for (const activeToken of activeTokens) {
			const entry = cac[channelAxis]?.[activeToken]?.[chipAxis];
			if (!entry) continue;
			if (entry.cautionary?.[chipToken]) return 'cautionary';
			if (entry.natural?.includes(chipToken)) hasNatural = true;
		}
	}
	return hasNatural ? 'natural' : null;
}

// getReverseChipState returns traffic-light state for a channel/form chip given active
// task/completeness selections (ADR-0148 reverse direction). Checks whether any active
// task/completeness token appears in the chip's own natural or cautionary lists.
// Cautionary takes precedence over natural.
export function getReverseChipState(
	grammar: Grammar,
	activeTokensByAxis: Record<string, string[]>,
	chipAxis: string,
	chipToken: string
): 'natural' | 'cautionary' | null {
	const cac = grammar.axes.cross_axis_composition;
	if (!cac) return null;
	const entry = cac[chipAxis]?.[chipToken];
	if (!entry) return null;
	let hasNatural = false;
	for (const taskAxis of ['task', 'completeness']) {
		const pair = entry[taskAxis];
		if (!pair) continue;
		for (const activeToken of (activeTokensByAxis[taskAxis] ?? [])) {
			if (pair.cautionary?.[activeToken]) return 'cautionary';
			if (pair.natural?.includes(activeToken)) hasNatural = true;
		}
	}
	return hasNatural ? 'natural' : null;
}
