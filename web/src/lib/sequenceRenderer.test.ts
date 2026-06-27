import { describe, it, expect, vi } from 'vitest';
import { buildCopyPrompt } from './sequenceRenderer.js';
import type { Grammar } from './grammar.js';
import type { Sequence } from './grammar.js';

vi.mock('./renderPrompt.js', () => ({
	renderPrompt: (_grammar: unknown, axisMap: Record<string, string[]>, subject: string, hint: string) =>
		`[rendered:${Object.keys(axisMap).join(',')}:${subject}:${hint}]`
}));

const stubGrammar = {} as unknown as Grammar;

const nonPauseSeq: Sequence = {
	description: 'Test sequence',
	mode: 'auto',
	steps: [
		{ token: 'task:probe', role: 'Probe step', prompt_hint: 'probe hint' },
		{ token: 'task:fix', role: 'Fix step', prompt_hint: 'fix hint' }
	]
};

const pauseSeq: Sequence = {
	description: 'Pause sequence',
	mode: 'interactive',
	steps: [
		{ token: 'task:probe', role: 'Probe step', requires_user_input: true },
		{ token: 'task:fix', role: 'Fix step' }
	]
};

const actionSeq: Sequence = {
	description: 'Action sequence',
	mode: 'interactive',
	steps: [
		{ type: 'action', role: 'Your action', prompt_hint: 'Do the thing' },
		{ token: 'task:fix', role: 'Fix step' }
	]
};

describe('buildCopyPrompt', () => {
	it('assembles parts for a non-pause sequence', () => {
		const result = buildCopyPrompt(nonPauseSeq, 'my subject', stubGrammar, 'my-seq');
		expect(result).toContain('=== SEQUENCE: my-seq');
		expect(result).toContain('Step 1/2');
		expect(result).toContain('Step 2/2');
		expect(result).toContain('You must complete all 2 steps in sequence');
	});

	it('uses pause preamble when sequence has requires_user_input', () => {
		const result = buildCopyPrompt(pauseSeq, 'subject', stubGrammar, 'pause-seq');
		expect(result).toContain('AWAITING INPUT');
		expect(result).toContain('your response must end there');
	});

	it('renders action steps with YOUR ACTION label', () => {
		const result = buildCopyPrompt(actionSeq, 'subject', stubGrammar, 'action-seq');
		expect(result).toContain('👤 YOUR ACTION');
		expect(result).toContain('Do the thing');
	});

	it('includes chain instruction for steps after the first', () => {
		const result = buildCopyPrompt(nonPauseSeq, 'subject', stubGrammar, 'my-seq');
		expect(result).toContain('Your subject for this step is the full output of the previous step');
	});

	it('does not include chain instruction for first step', () => {
		const result = buildCopyPrompt(nonPauseSeq, 'subject', stubGrammar, 'my-seq');
		const firstStepEnd = result.indexOf('Step 1/2');
		const secondStepStart = result.indexOf('Step 2/2');
		const firstPart = result.slice(firstStepEnd, secondStepStart);
		expect(firstPart).not.toContain('Your subject for this step');
	});
});
