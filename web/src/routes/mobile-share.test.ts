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
		persona_presets: [],
		reference_key: { task: '', addendum: '', constraints: '', constraints_axes: {}, persona: '', subject: '' },
		execution_reminder: '',
		planning_directive: '',
		meta_interpretation_guidance: ''
	}),
	getAxisTokens: vi.fn().mockReturnValue([]),
	getTaskTokens: vi.fn().mockReturnValue([{ token: 'show', label: 'Explain' }]),
	getPersonaPresets: vi.fn().mockReturnValue([]),
	getPersonaAxisTokens: vi.fn().mockReturnValue([]),
	AXES: ['completeness', 'scope', 'method', 'form', 'channel', 'directional'],
	toPersonaSlug: vi.fn().mockReturnValue(''),
	toAxisTokenSlug: vi.fn((s: string) => s.toLowerCase().replace(/\s+/g, '-')),
	getUsagePatterns: vi.fn().mockReturnValue([]),
	getStarterPacks: vi.fn().mockReturnValue([]),
	getCompositionData: vi.fn().mockReturnValue(null),
	getChipState: vi.fn().mockReturnValue(null),
	getReverseChipState: vi.fn().mockReturnValue(null),
	getChipStateWithReason: vi.fn().mockReturnValue({ state: null, naturalWith: [], cautionWith: [] })
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

	// ── Copy Link (always clipboard, never native share) ──────────────────────

	it('renders a .copy-link-btn in the action overlay', async () => {
		const { default: Page } = await import('../routes/+page.svelte');
		mount(Page, { target: container });
		await new Promise(r => setTimeout(r, 100));

		expect(container.querySelector('.action-overlay .copy-link-btn')).toBeTruthy();
	});

	it('renders a .copy-link-btn in the desktop action-row', async () => {
		const { default: Page } = await import('../routes/+page.svelte');
		mount(Page, { target: container });
		await new Promise(r => setTimeout(r, 100));

		expect(container.querySelector('.action-row .copy-link-btn')).toBeTruthy();
	});

	it('copy-link-btn always calls clipboard.writeText — never navigator.share', async () => {
		const mockShare = vi.fn().mockResolvedValue(undefined);
		Object.defineProperty(navigator, 'share', { value: mockShare, writable: true, configurable: true });

		const { default: Page } = await import('../routes/+page.svelte');
		mount(Page, { target: container });
		await new Promise(r => setTimeout(r, 100));

		(container.querySelector('.action-overlay .copy-link-btn') as HTMLElement).click();
		await new Promise(r => setTimeout(r, 50));

		expect((navigator.clipboard as { writeText: ReturnType<typeof vi.fn> }).writeText).toHaveBeenCalled();
		expect(mockShare).not.toHaveBeenCalled();
	});

	it('copy-link-btn shows confirmation state after click', async () => {
		const { default: Page } = await import('../routes/+page.svelte');
		mount(Page, { target: container });
		await new Promise(r => setTimeout(r, 100));

		const btn = container.querySelector('.action-overlay .copy-link-btn') as HTMLElement;
		const before = btn.textContent;
		btn.click();
		await new Promise(r => setTimeout(r, 50));

		expect(btn.textContent).not.toBe(before);
	});

	// ── Keyboard shortcut ⌘⇧L / Ctrl+Shift+L ────────────────────────────────

	it('⌘⇧L dispatches copyLink (clipboard.writeText called)', async () => {
		const { default: Page } = await import('../routes/+page.svelte');
		mount(Page, { target: container });
		await new Promise(r => setTimeout(r, 100));

		document.dispatchEvent(new KeyboardEvent('keydown', { key: 'l', shiftKey: true, metaKey: true, bubbles: true }));
		await new Promise(r => setTimeout(r, 50));

		expect((navigator.clipboard as { writeText: ReturnType<typeof vi.fn> }).writeText).toHaveBeenCalled();
	});

	it('copy-link-btn has title attribute mentioning ⌘⇧L', async () => {
		const { default: Page } = await import('../routes/+page.svelte');
		mount(Page, { target: container });
		await new Promise(r => setTimeout(r, 100));

		const btn = container.querySelector('.action-row .copy-link-btn') as HTMLElement | null;
		expect(btn?.title).toMatch(/⌘⇧L|Ctrl\+Shift\+L/);
	});

	it('shortcut-legend table contains a row for ⌘⇧L', async () => {
		const { default: Page } = await import('../routes/+page.svelte');
		mount(Page, { target: container });
		await new Promise(r => setTimeout(r, 100));

		const table = container.querySelector('.shortcut-table');
		expect(table?.textContent).toMatch(/⌘⇧L|Ctrl\+Shift\+L/);
	});
});
