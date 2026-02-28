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
	}
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
		expect(result).toContain('TASK 任務 (user prompt): The primary action to perform');
	});

	it('includes EXECUTION REMINDER section', () => {
		const result = renderPrompt(grammar, {}, 'x', '');
		expect(result).toContain('=== EXECUTION REMINDER ===');
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
});
