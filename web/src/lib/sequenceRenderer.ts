import { renderPrompt } from './renderPrompt.js';
import type { Grammar, Sequence } from './grammar.js';

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

	const hasPause = steps.some(s => s.requires_user_input || s.type === 'action');
	const preamble = hasPause
		? `Work through each step in sequence. When a step ends with "--- AWAITING INPUT ---", your response must end there. Do not continue to the next step until the user replies.\n\n`
		: `You must complete all ${steps.length} steps in sequence within this response. After completing each step, proceed immediately to the next.\n\n`;

	return preamble + parts.join('\n\n---\n\n');
}
