import { flushSync } from 'svelte';
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

describe('Page — Mobile Preview Toggle', () => {
	let container: HTMLDivElement;

	beforeEach(() => {
		vi.clearAllMocks();
		container = document.createElement('div');
		document.body.appendChild(container);
	});

	it('renders the page component', async () => {
		const { default: Page } = await import('../routes/+page.svelte');
		mount(Page, { target: container });

		const header = container.querySelector('header');
		expect(header).toBeTruthy();
	});

	it('has preview toggle button', async () => {
		const { default: Page } = await import('../routes/+page.svelte');
		mount(Page, { target: container });

		await new Promise(r => setTimeout(r, 100));

		const toggleBtn = container.querySelector('.preview-toggle');
		expect(toggleBtn).toBeTruthy();
	});

	it('preview panel is in the DOM', async () => {
		const { default: Page } = await import('../routes/+page.svelte');
		mount(Page, { target: container });

		await new Promise(r => setTimeout(r, 100));

		const previewPanel = container.querySelector('.preview-panel');
		expect(previewPanel).toBeTruthy();
	});

	it('clicking toggle toggles the visible class', async () => {
		const { default: Page } = await import('../routes/+page.svelte');
		mount(Page, { target: container });

		await new Promise(r => setTimeout(r, 100));

		const toggleBtn = container.querySelector('.preview-toggle');
		const previewPanel = container.querySelector('.preview-panel');

		expect(toggleBtn).toBeTruthy();
		expect(previewPanel).toBeTruthy();

		// Initially hidden on mobile (showPreview defaults to false)
		expect(previewPanel?.classList.contains('visible')).toBe(false);

		// Click to show
		(toggleBtn as HTMLElement).click();
		flushSync();
		expect(previewPanel?.classList.contains('visible')).toBe(true);

		// Click again to hide
		(toggleBtn as HTMLElement).click();
		flushSync();
		expect(previewPanel?.classList.contains('visible')).toBe(false);
	});
});
