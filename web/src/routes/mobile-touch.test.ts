import { mount } from 'svelte';
import { vi, describe, it, expect, beforeEach } from 'vitest';

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

vi.mock('$lib/grammar.js', () => ({
	loadGrammar: vi.fn().mockResolvedValue({
		hierarchy: { axis_soft_caps: {} },
		tokens: {},
		persona_presets: []
	}),
	getAxisTokens: vi.fn().mockReturnValue([]),
	getTaskTokens: vi.fn().mockReturnValue([{ token: 'show', label: 'Explain' }]),
	getPersonaPresets: vi.fn().mockReturnValue([
		{ key: 'fun_mode', label: 'Fun Mode' }
	]),
	getPersonaAxisTokens: vi.fn().mockReturnValue(['casual', 'formal']),
	AXES: ['completeness', 'scope', 'method', 'form', 'channel', 'directional'],
	toPersonaSlug: vi.fn().mockReturnValue(''),
	getUsagePatterns: vi.fn().mockReturnValue([]),
	getStarterPacks: vi.fn().mockReturnValue([]),
	getCompositionData: vi.fn().mockReturnValue(null),
	getChipState: vi.fn().mockReturnValue(null),
		getReverseChipState: vi.fn().mockReturnValue(null)
}));

vi.mock('$lib/incompatibilities.js', () => ({
	findConflicts: vi.fn().mockReturnValue([])
}));

vi.mock('$lib/renderPrompt.js', () => ({
	renderPrompt: vi.fn().mockReturnValue('')
}));

describe('Page — Touch Targets and iOS Zoom', () => {
	let container: HTMLDivElement;

	beforeEach(() => {
		vi.clearAllMocks();
		container = document.createElement('div');
		document.body.appendChild(container);
	});

	it('tab buttons are <button> elements (not divs)', async () => {
		const { default: Page } = await import('../routes/+page.svelte');
		mount(Page, { target: container });

		await new Promise(r => setTimeout(r, 100));

		const tabs = container.querySelectorAll('.tab');
		expect(tabs.length).toBeGreaterThan(0);
		tabs.forEach((tab) => {
			expect(tab.tagName.toLowerCase()).toBe('button');
		});
	});

	it('load-cmd-toggle is a <button> element (not a div)', async () => {
		const { default: Page } = await import('../routes/+page.svelte');
		mount(Page, { target: container });

		await new Promise(r => setTimeout(r, 100));

		const toggle = container.querySelector('.load-cmd-toggle');
		expect(toggle).toBeTruthy();
		expect(toggle?.tagName.toLowerCase()).toBe('button');
	});

	it('textareas have font-size class for iOS zoom prevention', async () => {
		const { default: Page } = await import('../routes/+page.svelte');
		mount(Page, { target: container });

		await new Promise(r => setTimeout(r, 100));

		const textareas = container.querySelectorAll('textarea.input-area');
		expect(textareas.length).toBeGreaterThan(0);
	});

	it('load-cmd-input exists and is an input element', async () => {
		const { default: Page } = await import('../routes/+page.svelte');
		mount(Page, { target: container });

		await new Promise(r => setTimeout(r, 100));

		// Open the load-cmd section first
		const toggle = container.querySelector('.load-cmd-toggle') as HTMLElement;
		toggle?.click();

		await new Promise(r => setTimeout(r, 50));

		const loadCmdInput = container.querySelector('.load-cmd-input');
		expect(loadCmdInput).toBeTruthy();
		expect(loadCmdInput?.tagName.toLowerCase()).toBe('input');
	});
});
