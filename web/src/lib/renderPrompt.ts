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

/**
 * Render the full structured prompt — mirrors RenderPlainText() from render.go.
 */
export function renderPrompt(
	grammar: Grammar,
	selected: Record<string, string[]>,
	subject: string,
	addendum: string,
	persona?: PersonaState
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

	// TOKENS: one bullet per active axis including persona row.
	const tokenLines: string[] = [];
	for (const axis of CONSTRAINT_AXES) {
		const tokens = effectiveSelected[axis] ?? [];
		if (tokens.length > 0) {
			tokenLines.push(`- ${axis} = ${tokens[0]}`);
		}
	}
	// Persona row.
	const personaSummary = buildPersonaTokenSummary(persona);
	tokenLines.push(personaSummary ? `- persona = ${personaSummary}` : '- persona = (none)');

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
	// Persona definition row.
	const personaDefLine = buildPersonaDefinitionLine(grammar, persona);
	defLines.push(personaDefLine);

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

function buildPersonaDefinitionLine(grammar: Grammar, persona?: PersonaState): string {
	if (!persona) return '- persona (none): No communication-identity styling applied.';

	const presetObj = persona.preset ? (grammar.persona?.presets?.[persona.preset] ?? null) : null;
	if (presetObj) {
		const key = presetObj.key ?? persona.preset;
		return `- persona (${key}): ${presetObj.label ?? ''}`.trim();
	}

	const tokens: string[] = [];
	const descs: string[] = [];

	const axes: Array<{ key: keyof typeof persona; docKey: 'voice' | 'audience' | 'tone' | 'intent' }> = [
		{ key: 'voice', docKey: 'voice' },
		{ key: 'audience', docKey: 'audience' },
		{ key: 'tone', docKey: 'tone' },
		{ key: 'intent', docKey: 'intent' },
	];
	for (const { key, docKey } of axes) {
		const tok = persona[key];
		if (tok) {
			tokens.push(tok);
			const desc = grammar.persona?.docs?.[docKey]?.[tok] ?? '';
			if (desc) descs.push(desc);
		}
	}

	if (tokens.length === 0) return '- persona (none): No communication-identity styling applied.';
	const tokenStr = tokens.join(', ');
	const descStr = descs.join(' ');
	return descStr ? `- persona (${tokenStr}): ${descStr}` : `- persona (${tokenStr})`;
}
