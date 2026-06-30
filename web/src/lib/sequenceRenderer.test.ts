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

const dispatchSeq: Sequence = {
	description: 'Dispatch sequence',
	mode: 'autonomous',
	steps: [
		{ token: 'task:probe', role: 'Frame enumeration', prompt_hint: 'Enumerate frames.' },
		{
			type: 'dispatch',
			role: 'parallel frame investigation',
			prompt_hint: 'Each agent investigates its frame.',
			fan_out: 'enumerate',
			join: 'first',
			isolation: true,
			inner: {
				mode: 'cycle',
				stop_when: "The vet output contains the literal string 'Root cause: confirmed'",
				steps: [
					{ token: 'make form:prep', role: 'hypothesis framing', prompt_hint: 'Frame a hypothesis.' },
					{ token: 'check form:vet', role: 'evidence evaluation', prompt_hint: 'Evaluate evidence.' }
				]
			}
		}
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

	it('requires sequence name in ## Agent Configuration block spec', () => {
		const result = buildCopyPrompt(dispatchSeq, 'subject', stubGrammar, 'dispatch-seq');
		expect(result).toContain('dispatch-seq sequence');
		// The agent config block spec must name the sequence so isolated agents have provenance
		const agentConfigIdx = result.indexOf('## Agent Configuration');
		const seqNameAfterConfig = result.indexOf('dispatch-seq', agentConfigIdx);
		expect(seqNameAfterConfig).toBeGreaterThan(agentConfigIdx);
	});

	it('renders sequence key provenance in dispatch steps', () => {
		const result = buildCopyPrompt(dispatchSeq, 'subject', stubGrammar, 'dispatch-seq');
		expect(result).toContain('dispatch step of the dispatch-seq sequence');
	});

	it('renders [DISPATCH GATE] for dispatch steps', () => {
		const result = buildCopyPrompt(dispatchSeq, 'subject', stubGrammar, 'dispatch-seq');
		expect(result).toContain('[DISPATCH GATE]');
	});

	it('renders fan_out value for dispatch steps', () => {
		const result = buildCopyPrompt(dispatchSeq, 'subject', stubGrammar, 'dispatch-seq');
		expect(result).toContain('fan_out: enumerate');
	});

	it('renders join value for dispatch steps', () => {
		const result = buildCopyPrompt(dispatchSeq, 'subject', stubGrammar, 'dispatch-seq');
		expect(result).toContain('join: first');
	});

	it('renders isolation text for dispatch steps', () => {
		const result = buildCopyPrompt(dispatchSeq, 'subject', stubGrammar, 'dispatch-seq');
		expect(result).toContain('isolation: true');
	});

	it('renders inner stop_when literal for dispatch steps', () => {
		const result = buildCopyPrompt(dispatchSeq, 'subject', stubGrammar, 'dispatch-seq');
		expect(result).toContain("The vet output contains the literal string 'Root cause: confirmed'");
	});

	it('renders inner step prompt_hint via renderPrompt for dispatch steps', () => {
		const result = buildCopyPrompt(dispatchSeq, 'subject', stubGrammar, 'dispatch-seq');
		expect(result).toContain('Frame a hypothesis.');
	});

	it('renders ## Agent Configuration criteria inline for dispatch steps', () => {
		const result = buildCopyPrompt(dispatchSeq, 'subject', stubGrammar, 'dispatch-seq');
		expect(result).toContain('## Agent Configuration');
		expect(result).toContain('subagent_type: general-purpose');
	});

	it('renders ## Derivation count-verification clause for dispatch steps', () => {
		const result = buildCopyPrompt(dispatchSeq, 'subject', stubGrammar, 'dispatch-seq');
		expect(result).toContain('## Derivation');
		expect(result).toContain('count equals the number of agents');
	});

	it('dispatch step without during_dispatch does not trigger pause preamble', () => {
		const result = buildCopyPrompt(dispatchSeq, 'subject', stubGrammar, 'dispatch-seq');
		expect(result).toContain('You must complete all 2 steps in sequence');
		expect(result).not.toContain('your response must end there');
	});

	it('dispatch step with during_dispatch triggers pause preamble', () => {
		const dispatchWithDuring: Sequence = {
			description: 'Dispatch with during',
			mode: 'autonomous',
			steps: [
				{ token: 'task:probe', role: 'Frame enumeration', prompt_hint: 'Enumerate frames.' },
				{
					type: 'dispatch',
					role: 'parallel investigation',
					fan_out: 'enumerate',
					join: 'all',
					during_dispatch: 'show form:quiz'
				}
			]
		};
		const result = buildCopyPrompt(dispatchWithDuring, 'subject', stubGrammar, 'dd-seq');
		expect(result).toContain('your response must end there');
	});

	it('renders ## During-dispatch task section when during_dispatch is set', () => {
		const dispatchWithDuring: Sequence = {
			description: 'Dispatch with during',
			mode: 'autonomous',
			steps: [
				{ token: 'task:probe', role: 'Frame enumeration', prompt_hint: 'Enumerate frames.' },
				{
					type: 'dispatch',
					role: 'parallel investigation',
					fan_out: 'enumerate',
					join: 'all',
					during_dispatch: 'show form:quiz'
				}
			]
		};
		const result = buildCopyPrompt(dispatchWithDuring, 'subject', stubGrammar, 'dd-seq');
		expect(result).toContain('## During-dispatch task');
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
