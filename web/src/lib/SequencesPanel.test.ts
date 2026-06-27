import { flushSync, mount } from 'svelte';
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest';

vi.mock('$lib/grammar.js', () => ({
	getSequences: vi.fn().mockReturnValue([
		{
			key: 'debug-cycle',
			description: 'Iterative debugging loop.',
			mode: 'linear',
			steps: [
				{ token: 'probe method:hollow', role: 'diagnosis', prompt_hint: 'Find root cause.', requires_user_input: true },
				{ token: 'fix method:atomic', role: 'repair', prompt_hint: 'Apply minimal fix.' }
			]
		},
		{
			key: 'frame-explore',
			description: 'Explore a problem from multiple frames.',
			mode: 'interactive',
			steps: [
				{ token: 'make method:prism', role: 'framing', prompt_hint: 'Enumerate frames.' }
			]
		},
		{
			key: 'experiment-cycle',
			description: 'Frame a hypothesis then run an experiment.',
			mode: 'cycle',
			steps: [
				{ token: 'make form:prep', role: 'pre-experiment framing', prompt_hint: 'State the hypothesis.' },
				{ type: 'action', role: 'experiment execution', prompt_hint: 'Run the experiment.', requires_user_input: true },
				{ token: 'check form:vet', role: 'post-experiment review', prompt_hint: 'Evaluate the evidence.' }
			]
		}
	])
}));

vi.mock('$lib/sequenceRenderer.js', () => ({
	buildCopyPrompt: vi.fn().mockReturnValue('MOCK PROMPT OUTPUT')
}));

describe('SequencesPanel', () => {
	let container: HTMLDivElement;

	beforeEach(() => {
		container = document.createElement('div');
		document.body.appendChild(container);
	});

	afterEach(() => {
		document.body.removeChild(container);
		vi.clearAllMocks();
	});

	async function mountPanel() {
		const { default: SequencesPanel } = await import('./SequencesPanel.svelte');
		mount(SequencesPanel, { target: container, props: { grammar: {} as any } });
		flushSync();
	}

	it('renders sequence names', async () => {
		await mountPanel();
		const text = container.textContent ?? '';
		expect(text).toContain('debug-cycle');
		expect(text).toContain('frame-explore');
	});

	it('renders sequence descriptions', async () => {
		await mountPanel();
		const text = container.textContent ?? '';
		expect(text).toContain('Iterative debugging loop.');
	});

	it('sequence steps are hidden before card is expanded', async () => {
		await mountPanel();
		expect(container.querySelector('.seq-steps')).toBeFalsy();
	});

	it('clicking a card header expands its steps', async () => {
		await mountPanel();
		const header = container.querySelector('.seq-card-header') as HTMLElement;
		header.click();
		flushSync();
		expect(container.querySelector('.seq-steps')).toBeTruthy();
	});

	it('shows pause indicator after a requires_user_input step', async () => {
		await mountPanel();
		const header = Array.from(container.querySelectorAll('.seq-card-header')).find(
			el => el.textContent?.includes('debug-cycle')
		) as HTMLElement;
		header.click();
		flushSync();
		expect(container.textContent).toContain('Provide your input');
	});

	it('shows user badge for action steps', async () => {
		await mountPanel();
		const header = Array.from(container.querySelectorAll('.seq-card-header')).find(
			el => el.textContent?.includes('experiment-cycle')
		) as HTMLElement;
		header.click();
		flushSync();
		expect(container.textContent).toContain('👤');
	});

	it('copy button calls buildCopyPrompt and shows modal on clipboard failure', async () => {
		await mountPanel();
		const header = container.querySelector('.seq-card-header') as HTMLElement;
		header.click();
		flushSync();

		const copyBtn = container.querySelector('.seq-copy-btn') as HTMLElement;
		copyBtn.click();
		await new Promise(r => setTimeout(r, 50));
		flushSync();

		const textarea = container.querySelector('.seq-modal-textarea') as HTMLTextAreaElement;
		expect(textarea).toBeTruthy();
		expect(textarea.value).toBe('MOCK PROMPT OUTPUT');
	});

	it('shows subject textarea for entering sequence subject', async () => {
		await mountPanel();
		expect(container.querySelector('.seq-subject-input')).toBeTruthy();
	});
});
