/**
 * Sequences mode: top-level mode switcher renders a sequences panel
 * instead of the axis tab bar when activeMode === 'sequences'.
 */
import { flushSync } from 'svelte';
import { mount } from 'svelte';
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest';

const mockLocalStorage = {
	getItem: vi.fn(() => null),
	setItem: vi.fn(),
	removeItem: vi.fn(),
	clear: vi.fn()
};

Object.defineProperty(globalThis, 'localStorage', {
	value: mockLocalStorage,
	writable: true
});

const MOCK_SEQUENCES = {
	'debug-cycle': {
		description: 'Iterative debugging loop.',
		mode: 'linear',
		steps: [
			{ token: 'probe method:hollow', role: 'diagnosis', prompt_hint: 'Find root cause.', requires_user_input: true },
			{ token: 'fix method:atomic', role: 'repair', prompt_hint: 'Apply minimal fix.' }
		]
	},
	'frame-explore': {
		description: 'Explore a problem from multiple frames.',
		mode: 'interactive',
		steps: [
			{ token: 'make method:prism', role: 'framing', prompt_hint: 'Enumerate frames.' }
		]
	}
};

vi.mock('$lib/grammar.js', () => ({
	loadGrammar: vi.fn().mockResolvedValue({
		sequences: MOCK_SEQUENCES,
		hierarchy: { axis_soft_caps: {} },
		tokens: {},
		persona_presets: [],
		persona: { use_when: {} },
		reference_key: { task: '', addendum: '', constraints: '', constraints_axes: {}, persona: '', subject: '' },
		execution_reminder: '',
		planning_directive: '',
		meta_interpretation_guidance: ''
	}),
	getAxisTokens: vi.fn().mockReturnValue([]),
	getTaskTokens: vi.fn().mockReturnValue([
		{ token: 'show', label: 'Explain', description: 'Explain or describe', guidance: '', use_when: '' }
	]),
	getPersonaPresets: vi.fn().mockReturnValue([]),
	getPersonaAxisTokens: vi.fn().mockReturnValue([]),
	getPersonaIntentTokens: vi.fn().mockReturnValue([]),
	getPersonaAxisTokensMeta: vi.fn().mockReturnValue([]),
	getPresetHint: vi.fn().mockReturnValue(''),
	personaTokenHint: vi.fn().mockReturnValue(''),
	personaTokenDistinctionText: vi.fn().mockReturnValue(''),
	AXES: ['topology', 'completeness', 'scope', 'method', 'form', 'channel', 'directional'],
	toPersonaSlug: vi.fn().mockReturnValue(''),
	toAxisTokenSlug: vi.fn().mockReturnValue(''),
	buildCommandTokens: vi.fn().mockReturnValue([]),
	getUsagePatterns: vi.fn().mockReturnValue([]),
	getStarterPacks: vi.fn().mockReturnValue([]),
	getCompositionData: vi.fn().mockReturnValue(null),
	getChipState: vi.fn().mockReturnValue(null),
	getReverseChipState: vi.fn().mockReturnValue(null),
	getChipStateWithReason: vi.fn().mockReturnValue({ state: null, naturalWith: [], cautionWith: [] }),
	getSequences: vi.fn().mockReturnValue(
		Object.entries(MOCK_SEQUENCES).map(([key, seq]) => ({ key, ...seq }))
	)
}));

vi.mock('$lib/incompatibilities.js', () => ({
	findConflicts: vi.fn().mockReturnValue([])
}));

vi.mock('$lib/renderPrompt.js', () => ({
	renderPrompt: vi.fn().mockReturnValue('MOCK RENDERED PROMPT')
}));

describe('Page — Sequences mode', () => {
	let container: HTMLDivElement;

	beforeEach(() => {
		vi.clearAllMocks();
		mockLocalStorage.getItem.mockReturnValue(null);
		container = document.createElement('div');
		document.body.appendChild(container);
	});

	afterEach(() => {
		document.body.removeChild(container);
	});

	it('Sequences mode button exists in the page', async () => {
		const { default: Page } = await import('../routes/+page.svelte');
		mount(Page, { target: container });
		await new Promise(r => setTimeout(r, 100));
		flushSync();

		const btn = Array.from(container.querySelectorAll('button')).find(
			b => b.textContent?.trim() === 'Sequences'
		);
		expect(btn).toBeTruthy();
	});

	it('axis tab bar is hidden when Sequences mode is active', async () => {
		const { default: Page } = await import('../routes/+page.svelte');
		mount(Page, { target: container });
		await new Promise(r => setTimeout(r, 100));
		flushSync();

		const btn = Array.from(container.querySelectorAll('button')).find(
			b => b.textContent?.trim() === 'Sequences'
		) as HTMLElement;
		btn.click();
		flushSync();

		const tabBar = container.querySelector('[role="tablist"]');
		expect(tabBar).toBeFalsy();
	});

	it('sequences panel shows sequence names when Sequences mode is active', async () => {
		const { default: Page } = await import('../routes/+page.svelte');
		mount(Page, { target: container });
		await new Promise(r => setTimeout(r, 100));
		flushSync();

		const btn = Array.from(container.querySelectorAll('button')).find(
			b => b.textContent?.trim() === 'Sequences'
		) as HTMLElement;
		btn.click();
		flushSync();

		const text = container.textContent ?? '';
		expect(text).toContain('debug-cycle');
		expect(text).toContain('frame-explore');
	});

	it('sequences panel shows sequence descriptions', async () => {
		const { default: Page } = await import('../routes/+page.svelte');
		mount(Page, { target: container });
		await new Promise(r => setTimeout(r, 100));
		flushSync();

		const btn = Array.from(container.querySelectorAll('button')).find(
			b => b.textContent?.trim() === 'Sequences'
		) as HTMLElement;
		btn.click();
		flushSync();

		const text = container.textContent ?? '';
		expect(text).toContain('Iterative debugging loop.');
	});

	it('build panel (div.main) is hidden when Sequences mode is active', async () => {
		const { default: Page } = await import('../routes/+page.svelte');
		mount(Page, { target: container });
		await new Promise(r => setTimeout(r, 100));
		flushSync();

		const btn = Array.from(container.querySelectorAll('button')).find(
			b => b.textContent?.trim() === 'Sequences'
		) as HTMLElement;
		btn.click();
		flushSync();

		const main = container.querySelector('.main');
		expect(main).toBeFalsy();
	});

	it('linear sequence shows pause indicator between steps requiring user input', async () => {
		const { default: Page } = await import('../routes/+page.svelte');
		mount(Page, { target: container });
		await new Promise(r => setTimeout(r, 100));
		flushSync();

		const seqBtn = Array.from(container.querySelectorAll('button')).find(
			b => b.textContent?.trim() === 'Sequences'
		) as HTMLElement;
		seqBtn.click();
		flushSync();

		const cardHeader = Array.from(container.querySelectorAll('.seq-card-header')).find(
			el => el.textContent?.includes('debug-cycle')
		) as HTMLElement;
		cardHeader.click();
		flushSync();

		const text = container.textContent ?? '';
		expect(text).toContain('⏸');
	});

	it('copied prompt injects AWAITING INPUT terminal string after requires_user_input steps', async () => {
		const { default: Page } = await import('../routes/+page.svelte');
		mount(Page, { target: container });
		await new Promise(r => setTimeout(r, 100));
		flushSync();

		const seqBtn = Array.from(container.querySelectorAll('button')).find(
			b => b.textContent?.trim() === 'Sequences'
		) as HTMLElement;
		seqBtn.click();
		flushSync();

		const cardHeader = Array.from(container.querySelectorAll('.seq-card-header')).find(
			el => el.textContent?.includes('debug-cycle')
		) as HTMLElement;
		cardHeader.click();
		flushSync();

		const copyBtn = Array.from(container.querySelectorAll('.seq-copy-btn')).find(
			el => el.textContent?.includes('Copy as Prompt')
		) as HTMLElement;
		copyBtn.click();
		await new Promise(r => setTimeout(r, 50));
		flushSync();

		const textarea = container.querySelector('.seq-modal-textarea') as HTMLTextAreaElement;
		expect(textarea).toBeTruthy();
		expect(textarea.value).toContain('--- AWAITING INPUT ---');
	});

	it('copied prompt with requires_user_input steps instructs LLM to pause for input', async () => {
		const { default: Page } = await import('../routes/+page.svelte');
		mount(Page, { target: container });
		await new Promise(r => setTimeout(r, 100));
		flushSync();

		const seqBtn = Array.from(container.querySelectorAll('button')).find(
			b => b.textContent?.trim() === 'Sequences'
		) as HTMLElement;
		seqBtn.click();
		flushSync();

		const cardHeader = Array.from(container.querySelectorAll('.seq-card-header')).find(
			el => el.textContent?.includes('debug-cycle')
		) as HTMLElement;
		cardHeader.click();
		flushSync();

		const copyBtn = Array.from(container.querySelectorAll('.seq-copy-btn')).find(
			el => el.textContent?.includes('Copy as Prompt')
		) as HTMLElement;
		copyBtn.click();
		await new Promise(r => setTimeout(r, 50));
		flushSync();

		const textarea = container.querySelector('.seq-modal-textarea') as HTMLTextAreaElement;
		expect(textarea).toBeTruthy();
		// pause-mode preamble: instructs stop-and-wait, not complete-all
		expect(textarea.value).toContain('--- AWAITING INPUT ---');
		expect(textarea.value).not.toContain('complete all');
	});

	it('copied prompt with no pause steps instructs LLM to complete all steps', async () => {
		const { default: Page } = await import('../routes/+page.svelte');
		mount(Page, { target: container });
		await new Promise(r => setTimeout(r, 100));
		flushSync();

		const seqBtn = Array.from(container.querySelectorAll('button')).find(
			b => b.textContent?.trim() === 'Sequences'
		) as HTMLElement;
		seqBtn.click();
		flushSync();

		const cardHeader = Array.from(container.querySelectorAll('.seq-card-header')).find(
			el => el.textContent?.includes('frame-explore')
		) as HTMLElement;
		cardHeader.click();
		flushSync();

		const copyBtn = Array.from(container.querySelectorAll('.seq-copy-btn')).find(
			el => el.textContent?.includes('Copy as Prompt')
		) as HTMLElement;
		copyBtn.click();
		await new Promise(r => setTimeout(r, 50));
		flushSync();

		const textarea = container.querySelector('.seq-modal-textarea') as HTMLTextAreaElement;
		expect(textarea).toBeTruthy();
		expect(textarea.value).toContain('complete all');
		expect(textarea.value).not.toContain('stop and wait');
	});

	it('top-level subject input is hidden when Sequences mode is active', async () => {
		const { default: Page } = await import('../routes/+page.svelte');
		mount(Page, { target: container });
		await new Promise(r => setTimeout(r, 100));
		flushSync();

		const btn = Array.from(container.querySelectorAll('button')).find(
			b => b.textContent?.trim() === 'Sequences'
		) as HTMLElement;
		btn.click();
		flushSync();

		const subjectLabel = container.querySelector('.subject-top');
		expect(subjectLabel).toBeFalsy();
	});

	it('pause indicator in copied prompt says to provide user input', async () => {
		const { default: Page } = await import('../routes/+page.svelte');
		mount(Page, { target: container });
		await new Promise(r => setTimeout(r, 100));
		flushSync();

		const seqBtn = Array.from(container.querySelectorAll('button')).find(
			b => b.textContent?.trim() === 'Sequences'
		) as HTMLElement;
		seqBtn.click();
		flushSync();

		const cardHeader = Array.from(container.querySelectorAll('.seq-card-header')).find(
			el => el.textContent?.includes('debug-cycle')
		) as HTMLElement;
		cardHeader.click();
		flushSync();

		const text = container.textContent ?? '';
		expect(text).toContain('Provide your input');
	});

	it('review panel (selected token chips) is hidden when Sequences mode is active', async () => {
		const { default: Page } = await import('../routes/+page.svelte');
		mount(Page, { target: container });
		await new Promise(r => setTimeout(r, 100));
		flushSync();

		const btn = Array.from(container.querySelectorAll('button')).find(
			b => b.textContent?.trim() === 'Sequences'
		) as HTMLElement;
		btn.click();
		flushSync();

		const reviewPanel = container.querySelector('.review-panel');
		expect(reviewPanel).toBeFalsy();
	});

	it('Build Prompt button returns to build mode and shows axis tab bar', async () => {
		const { default: Page } = await import('../routes/+page.svelte');
		mount(Page, { target: container });
		await new Promise(r => setTimeout(r, 100));
		flushSync();

		const seqBtn = Array.from(container.querySelectorAll('button')).find(
			b => b.textContent?.trim() === 'Sequences'
		) as HTMLElement;
		seqBtn.click();
		flushSync();

		const buildBtn = Array.from(container.querySelectorAll('button')).find(
			b => b.textContent?.trim() === 'Build Prompt'
		) as HTMLElement;
		expect(buildBtn).toBeTruthy();
		buildBtn.click();
		flushSync();

		const tabBar = container.querySelector('[role="tablist"]');
		expect(tabBar).toBeTruthy();
	});
});
