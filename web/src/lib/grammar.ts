export interface Grammar {
	axes: {
		definitions: Record<string, Record<string, string>>;
		labels: Record<string, Record<string, string>>;
		guidance: Record<string, Record<string, string>>;
		use_when: Record<string, Record<string, string>>;
	};
	tasks: {
		descriptions: Record<string, string>;
		labels: Record<string, string>;
		guidance: Record<string, string>;
	};
	hierarchy: {
		axis_priority: string[];
		axis_soft_caps: Record<string, number>;
		axis_incompatibilities: Record<string, Record<string, string[]>>;
	};
}

export interface TokenMeta {
	token: string;
	label: string;
	description: string;
	guidance: string;
	use_when: string;
}

let cached: Grammar | null = null;

export async function loadGrammar(): Promise<Grammar> {
	if (cached) return cached;
	const res = await fetch('/prompt-grammar.json');
	if (!res.ok) throw new Error(`Failed to load grammar: ${res.status}`);
	cached = await res.json();
	return cached!;
}

export function getAxisTokens(grammar: Grammar, axis: string): TokenMeta[] {
	const defs = grammar.axes.definitions[axis] ?? {};
	const labels = grammar.axes.labels?.[axis] ?? {};
	const guidance = grammar.axes.guidance?.[axis] ?? {};
	const use_when = grammar.axes.use_when?.[axis] ?? {};
	return Object.keys(defs)
		.sort()
		.map((token) => ({
			token,
			label: labels[token] ?? '',
			description: defs[token] ?? '',
			guidance: guidance[token] ?? '',
			use_when: use_when[token] ?? ''
		}));
}

export function getTaskTokens(grammar: Grammar): TokenMeta[] {
	const descs = grammar.tasks.descriptions ?? {};
	const labels = grammar.tasks.labels ?? {};
	const guidance = grammar.tasks.guidance ?? {};
	return Object.keys(descs)
		.sort()
		.map((token) => ({
			token,
			label: labels[token] ?? '',
			description: descs[token] ?? '',
			guidance: guidance[token] ?? '',
			use_when: ''
		}));
}

export const AXES = ['completeness', 'scope', 'method', 'form', 'channel', 'directional'];
