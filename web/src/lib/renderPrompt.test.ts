import { describe, it, expect } from 'vitest';
import { renderPrompt } from './renderPrompt.js';
import type { Grammar } from './grammar.js';

// ADR-0236: CONSTRAINT_AXES in renderPrompt.ts must include topology so
// topology token descriptions appear in the rendered CONSTRAINTS section.
describe('renderPrompt — ADR-0236 topology axis', () => {
	it('includes topology token description in CONSTRAINTS when topology is active', () => {
		const grammarWithTopology: Grammar = {
			...grammar,
			axes: {
				...grammar.axes,
				definitions: {
					...grammar.axes.definitions,
					topology: { solo: 'Unobserved synthesis-optimized reasoning.' },
				},
				kanji: {
					...grammar.axes.kanji,
					topology: { solo: '独' },
				},
			},
		};
		const result = renderPrompt(grammarWithTopology, { topology: ['solo'] }, 'show', '');
		expect(result).toContain('solo');
	});
});

const grammar: Grammar = {
	axes: {
		definitions: {
			completeness: { full: 'Comprehensive coverage of the topic.' },
			scope: { mean: 'Core meaning and central intent.', struct: 'Internal structure.' },
			form: { prose: 'Flowing narrative text.' },
			channel: { plain: 'Plain prose, no markdown.' },
			method: { probe: 'Probing analysis.' },
			directional: {}
		},
		labels: { completeness: {}, scope: {}, form: {}, channel: {}, method: {}, directional: {} },
		guidance: { completeness: {}, scope: {}, form: {}, channel: {}, method: {}, directional: {} },
		use_when: { completeness: {}, scope: {}, form: {}, channel: {}, method: {}, directional: {} },
		kanji: {
			completeness: { full: '全' },
			scope: { mean: '意', struct: '造' },
			form: { prose: '文' },
			channel: { plain: '平' },
			method: { probe: '探' },
		}
	},
	tasks: {
		descriptions: {
			show: 'Reveal the structure, content, or meaning of the subject.'
		},
		labels: { show: 'Show' },
		guidance: {}
	},
	hierarchy: {
		axis_priority: ['completeness', 'scope', 'method', 'form', 'channel', 'directional'],
		axis_soft_caps: {},
		axis_incompatibilities: {}
	},
	persona: {
		presets: {
			designer: {
				key: 'designer',
				label: 'Designer',
				voice: 'Design practitioner',
				audience: 'Product team',
				tone: 'Collaborative',
				spoken: 'as-designer'
			}
		},
		axes: { voice: [], audience: [], tone: [] }
	},
	reference_key: {
		task: 'SENTINEL_TASK_CONTRACT',
		addendum: 'SENTINEL_ADDENDUM_CONTRACT',
		constraints: 'SENTINEL_CONSTRAINTS_CONTRACT',
		constraints_axes: { completeness: 'SENTINEL_COMPLETENESS_CONTRACT', scope: 'SENTINEL_SCOPE_CONTRACT' },
		persona: 'SENTINEL_PERSONA_CONTRACT',
		subject: 'SENTINEL_SUBJECT_CONTRACT',
	},
	execution_reminder: 'EXECUTION REMINDER TEXT',
	planning_directive: 'PLANNING DIRECTIVE TEXT',
	meta_interpretation_guidance: 'META INTERPRETATION GUIDANCE TEXT'
};

describe('renderPrompt', () => {
	it('task description appears in REQUEST section', () => {
		const result = renderPrompt(grammar, { task: ['show'] }, 'hello', '');
		expect(result).not.toContain('=== TASK 任務 (DO THIS) ===');
		expect(result).toContain('Reveal the structure');
		expect(result).toContain('=== REQUEST 依頼 ===');
	});

	it('section is named REQUEST not SUBJECT', () => {
		const result = renderPrompt(grammar, {}, 'my subject text', '');
		expect(result).toContain('=== REQUEST');
		expect(result).not.toContain('=== SUBJECT');
	});

	it('includes REQUEST section with provided text', () => {
		const result = renderPrompt(grammar, {}, 'my subject text', '');
		expect(result).toContain('=== REQUEST');
		expect(result).toContain('my subject text');
	});

	it('uses placeholder when subject is empty', () => {
		const result = renderPrompt(grammar, {}, '', '');
		expect(result).toContain('(none provided)');
	});

	it('addendum text appears in REQUEST section when provided', () => {
		const result = renderPrompt(grammar, {}, 'subject', 'Focus on security');
		expect(result).not.toContain('=== ADDENDUM 追加 (CLARIFICATION) ===');
		const requestIdx = result.indexOf('=== REQUEST 依頼 ===');
		const axesIdx = result.indexOf('=== AXES');
		const requestBlock = result.slice(requestIdx, axesIdx);
		expect(requestBlock).toContain('Focus on security');
	});

	it('omits ADDENDUM section when empty', () => {
		const result = renderPrompt(grammar, {}, 'subject', '');
		expect(result).not.toContain('=== ADDENDUM');
	});

	it('includes constraint tokens with their descriptions in TOKEN DEFINITIONS', () => {
		const result = renderPrompt(grammar, { completeness: ['full'], scope: ['mean'] }, 'x', '');
		expect(result).toContain('- completeness (full 全): Comprehensive coverage');
		expect(result).toContain('- scope (mean 意): Core meaning');
	});

	it('shows (none) in AXES/TOKENS/TOKEN DEFINITIONS when no tokens selected', () => {
		const result = renderPrompt(grammar, {}, 'x', '');
		expect(result).toMatch(/=== AXES 軸.*\n\(none\)/s);
		expect(result).not.toContain('=== CONSTRAINTS 制約');
	});

	it('persona token appears in TOKENS section with preset — no collapsed persona= line', () => {
		const result = renderPrompt(grammar, {}, 'x', '', {
			preset: 'designer',
			voice: '',
			audience: '',
			tone: '',
			intent: ''
		});
		expect(result).not.toContain('=== PERSONA 人格 (STANCE) ===');
		const tokensIdx = result.indexOf('=== TOKENS 役割 ===');
		const defsIdx = result.indexOf('=== TOKEN DEFINITIONS 定義 ===');
		const tokensBlock = result.slice(tokensIdx, defsIdx);
		// Preset with no resolved axes → no individual lines → falls back to (none)
		expect(tokensBlock).toContain('- persona = (none)');
	});

	it('includes kanji in constraint tokens when available (ADR-0143)', () => {
		const result = renderPrompt(grammar, { completeness: ['full'], scope: ['struct'], method: ['probe'] }, 'x', '');
		expect(result).toContain('全'); // completeness full kanji
		expect(result).toContain('造'); // scope struct kanji
		expect(result).toContain('探'); // method probe kanji
	});

	// duplicate removed — covered by 'shows (none) in AXES/TOKENS/TOKEN DEFINITIONS' above

	it('persona axes appear as individual lines in TOKENS', () => {
		const result = renderPrompt(grammar, {}, 'x', '', {
			preset: '',
			voice: 'custom voice',
			audience: 'engineers',
			tone: 'direct',
			intent: ''
		});
		const tokensIdx = result.indexOf('=== TOKENS 役割 ===');
		const defsIdx = result.indexOf('=== TOKEN DEFINITIONS 定義 ===');
		const tokensBlock = result.slice(tokensIdx, defsIdx);
		expect(tokensBlock).toContain('- voice = custom voice');
		expect(tokensBlock).toContain('- audience = engineers');
		expect(tokensBlock).toContain('- tone = direct');
		expect(tokensBlock).not.toContain('- persona =');
	});

	it('persona intent appears as individual line in TOKENS', () => {
		const result = renderPrompt(grammar, {}, 'x', '', {
			preset: '',
			voice: '',
			audience: '',
			tone: '',
			intent: 'persuade'
		});
		const tokensIdx = result.indexOf('=== TOKENS 役割 ===');
		const defsIdx = result.indexOf('=== TOKEN DEFINITIONS 定義 ===');
		const tokensBlock = result.slice(tokensIdx, defsIdx);
		expect(tokensBlock).toContain('- intent = persuade');
	});

	it('persona TOKENS omits empty axis fields', () => {
		const result = renderPrompt(grammar, {}, 'x', '', {
			preset: '',
			voice: 'as programmer',
			audience: 'engineers',
			tone: 'direct',
			intent: ''
		});
		const tokensIdx = result.indexOf('=== TOKENS 役割 ===');
		const defsIdx = result.indexOf('=== TOKEN DEFINITIONS 定義 ===');
		const tokensBlock = result.slice(tokensIdx, defsIdx);
		expect(tokensBlock).not.toContain('- intent =');
	});

	it('does not include standalone REFERENCE KEY block (ADR-0176)', () => {
		const result = renderPrompt(grammar, {}, 'x', '');
		expect(result).not.toContain('=== REFERENCE KEY ===');
	});

	it('REQUEST section emits no ↓ contract', () => {
		const result = renderPrompt(grammar, {}, 'my text', '');
		expect(result).not.toContain('↓ [SENTINEL_SUBJECT_CONTRACT]');
	});

	it('EXECUTION REMINDER section is absent from redesigned output', () => {
		const result = renderPrompt(grammar, {}, 'x', '');
		expect(result).not.toContain('=== EXECUTION REMINDER ===');
	});

	it('META INTERPRETATION section is present when meta_interpretation_guidance is set', () => {
		const result = renderPrompt(grammar, {}, 'x', '');
		expect(result).toContain('=== META INTERPRETATION ===');
		expect(result).toContain('META INTERPRETATION GUIDANCE TEXT');
	});

	it('TOKENS section lists all tokens for an axis, not just the first', () => {
		const result = renderPrompt(grammar, { method: ['ground', 'falsify', 'atomic'] }, 'x', '');
		expect(result).toContain('- method = ground');
		expect(result).toContain('- method = falsify');
		expect(result).toContain('- method = atomic');
	});

	it('section is named FORMAT not PLANNING DIRECTIVE', () => {
		const result = renderPrompt(grammar, { completeness: ['full'] }, 'some subject', '');
		expect(result).toContain('=== FORMAT');
		expect(result).not.toContain('=== PLANNING DIRECTIVE');
	});

	it('FORMAT appears after REQUEST as final section', () => {
		const result = renderPrompt(grammar, { completeness: ['full'] }, 'some subject', '');
		const requestIdx = result.indexOf('=== REQUEST');
		const formatIdx = result.indexOf('=== FORMAT');
		expect(requestIdx).toBeGreaterThan(-1);
		expect(formatIdx).toBeGreaterThan(-1);
		expect(formatIdx).toBeGreaterThan(requestIdx);
	});

	it('output ends with a single newline', () => {
		const result = renderPrompt(grammar, {}, 'x', '');
		expect(result.endsWith('\n')).toBe(true);
		expect(result.endsWith('\n\n')).toBe(false);
	});

	// --- persona hydration tests ---

	it('persona TOKENS shows intent line when preset and intent both active', () => {
		const result = renderPrompt(grammar, {}, 'x', '', {
			preset: 'designer',
			voice: '',
			audience: '',
			tone: '',
			intent: 'persuade'
		});
		const tokensIdx = result.indexOf('=== TOKENS 役割 ===');
		const defsIdx = result.indexOf('=== TOKEN DEFINITIONS 定義 ===');
		const tokensBlock = result.slice(tokensIdx, defsIdx);
		expect(tokensBlock).toContain('- intent = persuade');
		expect(tokensBlock).not.toContain('- persona = designer');
	});

	it('persona TOKEN DEFINITIONS shows (none) when only preset with no resolved axes', () => {
		const result = renderPrompt(grammar, {}, 'x', '', {
			preset: 'designer',
			voice: '',
			audience: '',
			tone: '',
			intent: ''
		});
		const defsIdx = result.indexOf('=== TOKEN DEFINITIONS 定義 ===');
		const formatIdx = result.indexOf('=== FORMAT');
		const defsBlock = result.slice(defsIdx, formatIdx);
		expect(defsBlock).toContain('- persona (none)');
	});

	it('persona TOKEN DEFINITIONS has individual axis lines with descriptions', () => {
		const grammarWithDocs: Grammar = {
			...grammar,
			persona: {
				...grammar.persona,
				docs: {
					voice: { 'custom voice': 'A custom speaker role.' },
					audience: { engineers: 'Technical, implementation-ready.' },
					tone: {},
					intent: { coach: 'Guide growth and development.' }
				}
			}
		};
		const result = renderPrompt(grammarWithDocs, {}, 'x', '', {
			preset: '',
			voice: 'custom voice',
			audience: 'engineers',
			tone: 'direct',
			intent: 'coach'
		});
		const defsIdx = result.indexOf('=== TOKEN DEFINITIONS 定義 ===');
		const formatIdx = result.indexOf('=== FORMAT');
		const defsBlock = result.slice(defsIdx, formatIdx);
		expect(defsBlock).toContain('- voice (custom voice): A custom speaker role.');
		expect(defsBlock).toContain('- audience (engineers): Technical, implementation-ready.');
		expect(defsBlock).toContain('- tone (direct)');
		expect(defsBlock).toContain('- intent (coach): Guide growth and development.');
		expect(defsBlock).not.toContain('- persona (custom voice');
	});

	// ADR-0153 T-1: form tokens with form_default_completeness override the global default.
	it('uses form_default_completeness when no completeness token is selected (ADR-0153 T-1)', () => {
		const grammarWithDefault: Grammar = {
			...grammar,
			axes: {
				...grammar.axes,
				definitions: {
					...grammar.axes.definitions,
					completeness: {
						...grammar.axes.definitions.completeness,
						gist: 'Brief but complete.',
					},
					form: { commit: 'Conventional commit message.' },
				},
				form_default_completeness: { commit: 'gist' },
			},
		};
		const result = renderPrompt(grammarWithDefault, { task: ['show'], form: ['commit'] }, 'x', '');
		expect(result).toContain('- completeness (gist): Brief but complete.');
		expect(result).not.toContain('- completeness (full');
	});

	it('does not override explicit completeness when form_default_completeness is set (ADR-0153 T-1)', () => {
		const grammarWithDefault: Grammar = {
			...grammar,
			axes: {
				...grammar.axes,
				definitions: {
					...grammar.axes.definitions,
					form: { commit: 'Conventional commit message.' },
				},
				form_default_completeness: { commit: 'gist' },
			},
		};
		const result = renderPrompt(
			grammarWithDefault,
			{ task: ['show'], completeness: ['full'], form: ['commit'] },
			'x',
			''
		);
		expect(result).toContain('- completeness (full 全): Comprehensive coverage');
	});

	// ADR-0153 T-2: cautionary_notes render as ↳ conflict lines.
	it('renders conflict note for cautionary pair with cautionary_notes (ADR-0153 T-2)', () => {
		const grammarWithNotes: Grammar = {
			...grammar,
			axes: {
				...grammar.axes,
				definitions: {
					...grammar.axes.definitions,
					completeness: { gist: 'Brief but complete.' },
					directional: { fig: 'Span abstract and concrete.' },
				},
				cross_axis_composition: {
					completeness: {
						gist: {
							directional: {
								natural: [],
								cautionary: { fig: 'gist cannot express full vertical range' },
								cautionary_notes: { fig: 'Conflict: gist brevity limits directional range — completeness governs.' },
							},
						},
					},
				},
			},
		};
		const result = renderPrompt(
			grammarWithNotes,
			{ completeness: ['gist'], directional: ['fig'] },
			'x',
			''
		);
		expect(result).toContain('↳ Conflict: gist brevity limits directional range — completeness governs.');
	});

	it('does not render conflict note for non-conflicting pairs (ADR-0153 T-2)', () => {
		const grammarWithNotes: Grammar = {
			...grammar,
			axes: {
				...grammar.axes,
				cross_axis_composition: {
					completeness: {
						gist: {
							directional: {
								natural: [],
								cautionary: { fig: 'gist cannot express full vertical range' },
								cautionary_notes: { fig: 'Conflict: gist brevity limits directional range.' },
							},
						},
					},
				},
			},
		};
		// rog is not in cautionary_notes, so no conflict note
		const result = renderPrompt(
			grammarWithNotes,
			{ completeness: ['gist'], directional: ['rog'] },
			'x',
			''
		);
		expect(result).not.toContain('↳');
	});

	it('injects COMPOSITION RULES section when method token pair activates a composition (ADR-0227)', () => {
		const grammarWithCompositions: Grammar = {
			...grammar,
			compositions: [
				{ name: 'ground+gate', tokens: ['ground', 'gate'], prose: 'GROUND_GATE_PROSE' },
			],
		};
		const result = renderPrompt(
			grammarWithCompositions,
			{ method: ['ground', 'gate'] },
			'x',
			''
		);
		expect(result).toContain('=== COMPOSITION RULES');
		expect(result).toContain('GROUND_GATE_PROSE');
		const tokenDefsIdx = result.indexOf('=== TOKEN DEFINITIONS');
		const compositionIdx = result.indexOf('=== COMPOSITION RULES');
		const formatIdx = result.indexOf('=== FORMAT');
		expect(compositionIdx).toBeGreaterThan(tokenDefsIdx);
		expect(compositionIdx).toBeLessThan(formatIdx);
	});

	it('does not inject COMPOSITION RULES section when only one composition token is active (ADR-0227)', () => {
		const grammarWithCompositions: Grammar = {
			...grammar,
			compositions: [
				{ name: 'ground+gate', tokens: ['ground', 'gate'], prose: 'GROUND_GATE_PROSE' },
			],
		};
		const result = renderPrompt(
			grammarWithCompositions,
			{ method: ['ground'] },
			'x',
			''
		);
		expect(result).not.toContain('=== COMPOSITION RULES');
	});
});

describe('renderPrompt — AXES/TOKENS/TOKEN DEFINITIONS/FORMAT redesign', () => {
	const grammarWithAxisDescriptions: Grammar = {
		...grammar,
		axes: {
			...grammar.axes,
			axis_descriptions: {
				completeness: 'Depth of coverage — from a quick pass to exhaustive treatment.',
				method: 'Reasoning approach — how to think through the problem.',
			},
		},
		preamble: 'I want my responses formatted with a token derivation structure.',
		axis_interaction: 'Axis interaction: completeness sets the depth at which each method step runs.',
	};

	it('renders AXES 軸 section header with descriptor suffix', () => {
		const result = renderPrompt(grammarWithAxisDescriptions, { completeness: ['full'] }, 'show', '');
		expect(result).toContain('=== AXES 軸 (token types — each governs a different dimension) ===');
	});

	it('renders TOKENS 役割 section header', () => {
		const result = renderPrompt(grammarWithAxisDescriptions, { completeness: ['full'] }, 'show', '');
		expect(result).toContain('=== TOKENS 役割 ===');
	});

	it('renders TOKEN DEFINITIONS 定義 section header', () => {
		const result = renderPrompt(grammarWithAxisDescriptions, { completeness: ['full'] }, 'show', '');
		expect(result).toContain('=== TOKEN DEFINITIONS 定義 ===');
	});

	it('renders FORMAT 形式 section header with kanji', () => {
		const result = renderPrompt(grammarWithAxisDescriptions, { completeness: ['full'] }, 'show', '');
		expect(result).toContain('=== FORMAT 形式 ===');
	});

	it('does not render CONSTRAINTS 制約 (GUARDRAILS) section header', () => {
		const result = renderPrompt(grammarWithAxisDescriptions, { completeness: ['full'] }, 'show', '');
		expect(result).not.toContain('=== CONSTRAINTS 制約 (GUARDRAILS) ===');
	});

	it('AXES block contains axis description for active axis', () => {
		const result = renderPrompt(grammarWithAxisDescriptions, { completeness: ['full'] }, 'show', '');
		const axesIdx = result.indexOf('=== AXES 軸 (token types');
		const tokensIdx = result.indexOf('=== TOKENS 役割 ===');
		expect(axesIdx).toBeGreaterThan(-1);
		expect(tokensIdx).toBeGreaterThan(axesIdx);
		const axesBlock = result.slice(axesIdx, tokensIdx);
		expect(axesBlock).toContain('Depth of coverage');
	});

	it('TOKEN DEFINITIONS block contains verbatim token description', () => {
		const result = renderPrompt(grammarWithAxisDescriptions, { completeness: ['full'] }, 'show', '');
		const defsIdx = result.indexOf('=== TOKEN DEFINITIONS 定義 ===');
		const formatIdx = result.indexOf('=== FORMAT');
		expect(defsIdx).toBeGreaterThan(-1);
		expect(formatIdx).toBeGreaterThan(defsIdx);
		const defsBlock = result.slice(defsIdx, formatIdx);
		expect(defsBlock).toContain('Comprehensive coverage');
	});

	it('preamble appears before REQUEST section', () => {
		const result = renderPrompt(grammarWithAxisDescriptions, { completeness: ['full'] }, 'show', '');
		const preambleIdx = result.indexOf('I want my responses formatted with a token derivation structure.');
		const requestIdx = result.indexOf('=== REQUEST');
		expect(preambleIdx).toBeGreaterThan(-1);
		expect(requestIdx).toBeGreaterThan(preambleIdx);
	});

	it('REQUEST section uses 依頼 kanji not 題材', () => {
		const result = renderPrompt(grammarWithAxisDescriptions, { completeness: ['full'] }, 'show', '');
		expect(result).toContain('=== REQUEST 依頼 ===');
		expect(result).not.toContain('題材');
	});

	it('does not render TASK section', () => {
		const result = renderPrompt(grammarWithAxisDescriptions, { completeness: ['full'] }, 'show', '');
		expect(result).not.toContain('=== TASK');
	});

	it('does not render EXECUTION REMINDER section', () => {
		const result = renderPrompt(grammarWithAxisDescriptions, { completeness: ['full'] }, 'show', '');
		expect(result).not.toContain('=== EXECUTION REMINDER ===');
	});

	it('does not render standalone PERSONA section', () => {
		const result = renderPrompt(grammarWithAxisDescriptions, { completeness: ['full'] }, 'show', '', { preset: '', voice: 'as teacher', audience: '', tone: '', intent: '' });
		expect(result).not.toContain('=== PERSONA 人格 (STANCE) ===');
	});

	it('axis_interaction appears in AXES block', () => {
		const result = renderPrompt(grammarWithAxisDescriptions, { completeness: ['full'] }, 'show', '');
		const axesIdx = result.indexOf('=== AXES 軸 (token types');
		const tokensIdx = result.indexOf('=== TOKENS 役割 ===');
		const axesBlock = result.slice(axesIdx, tokensIdx);
		expect(axesBlock).toContain('Axis interaction:');
	});

	it('AXES bullets use "- axis: desc" format', () => {
		const result = renderPrompt(grammarWithAxisDescriptions, { completeness: ['full'] }, 'show', '');
		const axesIdx = result.indexOf('=== AXES 軸 (token types');
		const tokensIdx = result.indexOf('=== TOKENS 役割 ===');
		const axesBlock = result.slice(axesIdx, tokensIdx);
		expect(axesBlock).toContain('- completeness: Depth of coverage');
	});

	it('TOKENS bullets use "- axis = token" format', () => {
		const result = renderPrompt(grammarWithAxisDescriptions, { completeness: ['full'] }, 'show', '');
		const tokensIdx = result.indexOf('=== TOKENS 役割 ===');
		const defsIdx = result.indexOf('=== TOKEN DEFINITIONS 定義 ===');
		const tokensBlock = result.slice(tokensIdx, defsIdx);
		expect(tokensBlock).toContain('- completeness = full');
	});

	it('TOKEN DEFINITIONS bullets use "- axis (token): desc" format', () => {
		const result = renderPrompt(grammarWithAxisDescriptions, { completeness: ['full'] }, 'show', '');
		const defsIdx = result.indexOf('=== TOKEN DEFINITIONS 定義 ===');
		const formatIdx = result.indexOf('=== FORMAT');
		const defsBlock = result.slice(defsIdx, formatIdx);
		expect(defsBlock).toMatch(/- completeness \(full/);
	});

	it('persona voice appears as individual line in TOKENS section', () => {
		const result = renderPrompt(grammarWithAxisDescriptions, { completeness: ['full'] }, 'show', '', { preset: '', voice: 'as teacher', audience: '', tone: '', intent: '' });
		const tokensIdx = result.indexOf('=== TOKENS 役割 ===');
		const defsIdx = result.indexOf('=== TOKEN DEFINITIONS 定義 ===');
		const tokensBlock = result.slice(tokensIdx, defsIdx);
		expect(tokensBlock).toContain('- voice = as teacher');
	});

	it('persona = (none) when no persona active', () => {
		const result = renderPrompt(grammarWithAxisDescriptions, { completeness: ['full'] }, 'show', '');
		const tokensIdx = result.indexOf('=== TOKENS 役割 ===');
		const defsIdx = result.indexOf('=== TOKEN DEFINITIONS 定義 ===');
		const tokensBlock = result.slice(tokensIdx, defsIdx);
		expect(tokensBlock).toContain('- persona = (none)');
	});

	it('REQUEST section merges task token desc and subject', () => {
		const result = renderPrompt(grammarWithAxisDescriptions, { task: ['show'], completeness: ['full'] }, 'my subject text', '');
		const requestIdx = result.indexOf('=== REQUEST 依頼 ===');
		const axesIdx = result.indexOf('=== AXES');
		const requestBlock = result.slice(requestIdx, axesIdx);
		expect(requestBlock).toContain('my subject text');
	});
});
