import { describe, it, expect } from 'vitest';
import { renderPrompt } from './renderPrompt.js';
import type { Grammar } from './grammar.js';

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
	reference_key: 'REFERENCE KEY TEXT',
	execution_reminder: 'EXECUTION REMINDER TEXT',
	meta_interpretation_guidance: 'META INTERPRETATION GUIDANCE TEXT'
};

describe('renderPrompt', () => {
	it('includes TASK section with task description', () => {
		const result = renderPrompt(grammar, { task: ['show'] }, 'hello', '');
		expect(result).toContain('=== TASK 任務 (DO THIS) ===');
		expect(result).toContain('Reveal the structure');
	});

	it('includes SUBJECT section with provided text', () => {
		const result = renderPrompt(grammar, {}, 'my subject text', '');
		expect(result).toContain('=== SUBJECT 題材 (CONTEXT) ===');
		expect(result).toContain('my subject text');
	});

	it('uses placeholder when subject is empty', () => {
		const result = renderPrompt(grammar, {}, '', '');
		expect(result).toContain('(none provided)');
	});

	it('includes ADDENDUM section when provided', () => {
		const result = renderPrompt(grammar, {}, 'subject', 'Focus on security');
		expect(result).toContain('=== ADDENDUM 追加 (CLARIFICATION) ===');
		expect(result).toContain('Focus on security');
	});

	it('omits ADDENDUM section when empty', () => {
		const result = renderPrompt(grammar, {}, 'subject', '');
		expect(result).not.toContain('=== ADDENDUM');
	});

	it('includes constraint tokens with their descriptions', () => {
		const result = renderPrompt(grammar, { completeness: ['full'], scope: ['mean'] }, 'x', '');
		expect(result).toContain('Completeness (full 全): Comprehensive coverage');
		expect(result).toContain('Scope (mean 意): Core meaning');
	});

	it('shows (none) in constraints when no tokens selected', () => {
		const result = renderPrompt(grammar, {}, 'x', '');
		expect(result).toMatch(/=== CONSTRAINTS 制約.*\n\(none\)/s);
	});

	it('includes PERSONA section with preset values', () => {
		const result = renderPrompt(grammar, {}, 'x', '', {
			preset: 'designer',
			voice: '',
			audience: '',
			tone: '',
			intent: ''
		});
		expect(result).toContain('=== PERSONA 人格 (STANCE) ===');
		expect(result).toContain('Voice: Design practitioner');
		expect(result).toContain('Audience: Product team');
	});

	it('omits ADDENDUM section when empty', () => {
		const result = renderPrompt(grammar, {}, 'subject', '');
		expect(result).not.toContain('=== ADDENDUM');
	});

	it('includes constraint tokens with their descriptions', () => {
		const result = renderPrompt(grammar, { completeness: ['full'], scope: ['mean'] }, 'x', '');
		expect(result).toContain('Completeness (full 全): Comprehensive coverage');
		expect(result).toContain('Scope (mean 意): Core meaning');
	});

	it('includes kanji in constraint tokens when available (ADR-0143)', () => {
		const result = renderPrompt(grammar, { completeness: ['full'], scope: ['struct'], method: ['probe'] }, 'x', '');
		expect(result).toContain('全'); // completeness full kanji
		expect(result).toContain('造'); // scope struct kanji
		expect(result).toContain('探'); // method probe kanji
	});

	it('shows (none) in constraints when no tokens selected', () => {
		const result = renderPrompt(grammar, {}, 'x', '');
		expect(result).toMatch(/=== CONSTRAINTS.*\n\(none\)/s);
	});

	it('uses custom persona fields when no preset', () => {
		const result = renderPrompt(grammar, {}, 'x', '', {
			preset: '',
			voice: 'custom voice',
			audience: 'engineers',
			tone: 'direct',
			intent: ''
		});
		expect(result).toContain('Voice: custom voice');
		expect(result).toContain('Audience: engineers');
	});

	it('includes Intent in PERSONA section when set', () => {
		const result = renderPrompt(grammar, {}, 'x', '', {
			preset: '',
			voice: '',
			audience: '',
			tone: '',
			intent: 'persuade'
		});
		expect(result).toContain('Intent: persuade');
	});

	it('omits Intent line when intent is empty', () => {
		const result = renderPrompt(grammar, {}, 'x', '', {
			preset: '',
			voice: 'as programmer',
			audience: 'engineers',
			tone: 'direct',
			intent: ''
		});
		expect(result).not.toContain('Intent:');
	});

	it('includes REFERENCE KEY section', () => {
		const result = renderPrompt(grammar, {}, 'x', '');
		expect(result).toContain('=== REFERENCE KEY ===');
		expect(result).toContain('REFERENCE KEY TEXT');
	});

	it('includes EXECUTION REMINDER section', () => {
		const result = renderPrompt(grammar, {}, 'x', '');
		expect(result).toContain('=== EXECUTION REMINDER ===');
	});

	it('includes META INTERPRETATION section (ADR-0166)', () => {
		const result = renderPrompt(grammar, {}, 'x', '');
		expect(result).toContain('=== META INTERPRETATION ===');
		expect(result).toContain('META INTERPRETATION GUIDANCE TEXT');
	});

	it('omits META INTERPRETATION section when meta_interpretation_guidance is empty (ADR-0166)', () => {
		const grammarNoMeta: Grammar = { ...grammar, meta_interpretation_guidance: '' };
		const result = renderPrompt(grammarNoMeta, {}, 'x', '');
		expect(result).not.toContain('=== META INTERPRETATION ===');
	});

	it('EXECUTION REMINDER appears before CONSTRAINTS section', () => {
		const result = renderPrompt(grammar, { completeness: ['full'] }, 'x', '');
		const reminderIdx = result.indexOf('=== EXECUTION REMINDER ===');
		const constraintsIdx = result.indexOf('=== CONSTRAINTS 制約 (GUARDRAILS) ===');
		expect(reminderIdx).toBeGreaterThan(-1);
		expect(constraintsIdx).toBeGreaterThan(-1);
		expect(reminderIdx).toBeLessThan(constraintsIdx);
	});

	it('EXECUTION REMINDER also appears after SUBJECT as final section', () => {
		const result = renderPrompt(grammar, { completeness: ['full'] }, 'some subject', '');
		const subjectIdx = result.indexOf('=== SUBJECT 題材 (CONTEXT) ===');
		const lastReminderIdx = result.lastIndexOf('=== EXECUTION REMINDER ===');
		expect(subjectIdx).toBeGreaterThan(-1);
		expect(lastReminderIdx).toBeGreaterThan(-1);
		expect(lastReminderIdx).toBeGreaterThan(subjectIdx);
	});

	it('output ends with a single newline', () => {
		const result = renderPrompt(grammar, {}, 'x', '');
		expect(result.endsWith('\n')).toBe(true);
		expect(result.endsWith('\n\n')).toBe(false);
	});

	// --- persona hydration tests ---

	it('renders intent alongside preset axes when both are present', () => {
		const result = renderPrompt(grammar, {}, 'x', '', {
			preset: 'designer',
			voice: '',
			audience: '',
			tone: '',
			intent: 'persuade'
		});
		// Preset axes should appear
		expect(result).toContain('Voice: Design practitioner');
		// Intent must also appear even though a preset is active
		expect(result).toContain('Intent: persuade');
	});

	it('renders persona token descriptions from grammar.persona.docs when available', () => {
		const grammarWithDocs: Grammar = {
			...grammar,
			persona: {
				...grammar.persona,
				docs: {
					voice: { 'Design practitioner': 'Leads with usability and interaction clarity.' },
					audience: {},
					tone: {}
				}
			}
		};
		const result = renderPrompt(grammarWithDocs, {}, 'x', '', {
			preset: 'designer',
			voice: '',
			audience: '',
			tone: '',
			intent: ''
		});
		// Description from docs must appear in parenthetical format matching Go CLI
		expect(result).toContain('Voice (Design practitioner): Leads with usability');
	});

	it('renders descriptions for individual (non-preset) persona axes', () => {
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
		expect(result).toContain('Voice (custom voice): A custom speaker role.');
		expect(result).toContain('Audience (engineers): Technical, implementation-ready.');
		expect(result).toContain('Intent (coach): Guide growth and development.');
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
		expect(result).toContain('Completeness (gist): Brief but complete.');
		expect(result).not.toContain('Completeness (full');
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
		expect(result).toContain('Completeness (full 全): Comprehensive coverage');
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
});
