import { describe, it, expect } from 'vitest';
import { renderPrompt } from './renderPrompt.js';
import type { Grammar } from './grammar.js';

const grammar: Grammar = {
	axes: {
		definitions: {
			completeness: { full: 'Comprehensive coverage of the topic.' },
			scope: { mean: 'Core meaning and central intent.' },
			form: { prose: 'Flowing narrative text.' },
			channel: { plain: 'Plain prose, no markdown.' },
			method: {},
			directional: {}
		},
		labels: { completeness: {}, scope: {}, form: {}, channel: {}, method: {}, directional: {} },
		guidance: { completeness: {}, scope: {}, form: {}, channel: {}, method: {}, directional: {} },
		use_when: { completeness: {}, scope: {}, form: {}, channel: {}, method: {}, directional: {} }
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
		expect(result).toContain('=== TASK (DO THIS) ===');
		expect(result).toContain('Reveal the structure');
	});

	it('includes SUBJECT section with provided text', () => {
		const result = renderPrompt(grammar, {}, 'my subject text', '');
		expect(result).toContain('=== SUBJECT (CONTEXT) ===');
		expect(result).toContain('my subject text');
	});

	it('uses placeholder when subject is empty', () => {
		const result = renderPrompt(grammar, {}, '', '');
		expect(result).toContain('(none provided)');
	});

	it('includes ADDENDUM section when provided', () => {
		const result = renderPrompt(grammar, {}, 'subject', 'Focus on security');
		expect(result).toContain('=== ADDENDUM (CLARIFICATION) ===');
		expect(result).toContain('Focus on security');
	});

	it('omits ADDENDUM section when empty', () => {
		const result = renderPrompt(grammar, {}, 'subject', '');
		expect(result).not.toContain('=== ADDENDUM');
	});

	it('includes constraint tokens with their descriptions', () => {
		const result = renderPrompt(grammar, { completeness: ['full'], scope: ['mean'] }, 'x', '');
		expect(result).toContain('Completeness ("full"): Comprehensive coverage');
		expect(result).toContain('Scope ("mean"): Core meaning');
	});

	it('shows (none) in constraints when no tokens selected', () => {
		const result = renderPrompt(grammar, {}, 'x', '');
		expect(result).toMatch(/=== CONSTRAINTS.*\n\(none\)/s);
	});

	it('includes PERSONA section with preset values', () => {
		const result = renderPrompt(grammar, {}, 'x', '', {
			preset: 'designer',
			voice: '',
			audience: '',
			tone: ''
		});
		expect(result).toContain('=== PERSONA (STANCE) ===');
		expect(result).toContain('Voice: Design practitioner');
		expect(result).toContain('Audience: Product team');
	});

	it('uses custom persona fields when no preset', () => {
		const result = renderPrompt(grammar, {}, 'x', '', {
			preset: '',
			voice: 'custom voice',
			audience: 'engineers',
			tone: 'direct'
		});
		expect(result).toContain('Voice: custom voice');
		expect(result).toContain('Audience: engineers');
	});

	it('includes REFERENCE KEY section', () => {
		const result = renderPrompt(grammar, {}, 'x', '');
		expect(result).toContain('=== REFERENCE KEY ===');
		expect(result).toContain('TASK: The primary action to perform');
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
});
