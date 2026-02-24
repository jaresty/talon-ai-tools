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
	getPersonaPresets: vi.fn().mockReturnValue([]),
	getPersonaAxisTokens: vi.fn().mockReturnValue([]),
	AXES: ['completeness', 'scope', 'method', 'form', 'channel', 'directional'],
	toPersonaSlug: vi.fn().mockReturnValue(''),
	getUsagePatterns: vi.fn().mockReturnValue([]),
	getStarterPacks: vi.fn().mockReturnValue([])
}));

vi.mock('$lib/incompatibilities.js', () => ({
	findConflicts: vi.fn().mockReturnValue([])
}));

vi.mock('$lib/renderPrompt.js', () => ({
	renderPrompt: vi.fn().mockReturnValue('MOCK RENDERED PROMPT TEXT')
}));

describe('Page — Output Panel (rendered prompt display)', () => {
	let container: HTMLDivElement;

	beforeEach(() => {
		vi.clearAllMocks();
		container = document.createElement('div');
		document.body.appendChild(container);
	});

	it('toggle button uses "Output" label, not "Preview"', async () => {
		const { default: Page } = await import('../routes/+page.svelte');
		mount(Page, { target: container });

		await new Promise(r => setTimeout(r, 100));

		const toggleBtn = container.querySelector('.preview-toggle');
		expect(toggleBtn?.textContent?.toLowerCase()).toContain('output');
		expect(toggleBtn?.textContent?.toLowerCase()).not.toContain('preview');
	});

	it('.prompt-preview element exists inside the output panel', async () => {
		const { default: Page } = await import('../routes/+page.svelte');
		mount(Page, { target: container });

		await new Promise(r => setTimeout(r, 100));

		const promptPreview = container.querySelector('.prompt-preview');
		expect(promptPreview).toBeTruthy();
	});
});
