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
	getChipState: vi.fn().mockReturnValue(null),
		getReverseChipState: vi.fn().mockReturnValue(null)
}));

vi.mock('$lib/incompatibilities.js', () => ({
	findConflicts: vi.fn().mockReturnValue([])
}));

vi.mock('$lib/renderPrompt.js', () => ({
	renderPrompt: vi.fn().mockReturnValue('MOCK RENDERED PROMPT')
}));

describe('Page — Share: two distinct actions', () => {
	let container: HTMLDivElement;

	beforeEach(() => {
		vi.clearAllMocks();
		container = document.createElement('div');
		document.body.appendChild(container);
		Object.defineProperty(navigator, 'clipboard', {
			value: { writeText: vi.fn().mockResolvedValue(undefined) },
			writable: true,
			configurable: true
		});
		Object.defineProperty(navigator, 'share', {
			value: undefined,
			writable: true,
			configurable: true
		});
	});

	// ── Presence ──────────────────────────────────────────────────────────────

	it('renders a .share-prompt-btn (share rendered prompt) in the action overlay', async () => {
		const { default: Page } = await import('../routes/+page.svelte');
		mount(Page, { target: container });
		await new Promise(r => setTimeout(r, 100));

		expect(container.querySelector('.action-overlay .share-prompt-btn')).toBeTruthy();
	});

	it('renders a .share-link-btn (share URL) in the action overlay', async () => {
		const { default: Page } = await import('../routes/+page.svelte');
		mount(Page, { target: container });
		await new Promise(r => setTimeout(r, 100));

		expect(container.querySelector('.action-overlay .share-link-btn')).toBeTruthy();
	});

	// ── Share Prompt (text → ChatGPT) ─────────────────────────────────────────

	it('share-prompt-btn calls navigator.share({ text }) when available', async () => {
		const mockShare = vi.fn().mockResolvedValue(undefined);
		Object.defineProperty(navigator, 'share', { value: mockShare, writable: true, configurable: true });

		const { default: Page } = await import('../routes/+page.svelte');
		mount(Page, { target: container });
		await new Promise(r => setTimeout(r, 100));

		(container.querySelector('.action-overlay .share-prompt-btn') as HTMLElement).click();
		await new Promise(r => setTimeout(r, 50));

		expect(mockShare).toHaveBeenCalledOnce();
		expect(mockShare).toHaveBeenCalledWith(expect.objectContaining({ text: expect.any(String) }));
		// Must NOT include a url — this is a text share for pasting into ChatGPT
		expect(mockShare.mock.calls[0][0]).not.toHaveProperty('url');
	});

	it('share-prompt-btn falls back to clipboard.writeText when navigator.share unavailable', async () => {
		const { default: Page } = await import('../routes/+page.svelte');
		mount(Page, { target: container });
		await new Promise(r => setTimeout(r, 100));

		(container.querySelector('.action-overlay .share-prompt-btn') as HTMLElement).click();
		await new Promise(r => setTimeout(r, 50));

		expect((navigator.clipboard as { writeText: ReturnType<typeof vi.fn> }).writeText).toHaveBeenCalled();
	});

	// ── Share Link (URL → send to a friend) ───────────────────────────────────

	it('share-link-btn calls navigator.share({ url }) when available', async () => {
		const mockShare = vi.fn().mockResolvedValue(undefined);
		Object.defineProperty(navigator, 'share', { value: mockShare, writable: true, configurable: true });

		const { default: Page } = await import('../routes/+page.svelte');
		mount(Page, { target: container });
		await new Promise(r => setTimeout(r, 100));

		(container.querySelector('.action-overlay .share-link-btn') as HTMLElement).click();
		await new Promise(r => setTimeout(r, 50));

		expect(mockShare).toHaveBeenCalledOnce();
		expect(mockShare).toHaveBeenCalledWith(expect.objectContaining({ url: expect.any(String) }));
		// Must NOT include raw text — this is a URL share
		expect(mockShare.mock.calls[0][0]).not.toHaveProperty('text');
	});

	it('share-link-btn URL contains a hash fragment encoding the state', async () => {
		const mockShare = vi.fn().mockResolvedValue(undefined);
		Object.defineProperty(navigator, 'share', { value: mockShare, writable: true, configurable: true });

		const { default: Page } = await import('../routes/+page.svelte');
		mount(Page, { target: container });
		await new Promise(r => setTimeout(r, 100));

		(container.querySelector('.action-overlay .share-link-btn') as HTMLElement).click();
		await new Promise(r => setTimeout(r, 50));

		expect(mockShare.mock.calls[0][0].url).toMatch(/#.+/);
	});

	it('share-link-btn falls back to clipboard.writeText when navigator.share unavailable', async () => {
		const { default: Page } = await import('../routes/+page.svelte');
		mount(Page, { target: container });
		await new Promise(r => setTimeout(r, 100));

		(container.querySelector('.action-overlay .share-link-btn') as HTMLElement).click();
		await new Promise(r => setTimeout(r, 50));

		expect((navigator.clipboard as { writeText: ReturnType<typeof vi.fn> }).writeText).toHaveBeenCalled();
	});
});
