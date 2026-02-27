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
	getStarterPacks: vi.fn().mockReturnValue([]),
	getCompositionData: vi.fn().mockReturnValue(null),
	getChipState: vi.fn().mockReturnValue(null)
}));

vi.mock('$lib/incompatibilities.js', () => ({
	findConflicts: vi.fn().mockReturnValue([])
}));

describe('Page — Mobile Floating Action Button', () => {
	let container: HTMLDivElement;

	beforeEach(() => {
		vi.clearAllMocks();
		container = document.createElement('div');
		document.body.appendChild(container);
	});

	it('FAB button is a direct child of .layout, not inside .preview-panel', async () => {
		const { default: Page } = await import('../routes/+page.svelte');
		mount(Page, { target: container });

		await new Promise(r => setTimeout(r, 100));

		const previewPanel = container.querySelector('.preview-panel');
		const fabBtn = container.querySelector('.fab-btn');

		expect(fabBtn).toBeTruthy();
		// FAB must NOT be nested inside the preview panel
		expect(previewPanel?.contains(fabBtn)).toBe(false);
	});

	it('action-overlay is at layout root, not inside .preview-panel', async () => {
		const { default: Page } = await import('../routes/+page.svelte');
		mount(Page, { target: container });

		await new Promise(r => setTimeout(r, 100));

		const previewPanel = container.querySelector('.preview-panel');
		const actionOverlay = container.querySelector('.action-overlay');

		expect(actionOverlay).toBeTruthy();
		// Action overlay must NOT be nested inside the preview panel
		expect(previewPanel?.contains(actionOverlay)).toBe(false);
	});

	it('FAB click adds mobile-visible class to action-overlay', async () => {
		const { default: Page } = await import('../routes/+page.svelte');
		mount(Page, { target: container });

		await new Promise(r => setTimeout(r, 100));

		const fabBtn = container.querySelector('.fab-btn') as HTMLElement;
		const actionOverlay = container.querySelector('.action-overlay');

		expect(actionOverlay?.classList.contains('mobile-visible')).toBe(false);
		fabBtn.click();
		flushSync();
		expect(actionOverlay?.classList.contains('mobile-visible')).toBe(true);
	});

	it('has copy, share-prompt, and share-link buttons inside action-overlay', async () => {
		const { default: Page } = await import('../routes/+page.svelte');
		mount(Page, { target: container });

		await new Promise(r => setTimeout(r, 100));

		expect(container.querySelector('.action-overlay .copy-btn')).toBeTruthy();
		expect(container.querySelector('.action-overlay .share-prompt-btn')).toBeTruthy();
		expect(container.querySelector('.action-overlay .share-link-btn')).toBeTruthy();
	});
});
