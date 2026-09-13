/**
 * Client-side reimplementation of bar's RenderPlainText() (internal/barcli/render.go).
 * Produces the same structured prompt text that `bar build` would output.
 */

import type { Grammar } from './grammar.js';

const SUBJECT_PLACEHOLDER = '(none provided)';

const CONSTRAINT_AXES = ['topology', 'completeness', 'scope', 'method', 'form', 'channel', 'directional'];

function writeSection(heading: string, body: string): string {
	const trimmed = body.trim();
	if (!trimmed) return `${heading}\n(none)\n\n`;
	return `${heading}\n${trimmed}\n\n`;
}

function writeSectionWithContract(heading: string, contract: string, body: string): string {
	const c = contract.trim();
	const contractLine = c ? `↓ [${c}]\n` : '';
	const trimmed = body.trim();
	if (!trimmed) return `${heading}\n${contractLine}(none)\n\n`;
	return `${heading}\n${contractLine}${trimmed}\n\n`;
}

export interface PersonaState {
	preset: string;
	voice: string;
	audience: string;
	tone: string;
	intent: string;
}

export interface SeedWordsOptions {
	count: number;
	seed?: number;
}

export interface MutateOptions {
	enabled: boolean;
	// seed is optional: when provided the locus choice is reproducible (used by
	// tests); when omitted the SPA re-rolls a fresh random locus each render.
	seed?: number;
}

// mulberry32: a small, fast, seedable PRNG. Used so a given seed replays the
// same word selection within the SPA (web-only reproducibility — this does not
// match Go's math/rand sequence, by design).
function mulberry32(seed: number): () => number {
	let a = seed >>> 0;
	return function () {
		a |= 0;
		a = (a + 0x6d2b79f5) | 0;
		let t = Math.imul(a ^ (a >>> 15), 1 | a);
		t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
		return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
	};
}

/**
 * Select n words sampled without replacement from words, deterministically from
 * seed (partial Fisher-Yates). Mirrors deriveLateralSeed() in lateral_seed.go in
 * shape and guarantees (count = min(n, list); no repeats; deterministic in inputs),
 * but not in exact word choice — the SPA uses its own PRNG.
 */
export function deriveSeedWords(words: string[], seed: number, n: number): string[] {
	if (n <= 0 || words.length === 0) return [];
	const take = Math.min(n, words.length);
	const rng = mulberry32(seed);
	const pool = [...words];
	for (let i = 0; i < take; i++) {
		const j = i + Math.floor(rng() * (pool.length - i));
		[pool[i], pool[j]] = [pool[j], pool[i]];
	}
	return pool.slice(0, take);
}

/**
 * Select one active non-task token to perturb ("mutate"). Mirrors
 * deriveMutationLocus() in mutate.go in shape and guarantees (locus is an active
 * non-task token; "" when none exists), but not in exact choice — the SPA uses
 * its own PRNG, and re-rolls each render when seed is undefined.
 */
export function deriveMutationLocus(
	selected: Record<string, string[]>,
	seed?: number
): string {
	const taskTokens = new Set(selected.task ?? []);
	const candidates: string[] = [];
	for (const [axis, tokens] of Object.entries(selected)) {
		if (axis === 'task') continue;
		for (const tok of tokens) {
			if (tok && !taskTokens.has(tok)) candidates.push(tok);
		}
	}
	if (candidates.length === 0) return '';
	const roll = seed === undefined ? Math.random() : mulberry32(seed)();
	return candidates[Math.floor(roll * candidates.length)];
}

// mutationBody substitutes the locus token name into the grammar-sourced
// template (SSOT: MUTATION_INSTRUCTION in lib/metaPromptConfig.py). Mirrors
// mutationBody() in render.go, which reads the same field — so the two runtimes
// cannot drift.
function mutationBody(template: string, locus: string): string {
	return template.split('{locus}').join(locus);
}

// lateralSeedBody substitutes the comma-joined quoted word list into the
// grammar-sourced template (SSOT: LATERAL_SEED_BODY_SINGULAR / _PLURAL in
// lib/metaPromptConfig.py). Singular framing for one word, plural for several.
// Mirrors lateralSeedBody() in render.go, which reads the same fields.
function lateralSeedBody(singular: string, plural: string, words: string[]): string {
	const joined = words.map((w) => `"${w}"`).join(', ');
	const template = words.length === 1 ? singular : plural;
	return template.split('{words}').join(joined);
}

/**
 * Render the full structured prompt — mirrors RenderPlainText() from render.go.
 */
export function renderPrompt(
	grammar: Grammar,
	selected: Record<string, string[]>,
	subject: string,
	addendum: string,
	persona?: PersonaState,
	seedWords?: SeedWordsOptions,
	mutate?: MutateOptions
): string {
	const parts: string[] = [];

	// Preamble: plain user voice constant precedes all sections.
	if (grammar.preamble?.trim()) {
		parts.push(grammar.preamble.trim() + '\n\n');
	}

	// ADR-0153 T-1: apply form-token default completeness override.
	const effectiveSelected = { ...selected };
	const formTokens = effectiveSelected.form ?? [];
	if ((effectiveSelected.completeness ?? []).length === 0 && formTokens.length > 0) {
		const formDefault = grammar.axes?.form_default_completeness?.[formTokens[0]] ?? null;
		if (formDefault) {
			effectiveSelected.completeness = [formDefault];
		}
	}

	// ADR-0153 T-2: build conflict-note index.
	const conflictNotes: Record<string, Record<string, string>> = {};
	const cac = grammar.axes?.cross_axis_composition ?? {};
	for (const [axisA, byTokenA] of Object.entries(cac)) {
		for (const [tokenA, byAxisB] of Object.entries(byTokenA)) {
			if (!(effectiveSelected[axisA] ?? []).includes(tokenA)) continue;
			for (const [axisB, pair] of Object.entries(
				byAxisB as Record<string, { cautionary_notes?: Record<string, string> }>
			)) {
				const notes = pair.cautionary_notes ?? {};
				for (const [tokenB, note] of Object.entries(notes)) {
					if ((effectiveSelected[axisB] ?? []).includes(tokenB)) {
						conflictNotes[axisA] ??= {};
						conflictNotes[axisA][tokenA] = note;
					}
				}
			}
		}
	}

	// REQUEST: task token desc + addendum + subject merged into one block.
	const taskTokens = selected.task ?? [];
	const taskToken = taskTokens[0] ?? '';
	const taskDesc = taskToken ? (grammar.tasks.descriptions?.[taskToken] ?? taskToken) : '';
	const requestParts: string[] = [];
	if (taskDesc) requestParts.push(taskDesc);
	if (addendum.trim()) requestParts.push(addendum.trim());
	if (subject.trim()) requestParts.push(subject.trim());
	const requestBody = requestParts.join('\n\n') || SUBJECT_PLACEHOLDER;
	parts.push(writeSection('=== REQUEST 依頼 ===', requestBody));

	// AXES: one bullet per active axis with role description.
	const activeAxes: string[] = [];
	for (const axis of CONSTRAINT_AXES) {
		if ((effectiveSelected[axis] ?? []).length > 0) {
			activeAxes.push(axis);
		}
	}
	if (activeAxes.length === 0) {
		parts.push('=== AXES 軸 (token types — each governs a different dimension) ===\n(none)\n\n');
	} else {
		let axesBody = '';
		for (const axis of activeAxes) {
			const desc = grammar.axes?.axis_descriptions?.[axis] ?? '';
			axesBody += desc ? `- ${axis}: ${desc}\n` : `- ${axis}\n`;
		}
		if (grammar.axis_interaction?.trim()) {
			axesBody += grammar.axis_interaction.trim() + '\n';
		}
		parts.push(`=== AXES 軸 (token types — each governs a different dimension) ===\n${axesBody}\n`);
	}

	// TOKENS: one bullet per active axis including persona axes.
	const tokenLines: string[] = [];
	for (const axis of CONSTRAINT_AXES) {
		const tokens = effectiveSelected[axis] ?? [];
		for (const token of tokens) {
			tokenLines.push(`- ${axis} = ${token}`);
		}
	}
	// Persona axes: emit individual axis=token lines.
	const PERSONA_AXES = ['voice', 'audience', 'tone', 'intent'] as const;
	let personaWritten = false;
	if (persona) {
		for (const axis of PERSONA_AXES) {
			const tok = persona[axis];
			if (tok) {
				tokenLines.push(`- ${axis} = ${tok}`);
				personaWritten = true;
			}
		}
	}
	if (!personaWritten) {
		tokenLines.push('- persona = (none)');
	}

	parts.push(`=== TOKENS 役割 ===\n${tokenLines.join('\n')}\n\n`);

	// TOKEN DEFINITIONS: one bullet per active token including persona row.
	const defLines: string[] = [];
	for (const axis of CONSTRAINT_AXES) {
		const tokens = effectiveSelected[axis] ?? [];
		const kanjiMap = grammar.axes?.kanji?.[axis] ?? {};
		for (const token of tokens) {
			const desc = grammar.axes?.definitions?.[axis]?.[token] ?? '';
			const kanji = kanjiMap[token] ?? '';
			const tokenWithKanji = kanji ? `${token} ${kanji}` : token;
			if (desc) {
				let line = `- ${axis} (${tokenWithKanji}): ${desc}`;
				const note = conflictNotes[axis]?.[token];
				if (note) line += `\n  ↳ ${note}`;
				defLines.push(line);
			}
		}
	}
	// Persona definition lines (one per active axis).
	const personaDefLines = buildPersonaDefinitionLines(grammar, persona);
	defLines.push(personaDefLines);

	const defsBody = defLines.length > 0 ? defLines.join('\n') + '\n' : '(none)\n';
	parts.push(`=== TOKEN DEFINITIONS 定義 ===\n${defsBody}\n`);

	// ADR-0227: COMPOSITION RULES section when active.
	if (grammar.compositions && grammar.compositions.length > 0) {
		const allActiveTokens = new Set<string>(Object.values(selected).flat());
		const activeCompositions = grammar.compositions.filter((c) =>
			c.tokens.every((t) => allActiveTokens.has(t))
		);
		if (activeCompositions.length > 0) {
			parts.push(`=== COMPOSITION RULES 合成 (CO-PRESENCE) ===\n`);
			parts.push(`↓ [Additional rules that apply because specific token combinations are co-present. Applied on top of CONSTRAINTS.]\n`);
			for (const comp of activeCompositions) {
				parts.push(comp.prose.trim() + '\n\n');
			}
		}
	}

	// FORMAT section.
	parts.push(writeSection('=== FORMAT 形式 ===', grammar.planning_directive));

	// META INTERPRETATION section.
	if (grammar.meta_interpretation_guidance?.trim()) {
		parts.push(writeSection('=== META INTERPRETATION ===', grammar.meta_interpretation_guidance));
	}

	// LATERAL SEED: opt-in creative seed. Emitted last (mirrors render.go), only
	// when count > 0, so a render without it is unchanged.
	if (seedWords && seedWords.count > 0) {
		const words = deriveSeedWords(
			grammar.lateral_seed_words ?? [],
			seedWords.seed ?? 0,
			seedWords.count
		);
		if (words.length > 0) {
			parts.push(
				writeSection(
					'=== LATERAL SEED 種 ===',
					lateralSeedBody(grammar.lateral_seed_body_singular, grammar.lateral_seed_body_plural, words)
				)
			);
		}
	}

	// MUTATION: opt-in stance perturbation. Emitted last (mirrors render.go), only
	// when a locus is present, so a render without it is unchanged.
	if (mutate?.enabled) {
		const locus = deriveMutationLocus(selected, mutate.seed);
		if (locus) {
			parts.push(writeSection('=== MUTATION 変 ===', mutationBody(grammar.mutation_instruction, locus)));
		}
	}

	return parts.join('').trimEnd() + '\n';
}

function buildPersonaTokenSummary(persona?: PersonaState): string {
	if (!persona) return '';
	if (persona.preset) return persona.preset;
	const parts: string[] = [];
	if (persona.voice) parts.push(persona.voice);
	if (persona.audience) parts.push(persona.audience);
	if (persona.tone) parts.push(persona.tone);
	if (persona.intent) parts.push(persona.intent);
	return parts.join(', ');
}

function buildPersonaDefinitionLines(grammar: Grammar, persona?: PersonaState): string {
	if (!persona) return '- persona (none): No communication-identity styling applied.';

	const axes: Array<{ key: keyof PersonaState; docKey: 'voice' | 'audience' | 'tone' | 'intent' }> = [
		{ key: 'voice', docKey: 'voice' },
		{ key: 'audience', docKey: 'audience' },
		{ key: 'tone', docKey: 'tone' },
		{ key: 'intent', docKey: 'intent' },
	];

	const lines: string[] = [];
	for (const { key, docKey } of axes) {
		const tok = persona[key];
		if (!tok) continue;
		const desc = grammar.persona?.docs?.[docKey]?.[tok] ?? '';
		lines.push(desc ? `- ${key} (${tok}): ${desc}` : `- ${key} (${tok})`);
	}

	if (lines.length === 0) return '- persona (none): No communication-identity styling applied.';
	return lines.join('\n');
}
