export interface StarterPack {
	name: string;
	framing: string;
	command: string;
}

export interface TaskMetadataDistinction {
	token: string;
	note: string;
}

export interface TaskMetadata {
	definition: string;
	heuristics: string[];
	distinctions: TaskMetadataDistinction[];
}

export interface PersonaPreset {
	key: string;
	label: string;
	voice: string;
	audience: string;
	tone: string;
	spoken: string;
}

// ADR-0227: Pairwise token composition — activates COMPOSITION RULES section in rendered prompt.
export interface GrammarComposition {
	name: string;
	tokens: string[];
	prose: string;
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
	cautionary_notes?: Record<string, string>; // ADR-0153: render-time conflict notes (bar only, not displayed in SPA)
}

export interface Grammar {
	axes: {
		definitions: Record<string, Record<string, string>>;
		labels: Record<string, Record<string, string>>;
		guidance: Record<string, Record<string, string>>;
		use_when: Record<string, Record<string, string>>;
		kanji: Record<string, Record<string, string>>; // ADR-0143
		categories?: Record<string, Record<string, string>>; // ADR-0144: semantic family groupings for method tokens
		category_order?: Record<string, string[]>;           // ADR-0144: canonical display order for category groups
		routing_concept?: Record<string, Record<string, string>>; // ADR-0146: distilled routing concept phrases
		cross_axis_composition?: Record<string, Record<string, Record<string, CrossAxisPair>>>; // ADR-0148
		axis_descriptions?: Record<string, string>; // axis-level empty-state descriptions
		form_default_completeness?: Record<string, string>; // ADR-0153: per-form-token completeness override
		metadata?: Record<string, Record<string, TaskMetadata>>; // ADR-0155: structured metadata per axis token
	};
	tasks: {
		descriptions: Record<string, string>;
		labels: Record<string, string>;
		guidance: Record<string, string>;
		use_when?: Record<string, string>;           // ADR-0142
		kanji?: Record<string, string>;              // ADR-0143
		routing_concept?: Record<string, string>;    // ADR-0146
		metadata?: Record<string, TaskMetadata>;     // ADR-0154
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
		labels?: Record<string, Record<string, string>>;             // ADR-0170
		kanji?: Record<string, Record<string, string>>;              // ADR-0143
		routing_concept?: Record<string, Record<string, string>>;    // ADR-0146
		metadata?: Record<string, Record<string, TaskMetadata>>;     // ADR-0156
		intent?: {
			axis_tokens?: Record<string, string[]>;
		};
	};
	patterns?: GrammarPattern[];
	starter_packs?: StarterPack[]; // ADR-0144 Phase 2
	compositions?: GrammarComposition[]; // ADR-0227
	reference_key: {
		task: string;
		addendum: string;
		constraints: string;
		constraints_axes: Record<string, string>;
		persona: string;
		subject: string;
	};
	execution_reminder: string;
	planning_directive: string;
	meta_interpretation_guidance: string;
	subject_framing: string;
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
	metadata: TaskMetadata | null; // ADR-0154: structured definition, heuristics, distinctions
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
	const axisMetadata = grammar.axes.metadata?.[axis] ?? {};
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
			routing_concept: routing_concepts[token] ?? '',
			metadata: axisMetadata[token] ?? null
		}));
}

// Category order for method axis (ADR-0144). Derived from grammar JSON — not hardcoded.
export function getMethodCategoryOrder(grammar: Grammar): string[] {
	return grammar.axes.category_order?.['method'] ?? [];
}

// Returns method tokens grouped by category in canonical order (ADR-0144).
// Order is derived from grammar.axes.category_order — not hardcoded.
export function getMethodTokensByCategory(grammar: Grammar): { category: string; tokens: TokenMeta[] }[] {
	const all = getAxisTokens(grammar, 'method');
	const categoryOrder = getMethodCategoryOrder(grammar);
	const byCategory = new Map<string, TokenMeta[]>();
	const uncategorized: TokenMeta[] = [];
	for (const t of all) {
		if (!t.category) { uncategorized.push(t); continue; }
		if (!byCategory.has(t.category)) byCategory.set(t.category, []);
		byCategory.get(t.category)!.push(t);
	}
	const result: { category: string; tokens: TokenMeta[] }[] = [];
	for (const cat of categoryOrder) {
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
	const metadata = grammar.tasks.metadata ?? {};
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
			routing_concept: routing_concepts[token] ?? '',
			metadata: metadata[token] ?? null
		}));
}

export const AXES = ['topology', 'completeness', 'scope', 'method', 'form', 'channel', 'directional'];

/** Convert a human-readable persona value to a bar slug ("as designer" → "as-designer"). */
export function toPersonaSlug(s: string): string {
	return s.toLowerCase().replace(/\s+/g, '-');
}

/** Convert a multi-word axis token (e.g. 'dip bog') to its CLI slug form ('dip-bog'). */
export function toAxisTokenSlug(s: string): string {
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

// ADR-0170: extended to support 'intent' axis and populate labels from grammar.
export function getPersonaAxisTokensMeta(grammar: Grammar, axis: 'voice' | 'audience' | 'tone' | 'intent'): TokenMeta[] {
	const tokens = axis === 'intent'
		? [...(grammar.persona?.intent?.axis_tokens?.intent ?? [])].sort()
		: getPersonaAxisTokens(grammar, axis);
	const docs = grammar.persona?.docs?.[axis] ?? {};
	const labels = grammar.persona?.labels?.[axis] ?? {};
	const kanji = grammar.persona?.kanji?.[axis] ?? {};
	const routing_concepts = grammar.persona?.routing_concept?.[axis] ?? {};
	const personaMetadata = grammar.persona?.metadata?.[axis] ?? {};
	return tokens.map((token) => ({
		token,
		label: labels[token] ?? token,
		description: docs[token] ?? '',
		guidance: '',
		use_when: '',
		kanji: kanji[token] ?? '',
		category: '',
		routing_concept: routing_concepts[token] ?? '',
		metadata: personaMetadata[token] ?? null  // ADR-0156
	}));
}

/** Returns the first heuristic phrase for a preset, for use as a subtitle. */
export function getPresetHint(grammar: Grammar, key: string): string {
	return grammar.persona?.metadata?.['presets']?.[key]?.heuristics?.[0] ?? '';
}

/** Returns heuristic trigger phrases for a persona token, joined by '; '. ADR-0156. */
export function personaTokenHint(grammar: Grammar, axis: string, token: string): string {
	return grammar.persona?.metadata?.[axis]?.[token]?.heuristics?.join('; ') ?? '';
}

/** Returns distinction text for a persona token ("vs X: note; vs Y: note"). ADR-0156. */
export function personaTokenDistinctionText(grammar: Grammar, axis: string, token: string): string {
	const d = grammar.persona?.metadata?.[axis]?.[token]?.distinctions ?? [];
	return d.map((x) => `vs ${x.token}: ${x.note}`).join('; ');
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

// getChipStateWithReason returns traffic-light state plus the active tokens causing it,
// for any axis (ADR-0148 forward + reverse lookups). naturalWith lists active tokens that
// positively pair with this chip; cautionWith is [token, warning] pairs. Cautionary > natural.
export function getChipStateWithReason(
	grammar: Grammar,
	activeTokensByAxis: Record<string, string[]>,
	chipAxis: string,
	chipToken: string
): { state: 'natural' | 'cautionary' | null; naturalWith: string[]; cautionWith: Array<[string, string]> } {
	const cac = grammar.axes?.cross_axis_composition;
	if (!cac) return { state: null, naturalWith: [], cautionWith: [] };
	const seenCaution = new Set<string>();
	const seenNatural = new Set<string>();
	const naturalWith: string[] = [];
	const cautionWith: Array<[string, string]> = [];

	const addCaution = (token: string, warning: string) => {
		if (!seenCaution.has(token)) { seenCaution.add(token); cautionWith.push([token, warning]); }
	};
	const addNatural = (token: string) => {
		if (!seenNatural.has(token)) { seenNatural.add(token); naturalWith.push(token); }
	};

	// Forward: check this chip's own composition data against all active axes.
	const entry = cac[chipAxis]?.[chipToken];
	if (entry) {
		for (const [targetAxis, pair] of Object.entries(entry)) {
			for (const activeToken of (activeTokensByAxis[targetAxis] ?? [])) {
				const warning = (pair as CrossAxisPair).cautionary?.[activeToken];
				if (warning) addCaution(activeToken, warning);
				else if ((pair as CrossAxisPair).natural?.includes(activeToken)) addNatural(activeToken);
			}
		}
	}

	// Reverse: check if any active token on another axis has composition data pointing to this chip.
	for (const [otherAxis, otherTokens] of Object.entries(activeTokensByAxis)) {
		if (otherAxis === chipAxis) continue;
		for (const otherToken of otherTokens) {
			const otherEntry = cac[otherAxis]?.[otherToken]?.[chipAxis];
			if (!otherEntry) continue;
			const warning = otherEntry.cautionary?.[chipToken];
			if (warning) addCaution(otherToken, warning);
			else if (otherEntry.natural?.includes(chipToken)) addNatural(otherToken);
		}
	}

	let state: 'natural' | 'cautionary' | null = null;
	if (cautionWith.length > 0) state = 'cautionary';
	else if (naturalWith.length > 0) state = 'natural';
	return { state, naturalWith, cautionWith };
}

// getReverseChipState returns traffic-light state for a channel/form chip given active
// selections on any other axis (ADR-0148 reverse direction + form↔channel extension).
// Forward check: looks at the chip's own composition data against all active axes.
// Reverse check: looks at active tokens' composition data to see if they point to this chip.
// Cautionary takes precedence over natural.
export function getReverseChipState(
	grammar: Grammar,
	activeTokensByAxis: Record<string, string[]>,
	chipAxis: string,
	chipToken: string
): 'natural' | 'cautionary' | null {
	const cac = grammar.axes.cross_axis_composition;
	if (!cac) return null;
	let hasNatural = false;

	// Forward: check this chip's own composition data against all active axes.
	const entry = cac[chipAxis]?.[chipToken];
	if (entry) {
		for (const [targetAxis, pair] of Object.entries(entry)) {
			for (const activeToken of (activeTokensByAxis[targetAxis] ?? [])) {
				if (pair.cautionary?.[activeToken]) return 'cautionary';
				if (pair.natural?.includes(activeToken)) hasNatural = true;
			}
		}
	}

	// Reverse: check if any active token on another axis has composition data pointing to this chip.
	for (const [otherAxis, otherTokens] of Object.entries(activeTokensByAxis)) {
		if (otherAxis === chipAxis) continue;
		for (const otherToken of otherTokens) {
			const otherEntry = cac[otherAxis]?.[otherToken]?.[chipAxis];
			if (!otherEntry) continue;
			if (otherEntry.cautionary?.[chipToken]) return 'cautionary';
			if (otherEntry.natural?.includes(chipToken)) hasNatural = true;
		}
	}

	return hasNatural ? 'natural' : null;
}
