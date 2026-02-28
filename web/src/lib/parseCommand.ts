import type { Grammar } from './grammar.js';
import type { PersonaState } from './renderPrompt.js';

export interface ParseResult {
	selected: Record<string, string[]>;
	persona: PersonaState;
	subject: string;
	addendum: string;
	unrecognized: string[];
}

const FLAG_RE = /--(?:subject|addendum)\s+"(?:[^"\\]|\\.)*"/g;
const QUOTED_FLAG_RE = /^--([a-z]+)\s+"((?:[^"\\]|\\.)*)"$/;

/** Extract --flag "value" pairs from a bar command string. */
function extractFlag(cmd: string, flag: string): [string, string] {
	const re = new RegExp(`--${flag}\\s+"((?:[^"\\\\]|\\\\.)*)"`, 'g');
	const match = re.exec(cmd);
	if (!match) return [cmd, ''];
	return [cmd.replace(match[0], '').trim(), match[1].replace(/\\"/g, '"')];
}

/** Build a map from token → axis, covering all grammar axes and tasks. */
function buildTokenIndex(grammar: Grammar): Map<string, string> {
	const index = new Map<string, string>();
	for (const token of Object.keys(grammar.tasks.descriptions ?? {})) {
		index.set(token, 'task');
	}
	for (const [axis, defs] of Object.entries(grammar.axes.definitions ?? {})) {
		for (const token of Object.keys(defs)) {
			index.set(token, axis);
		}
	}
	return index;
}

/**
 * Resolve a persona token value (possibly a slug like "as-designer") to its
 * canonical form ("as designer") by checking against the axis token list.
 * Falls back to the original value if no match is found.
 */
function resolvePersonaTokenSlug(val: string, axisTokens: string[]): string {
	if (axisTokens.includes(val)) return val;
	const deslug = val.replace(/-/g, ' ');
	if (axisTokens.includes(deslug)) return deslug;
	const lower = deslug.toLowerCase();
	const match = axisTokens.find((t) => t.toLowerCase() === lower);
	return match ?? val;
}

/** Build a map from positional persona value → persona sub-axis (voice/audience/tone/intent).
 *  Indexes both canonical forms ("as designer") and their slug equivalents ("as-designer")
 *  so that SPA-generated slug commands round-trip cleanly.
 */
function buildPersonaIndex(grammar: Grammar): Map<string, string> {
	const index = new Map<string, string>();
	const addTokens = (tokens: string[], axis: string) => {
		for (const v of tokens) {
			index.set(v, axis);
			const slug = v.toLowerCase().replace(/\s+/g, '-');
			if (slug !== v) index.set(slug, axis);
		}
	};
	addTokens(grammar.persona.axes.voice ?? [], 'voice');
	addTokens(grammar.persona.axes.audience ?? [], 'audience');
	addTokens(grammar.persona.axes.tone ?? [], 'tone');
	const intentTokens = grammar.persona.intent?.axis_tokens?.['intent'] ?? [];
	for (const v of intentTokens) index.set(v, 'intent');
	return index;
}

const PERSONA_KEYS = new Set(['voice', 'audience', 'tone', 'intent', 'persona']);

/**
 * Parse a `bar build <tokens> [--subject "..."] [--addendum "..."]` command
 * string into structured state.
 */
export function parseCommand(raw: string, grammar: Grammar): ParseResult {
	let cmd = raw.trim();

	// Strip "bar build" prefix (case-insensitive, optional "bar")
	cmd = cmd.replace(/^bar\s+build\s*/i, '').replace(/^build\s*/i, '');

	// Extract --subject and --addendum flags
	let subject = '';
	let addendum = '';
	[cmd, subject] = extractFlag(cmd, 'subject');
	[cmd, addendum] = extractFlag(cmd, 'addendum');

	const tokenIndex = buildTokenIndex(grammar);
	const personaIndex = buildPersonaIndex(grammar);

	const selected: Record<string, string[]> = {
		task: [],
		completeness: [],
		scope: [],
		method: [],
		form: [],
		channel: [],
		directional: []
	};
	const persona: PersonaState = { preset: '', voice: '', audience: '', tone: '', intent: '' };
	const unrecognized: string[] = [];

	const rawTokens = cmd.trim().split(/\s+/).filter(Boolean);

	for (const tok of rawTokens) {
		if (tok.startsWith('--')) {
			// Unknown flag — skip silently (already extracted subject/addendum)
			continue;
		}

		if (tok.includes('=')) {
			const eqIdx = tok.indexOf('=');
			const key = tok.slice(0, eqIdx).toLowerCase();
			const val = tok.slice(eqIdx + 1);
			if (PERSONA_KEYS.has(key)) {
				if (key === 'persona') {
					persona.preset = val;
					persona.voice = '';
					persona.audience = '';
					persona.tone = '';
				} else if (key === 'voice') {
					persona.voice = resolvePersonaTokenSlug(val, grammar.persona.axes.voice ?? []);
					persona.preset = '';
				} else if (key === 'audience') {
					persona.audience = resolvePersonaTokenSlug(val, grammar.persona.axes.audience ?? []);
					persona.preset = '';
				} else if (key === 'tone') {
					persona.tone = resolvePersonaTokenSlug(val, grammar.persona.axes.tone ?? []);
					persona.preset = '';
				} else if (key === 'intent') {
					persona.intent = val;
				}
			} else {
				unrecognized.push(tok);
			}
			continue;
		}

		const axis = tokenIndex.get(tok);
		if (axis) {
			if (!selected[axis]) selected[axis] = [];
			if (!selected[axis].includes(tok)) {
				selected[axis].push(tok);
			}
		} else {
			const personaAxis = personaIndex.get(tok);
			if (personaAxis === 'voice') { persona.voice = resolvePersonaTokenSlug(tok, grammar.persona.axes.voice ?? []); persona.preset = ''; }
			else if (personaAxis === 'audience') { persona.audience = resolvePersonaTokenSlug(tok, grammar.persona.axes.audience ?? []); persona.preset = ''; }
			else if (personaAxis === 'tone') { persona.tone = resolvePersonaTokenSlug(tok, grammar.persona.axes.tone ?? []); persona.preset = ''; }
			else if (personaAxis === 'intent') { persona.intent = tok; }
			else { unrecognized.push(tok); }
		}
	}

	return { selected, persona, subject, addendum, unrecognized };
}
