import { renderPrompt } from './renderPrompt.js';
import type { Grammar, Sequence, SequenceStep } from './grammar.js';

export function buildCopyPrompt(seq: Sequence, subject: string, grammar: Grammar, key: string): string {
	const steps = seq.steps;
	const total = steps.length;
	const parts: string[] = [];

	for (let i = 0; i < steps.length; i++) {
		const step = steps[i];
		const header = i === 0
			? `Step ${i + 1} of ${total} — ${step.role} (sequence: ${key}):`
			: `Step ${i + 1} of ${total} — ${step.role}:`;

		if (step.type === 'action') {
			parts.push(`${header}\n\nThis step is my turn to act: ${step.prompt_hint ?? step.role}\n\nPlease stop here and wait for my reply before continuing.`);
		} else if (step.type === 'dispatch') {
			parts.push(`${header}\n\n${buildDispatchBlock(step, grammar, subject, key)}`);
		} else {
			const axisMap: Record<string, string[]> = {};
			for (const pair of (step.token ?? '').split(' ')) {
				const colonIdx = pair.indexOf(':');
				if (colonIdx === -1) continue;
				const axis = pair.slice(0, colonIdx);
				const value = pair.slice(colonIdx + 1);
				if (!axis || !value) continue;
				if (!axisMap[axis]) axisMap[axis] = [];
				axisMap[axis].push(value);
			}
			const rendered = renderPrompt(grammar, axisMap, subject, step.prompt_hint ?? '');
			const terminal = step.requires_user_input ? '\n\nPlease stop here and wait for my reply before continuing.' : '';
			const chain = i === 0 ? '' : 'Your subject for this step is the full output of the previous step.\n\n';
			parts.push(`${header}\n\n${chain}${rendered}${terminal}`);
		}
	}

	const hasPause = steps.some(s => s.requires_user_input || s.type === 'action' || (s.type === 'dispatch' && !!s.during_dispatch));
	const preamble = hasPause
		? `Please work through these steps in order. When a step asks me to reply before continuing, stop there and wait for my reply — don't move on to the next step until I've answered.\n\n`
		: `Please work through all ${steps.length} steps in order, moving on to the next step as soon as you finish one.\n\n`;

	return preamble + parts.join('\n\n---\n\n');
}

function buildDispatchBlock(step: SequenceStep, grammar: Grammar, subject: string, sequenceKey: string): string {
	const lines: string[] = [];

	if (step.prompt_hint) {
		lines.push(step.prompt_hint);
		lines.push('');
	}

	lines.push(`For this step of my ${sequenceKey} sequence, I'd like you to coordinate several agents working in parallel.`);
	lines.push('');
	lines.push('This step fans work out to parallel agents.');

	const fanOutDesc = step.fan_out === 'enumerate'
		? 'enumerate — treat the prior step\'s output as a list; send one item per agent'
		: step.fan_out === 'replicate'
		? 'replicate — send the full prior output to every agent unchanged'
		: (step.fan_out ?? 'enumerate');
	lines.push(`fan_out: ${fanOutDesc}`);

	if (step.isolation) {
		const isolationCtx = step.inner
			? 'its assigned item, the inner steps below, and the inner stop_when — no shared context from other agents'
			: 'its assigned item and prompt_hint — no shared context from other agents';
		lines.push(`isolation: true — each agent receives only ${isolationCtx}`);
	} else {
		lines.push('isolation: false — agents share conversation context');
	}
	lines.push('');

	lines.push('Before spawning agents, please write a ## Agent Configuration block containing:');
	lines.push('1. The literal string `subagent_type: general-purpose`');
	lines.push(`2. The sequence context: "You are one of several agents I've dispatched in my ${sequenceKey} sequence."`);
	lines.push('3. The assigned item — verbatim text of the item this agent is processing from the enumerated list');
	lines.push('4. Factual statements about the task domain traceable to your prior output');
	lines.push('Please keep every sentence in that block to one of these four categories — leave out persona, behavioral stance, reasoning style, and approach.');
	lines.push('');

	if (step.during_dispatch) {
		lines.push(`Please start with a line like \`Dispatching N agents:\`, where N is the number of items in the prior step's list. Then spawn one Agent tool call per item — all in this same response turn — with run_in_background: true, so there's one agent per item. Once the agents are running, go straight into the during-dispatch task below in this same turn rather than deferring it.`);
	} else {
		lines.push(`Please start with a line like \`Dispatching N agents:\`, where N is the number of items in the prior step's list. Then spawn one Agent tool call per item — all in this same response turn — with run_in_background: true, so there's one agent per item. Wait until every agent has returned a result before moving on to the join step.`);
	}
	lines.push('');

	if (step.inner) {
		const inner = step.inner;
		lines.push(`inner mode: ${inner.mode}`);
		if (inner.stop_when) {
			lines.push(`inner stop_when: ${inner.stop_when}`);
		}
		lines.push('');

		if (inner.mode === 'cycle') {
			lines.push('Each agent works through the following cycle, repeating until stop_when is met:');
			lines.push('');
			for (let ci = 0; ci < inner.steps.length; ci++) {
				const is = inner.steps[ci];
				if (is.type === 'action') {
					lines.push(`Step ${ci + 1} — ${is.role}: Please carry out the actions named in the prior step's output using the available tools, and record the results before moving on. This step is done once you've actually run the subject and have a tool result to show for it — reading files alone isn't enough here.`);
				} else {
					const rendered = renderPrompt(grammar, parseTokenString(is.token ?? ''), subject, is.prompt_hint ?? '');
					lines.push(`Step ${ci + 1} — ${is.role}:`);
					lines.push(rendered);
				}
			}
			lines.push(`Step ${inner.steps.length + 1} — check stop_when: ${inner.stop_when ?? 'evaluate stop condition'}. If not met, begin a new cycle from step 1.`);
		} else {
			lines.push('Each agent executes the following steps:');
			lines.push('');
			for (let ci = 0; ci < inner.steps.length; ci++) {
				const is = inner.steps[ci];
				if (is.type === 'action') {
					lines.push(`Step ${ci + 1} — ${is.role}: Execute the actions named in the prior step's output using available tools. Record results before proceeding.`);
				} else {
					const rendered = renderPrompt(grammar, parseTokenString(is.token ?? ''), subject, is.prompt_hint ?? '');
					lines.push(`Step ${ci + 1} — ${is.role}:`);
					lines.push(rendered);
				}
			}
		}
		lines.push('');
	} else {
		lines.push(`Each agent receives the step prompt_hint as its task instruction: ${step.prompt_hint ?? ''}`);
		lines.push('');
	}

	const joinDesc = step.join === 'all'
		? 'all — wait for every agent; fail if any fail'
		: step.join === 'first'
		? 'first — take the first successful result; remaining agents may still complete. In each agent\'s prompt, please include two things: (a) ask it to return its finding as soon as it has confirmed the result, and (b) let it know its result will be used as the join answer if it confirms first.'
		: step.join === 'merge'
		? 'merge — collect all results into an array'
		: (step.join ?? 'all');
	lines.push(`join: ${joinDesc}`);
	lines.push('');

	lines.push('Please ask each agent to return a ## Derivation block naming: tokens applied, governing goal, behavioral dimensions. Gather these so the join result carries one ## Derivation block per agent, verbatim as returned — one per agent.');
	lines.push('');
	lines.push('Once all the agents are done, please reproduce each ## Derivation block verbatim in your output before moving on — again, one per agent.');

	if (step.during_dispatch) {
		lines.push('');
		lines.push('## During-dispatch task (run concurrently while agents execute):');
		const rendered = renderPrompt(grammar, parseTokenString(step.during_dispatch), subject, '');
		lines.push(rendered);
	}

	return lines.join('\n');
}

function parseTokenString(token: string): Record<string, string[]> {
	const axisMap: Record<string, string[]> = {};
	for (const pair of token.split(' ')) {
		const colonIdx = pair.indexOf(':');
		if (colonIdx === -1) continue;
		const axis = pair.slice(0, colonIdx);
		const value = pair.slice(colonIdx + 1);
		if (!axis || !value) continue;
		if (!axisMap[axis]) axisMap[axis] = [];
		axisMap[axis].push(value);
	}
	return axisMap;
}
