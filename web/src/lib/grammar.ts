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

export interface Grammar {
	axes: {
		definitions: Record<string, Record<string, string>>;
		labels: Record<string, Record<string, string>>;
		guidance: Record<string, Record<string, string>>;
		use_when: Record<string, Record<string, string>>;
		kanji: Record<string, Record<string, string>>; // ADR-0143
	};
	tasks: {
		descriptions: Record<string, string>;
		labels: Record<string, string>;
		guidance: Record<string, string>;
		use_when?: Record<string, string>; // ADR-0142
		kanji?: Record<string, string>; // ADR-0143
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
		kanji?: Record<string, Record<string, string>>; // ADR-0143
	};
	patterns?: GrammarPattern[];
}

export interface TokenMeta {
	token: string;
	label: string;
	description: string;
	guidance: string;
	use_when: string;
	kanji: string;
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
	return Object.keys(defs)
		.sort()
		.map((token) => ({
			token,
			label: labels[token] ?? '',
			description: defs[token] ?? '',
			guidance: guidance[token] ?? '',
			use_when: use_when[token] ?? '',
			kanji: kanji[token] ?? ''
		}));
}

export function getTaskTokens(grammar: Grammar): TokenMeta[] {
	const descs = grammar.tasks.descriptions ?? {};
	const labels = grammar.tasks.labels ?? {};
	const guidance = grammar.tasks.guidance ?? {};
	const use_when = grammar.tasks.use_when ?? {};
	return Object.keys(descs)
		.sort()
		.map((token) => ({
			token,
			label: labels[token] ?? '',
			description: descs[token] ?? '',
			guidance: guidance[token] ?? '',
			use_when: use_when[token] ?? ''
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

export function getPersonaAxisTokens(grammar: Grammar, axis: 'voice' | 'audience' | 'tone'): string[] {
	return [...(grammar.persona?.axes?.[axis] ?? [])].sort();
}

export function getPersonaAxisTokensMeta(grammar: Grammar, axis: 'voice' | 'audience' | 'tone'): TokenMeta[] {
	const tokens = getPersonaAxisTokens(grammar, axis);
	const docs = grammar.persona?.docs?.[axis] ?? {};
	const use_when = grammar.persona?.use_when?.[axis] ?? {};
	return tokens.map((token) => ({
		token,
		label: token,
		description: docs[token] ?? '',
		guidance: '',
		use_when: use_when[token] ?? ''
	}));
}

export function getUsagePatterns(grammar: Grammar): GrammarPattern[] {
	return grammar.patterns ?? [];
}
