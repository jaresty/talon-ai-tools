import { renderPrompt } from './renderPrompt.js';
import type { Grammar, Sequence, SequenceStep } from './grammar.js';

export function buildCopyPrompt(seq: Sequence, subject: string, grammar: Grammar, key: string): string {
	const steps = seq.steps;
	const total = steps.length;
	const parts: string[] = [];

	for (let i = 0; i < steps.length; i++) {
		const step = steps[i];
		const header = i === 0
			? `=== SEQUENCE: ${key} — Step ${i + 1}/${total}: ${step.role} ===`
			: `=== Step ${i + 1}/${total}: ${step.role} ===`;

		if (step.type === 'action') {
			parts.push(`${header}\n\n👤 YOUR ACTION: ${step.prompt_hint ?? step.role}\n\n--- AWAITING INPUT ---`);
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
			const terminal = step.requires_user_input ? '\n\n--- AWAITING INPUT ---' : '';
			const chain = i === 0 ? '' : 'Your subject for this step is the full output of the previous step.\n\n';
			parts.push(`${header}\n\n${chain}${rendered}${terminal}`);
		}
	}

	const hasPause = steps.some(s => s.requires_user_input || s.type === 'action' || (s.type === 'dispatch' && !!s.during_dispatch));
	const preamble = hasPause
		? `Work through each step in sequence. When a step ends with "--- AWAITING INPUT ---", your response must end there. Do not continue to the next step until the user replies.\n\n`
		: `You must complete all ${steps.length} steps in sequence within this response. After completing each step, proceed immediately to the next.\n\n`;

	return preamble + parts.join('\n\n---\n\n');
}

function buildDispatchBlock(step: SequenceStep, grammar: Grammar, subject: string, sequenceKey: string): string {
	const lines: string[] = [];

	if (step.prompt_hint) {
		lines.push(step.prompt_hint);
		lines.push('');
	}

	lines.push(`[dispatch protocol — required] This is the dispatch step of the ${sequenceKey} sequence — a structured parallel analysis workflow initiated by the user. You are the orchestrator.`);
	lines.push('');
	lines.push('This step fans out work to parallel agents.');

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

	lines.push('Before spawning agents, write a ## Agent Configuration block containing:');
	lines.push('1. The literal string `subagent_type: general-purpose`');
	lines.push(`2. The sequence context: "You are a dispatched agent in the ${sequenceKey} sequence — a structured parallel analysis workflow initiated by the user."`);
	lines.push('3. The assigned item — verbatim text of the item this agent is processing from the enumerated list');
	lines.push('4. Factual statements about the task domain traceable to the orchestrator\'s prior output');
	lines.push('A block is compliant only when every sentence in it can be matched to one of these four categories by an evaluator reading the transcript — persona, behavioral stance, reasoning style, and approach must not appear here; a sentence naming any of these makes the block non-compliant.');
	lines.push('');

	if (step.during_dispatch) {
		lines.push(`[DISPATCH GATE] Emit a line of the form \`Dispatching N agents:\` where N equals the count of items in the prior step's list. Spawn one Agent tool call per item — all in this same response turn — with run_in_background: true. The number of Agent tool calls must equal N. An evaluator determines required Agent call count by reading N from the first \`Dispatching N agents:\` line in the turn. After spawning all agents, immediately execute the during_dispatch task below in this same response turn — do not defer it.`);
	} else {
		lines.push(`[DISPATCH GATE] Emit a line of the form \`Dispatching N agents:\` where N equals the count of items in the prior step's list. Spawn one Agent tool call per item — all in this same response turn — with run_in_background: true. The number of Agent tool calls must equal N. An evaluator determines required Agent call count by reading N from the first \`Dispatching N agents:\` line in the turn. Do not proceed to the join step until every background agent has returned a result — an evaluator determines compliance by confirming that a result block for each Agent tool call spawned in this step appears in the transcript before join output.`);
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
					lines.push(`Step ${ci + 1} — ${is.role}: Execute the actions named in the prior step's output using available tools. Record results before proceeding. This step is complete only when a tool call result appears in the transcript showing output from executing the subject — a call that only reads files does not satisfy this requirement.`);
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
		? 'first — take the first successful result; remaining agents may still complete. Each agent prompt must contain: (a) an instruction to return the finding immediately upon confirming the result, and (b) a statement that its result will be taken as the join answer if it is first to confirm. An evaluator determines compliance by locating each agent prompt and checking whether both clauses are present as distinct sentences — a prompt containing neither clause does not satisfy this gate.'
		: step.join === 'merge'
		? 'merge — collect all results into an array'
		: (step.join ?? 'all');
	lines.push(`join: ${joinDesc}`);
	lines.push('');

	lines.push('Each agent must return a ## Derivation block naming: tokens applied, governing goal, behavioral dimensions. The join result must contain one ## Derivation block per agent, appearing verbatim as returned. An evaluator determines compliance by counting ## Derivation headings in the join result and confirming the count equals the number of agents — a join result containing fewer ## Derivation headings than agents does not satisfy this gate.');
	lines.push('');
	lines.push('After all agents complete, reproduce each ## Derivation block verbatim in your output. An evaluator determines compliance by counting ## Derivation headings before the next step\'s output and confirming the count equals the number of agents — a count mismatch does not satisfy this gate.');

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
