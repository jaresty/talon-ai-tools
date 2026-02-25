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
					persona.voice = val;
					persona.preset = '';
				} else if (key === 'audience') {
					persona.audience = val;
					persona.preset = '';
				} else if (key === 'tone') {
					persona.tone = val;
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
			unrecognized.push(tok);
		}
	}

	return { selected, persona, subject, addendum, unrecognized };
}
