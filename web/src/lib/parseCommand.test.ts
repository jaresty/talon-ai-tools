import { describe, it, expect } from 'vitest';
import { parseCommand } from './parseCommand.js';
import type { Grammar } from './grammar.js';

const grammar: Grammar = {
	axes: {
		definitions: {
			completeness: { full: 'Comprehensive coverage.', lean: 'Concise coverage.' },
			scope: { mean: 'Core meaning.', sys: 'System level.' },
			method: { flow: 'Flow analysis.' },
			form: { prose: 'Flowing narrative.', wardley: 'Wardley map.' },
			channel: { plain: 'Plain prose, no markdown.', slack: 'Slack-formatted.' },
			directional: { fwd: 'Forward-looking.' }
		},
		labels: { completeness: {}, scope: {}, method: {}, form: {}, channel: {}, directional: {} },
		guidance: { completeness: {}, scope: {}, method: {}, form: {}, channel: {}, directional: {} },
		use_when: { completeness: {}, scope: {}, method: {}, form: {}, channel: {}, directional: {} }
	},
	tasks: {
		descriptions: {
			show: 'Reveal the structure.',
			make: 'Produce an artifact.',
			plan: 'Create a plan.'
		},
		labels: {},
		guidance: {}
	},
	hierarchy: {
		axis_priority: [],
		axis_soft_caps: {},
		axis_incompatibilities: {}
	},
	persona: {
		presets: {},
		axes: { voice: [], audience: [], tone: [] }
	}
};

describe('parseCommand — D1 falsifiable', () => {
	it('parses basic command: show mean full plain', () => {
		const result = parseCommand('bar build show mean full plain', grammar);
		expect(result.selected.task).toEqual(['show']);
		expect(result.selected.scope).toEqual(['mean']);
		expect(result.selected.completeness).toEqual(['full']);
		expect(result.selected.channel).toEqual(['plain']);
		expect(result.selected.form).toEqual([]);
		expect(result.selected.method).toEqual([]);
		expect(result.unrecognized).toEqual([]);
	});
});

describe('parseCommand', () => {
	it('strips "bar build" prefix', () => {
		const result = parseCommand('bar build show', grammar);
		expect(result.selected.task).toEqual(['show']);
	});

	it('strips "build" prefix without "bar"', () => {
		const result = parseCommand('build show', grammar);
		expect(result.selected.task).toEqual(['show']);
	});

	it('handles command without prefix', () => {
		const result = parseCommand('show mean', grammar);
		expect(result.selected.task).toEqual(['show']);
		expect(result.selected.scope).toEqual(['mean']);
	});

	it('extracts --subject flag value', () => {
		const result = parseCommand('bar build show --subject "hello world"', grammar);
		expect(result.subject).toBe('hello world');
		expect(result.selected.task).toEqual(['show']);
	});

	it('extracts --addendum flag value', () => {
		const result = parseCommand('bar build show --addendum "focus on errors"', grammar);
		expect(result.addendum).toBe('focus on errors');
	});

	it('extracts both --subject and --addendum', () => {
		const result = parseCommand(
			'bar build show mean --subject "my text" --addendum "focus on X"',
			grammar
		);
		expect(result.subject).toBe('my text');
		expect(result.addendum).toBe('focus on X');
	});

	it('handles escaped quotes in flag values', () => {
		const result = parseCommand('bar build show --subject "say \\"hello\\""', grammar);
		expect(result.subject).toBe('say "hello"');
	});

	it('classifies form tokens correctly', () => {
		const result = parseCommand('bar build show wardley', grammar);
		expect(result.selected.form).toEqual(['wardley']);
	});

	it('classifies method tokens correctly', () => {
		const result = parseCommand('bar build show flow', grammar);
		expect(result.selected.method).toEqual(['flow']);
	});

	it('classifies directional tokens correctly', () => {
		const result = parseCommand('bar build show fwd', grammar);
		expect(result.selected.directional).toEqual(['fwd']);
	});

	it('collects unrecognized tokens', () => {
		const result = parseCommand('bar build show unknown-token xyz', grammar);
		expect(result.selected.task).toEqual(['show']);
		expect(result.unrecognized).toContain('unknown-token');
		expect(result.unrecognized).toContain('xyz');
	});

	it('parses persona=preset token', () => {
		const result = parseCommand('bar build persona=designer show', grammar);
		expect(result.persona.preset).toBe('designer');
		expect(result.selected.task).toEqual(['show']);
	});

	it('parses voice=value persona token', () => {
		const result = parseCommand('bar build voice=as-developer show', grammar);
		expect(result.persona.voice).toBe('as-developer');
		expect(result.persona.preset).toBe('');
	});

	it('parses audience=value persona token', () => {
		const result = parseCommand('bar build audience=engineers show', grammar);
		expect(result.persona.audience).toBe('engineers');
	});

	it('parses tone=value persona token', () => {
		const result = parseCommand('bar build tone=direct show', grammar);
		expect(result.persona.tone).toBe('direct');
	});

	it('parses intent=value persona token', () => {
		const result = parseCommand('bar build intent=persuade show', grammar);
		expect(result.persona.intent).toBe('persuade');
		expect(result.persona.preset).toBe('');
	});

	it('intent= coexists with persona=preset (orthogonal dimensions)', () => {
		const result = parseCommand('bar build persona=designer intent=inform', grammar);
		expect(result.persona.preset).toBe('designer');
		expect(result.persona.intent).toBe('inform');
	});

	it('clears preset when custom persona key is given', () => {
		const result = parseCommand('bar build voice=developer', grammar);
		expect(result.persona.preset).toBe('');
		expect(result.persona.voice).toBe('developer');
	});

	it('handles empty command', () => {
		const result = parseCommand('bar build', grammar);
		expect(result.selected.task).toEqual([]);
		expect(result.unrecognized).toEqual([]);
	});

	it('does not duplicate tokens if repeated', () => {
		const result = parseCommand('bar build show show', grammar);
		expect(result.selected.task).toEqual(['show']);
	});

	it('handles multiple scope tokens', () => {
		const result = parseCommand('bar build show mean sys', grammar);
		expect(result.selected.scope).toEqual(['mean', 'sys']);
	});
});
