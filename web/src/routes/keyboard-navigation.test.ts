/**
 * ADR-0139: SPA Tab Keyboard Navigation and Action Shortcuts
 * Specifying validations for F1–F8.
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

const mockClipboard = {
	writeText: vi.fn().mockResolvedValue(undefined)
};

Object.defineProperty(globalThis, 'navigator', {
	value: { clipboard: mockClipboard },
	writable: true
});

vi.mock('$lib/grammar.js', () => ({
	loadGrammar: vi.fn().mockResolvedValue({
		hierarchy: { axis_soft_caps: {} },
		tokens: {},
		persona_presets: [],
		persona: { use_when: {} }
	}),
	getAxisTokens: vi.fn().mockReturnValue([]),
	getTaskTokens: vi.fn().mockReturnValue([
		{ token: 'show', label: 'Explain', description: 'Explain or describe', guidance: '', use_when: '' }
	]),
	getPersonaPresets: vi.fn().mockReturnValue([]),
	getPersonaAxisTokens: vi.fn().mockReturnValue([]),
	AXES: ['completeness', 'scope', 'method', 'form', 'channel', 'directional'],
	toPersonaSlug: vi.fn().mockReturnValue(''),
	getUsagePatterns: vi.fn().mockReturnValue([])
}));

vi.mock('$lib/incompatibilities.js', () => ({
	findConflicts: vi.fn().mockReturnValue([])
}));

vi.mock('$lib/renderPrompt.js', () => ({
	renderPrompt: vi.fn().mockReturnValue('MOCK RENDERED PROMPT')
}));

describe('ADR-0139 — T1: ARIA tablist on tab-bar nav (F1/F2/F3)', () => {
	let container: HTMLDivElement;

	beforeEach(() => {
		vi.clearAllMocks();
		mockClipboard.writeText.mockClear();
		container = document.createElement('div');
		document.body.appendChild(container);
	});

	afterEach(() => {
		document.body.removeChild(container);
	});

	// F3: Tab-bar nav has role="tablist"; buttons have role="tab" and aria-selected
	it('F3: tab-bar nav has role=tablist and tabs have role=tab with aria-selected', async () => {
		const { default: Page } = await import('../routes/+page.svelte');
		mount(Page, { target: container });
		await new Promise((r) => setTimeout(r, 50));
		flushSync();

		const nav = container.querySelector('nav.tab-bar');
		expect(nav?.getAttribute('role')).toBe('tablist');

		const tabs = container.querySelectorAll('nav.tab-bar .tab');
		expect(tabs.length).toBeGreaterThan(0);

		tabs.forEach((tab) => {
			expect(tab.getAttribute('role')).toBe('tab');
			const selected = tab.getAttribute('aria-selected');
			expect(selected === 'true' || selected === 'false').toBe(true);
		});

		// Only the active tab should have aria-selected="true"
		const activeTabs = Array.from(tabs).filter(
			(t) => t.getAttribute('aria-selected') === 'true'
		);
		expect(activeTabs.length).toBe(1);
	});

	// F1: ArrowRight on tablist advances activeTab to next axis
	it('F1: ArrowRight on tablist moves active tab to next axis', async () => {
		const { default: Page } = await import('../routes/+page.svelte');
		mount(Page, { target: container });
		await new Promise((r) => setTimeout(r, 50));
		flushSync();

		const nav = container.querySelector('nav.tab-bar') as HTMLElement;
		expect(nav).toBeTruthy();

		// Find which tab is currently active
		const tabsBefore = container.querySelectorAll('nav.tab-bar .tab');
		const activeBeforeIdx = Array.from(tabsBefore).findIndex(
			(t) => t.getAttribute('aria-selected') === 'true'
		);

		// Dispatch ArrowRight on the nav
		nav.dispatchEvent(new KeyboardEvent('keydown', { key: 'ArrowRight', bubbles: true }));
		flushSync();

		const tabsAfter = container.querySelectorAll('nav.tab-bar .tab');
		const activeAfterIdx = Array.from(tabsAfter).findIndex(
			(t) => t.getAttribute('aria-selected') === 'true'
		);

		const expectedNextIdx = (activeBeforeIdx + 1) % tabsAfter.length;
		expect(activeAfterIdx).toBe(expectedNextIdx);
	});

	// F2: ArrowLeft on tablist moves active tab to previous axis (cycling)
	it('F2: ArrowLeft on tablist moves active tab to previous axis (cycling)', async () => {
		const { default: Page } = await import('../routes/+page.svelte');
		mount(Page, { target: container });
		await new Promise((r) => setTimeout(r, 50));
		flushSync();

		const nav = container.querySelector('nav.tab-bar') as HTMLElement;
		expect(nav).toBeTruthy();

		const tabsBefore = container.querySelectorAll('nav.tab-bar .tab');
		const activeBeforeIdx = Array.from(tabsBefore).findIndex(
			(t) => t.getAttribute('aria-selected') === 'true'
		);

		// Dispatch ArrowLeft on the nav
		nav.dispatchEvent(new KeyboardEvent('keydown', { key: 'ArrowLeft', bubbles: true }));
		flushSync();

		const tabsAfter = container.querySelectorAll('nav.tab-bar .tab');
		const activeAfterIdx = Array.from(tabsAfter).findIndex(
			(t) => t.getAttribute('aria-selected') === 'true'
		);

		const n = tabsAfter.length;
		const expectedPrevIdx = (activeBeforeIdx - 1 + n) % n;
		expect(activeAfterIdx).toBe(expectedPrevIdx);
	});
});

describe('ADR-0139 — T2: Auto-advance Tab-exhaustion (F4/F5)', () => {
	// F4: Tab on last chip in TokenSelector calls onTabNext
	it('F4: Tab pressed on last chip fires onTabNext callback', async () => {
		const { default: TokenSelector } = await import('$lib/TokenSelector.svelte');
		const onTabNext = vi.fn();
		const onTabPrev = vi.fn();
		const tokens = [
			{ token: 'show', label: 'Show', description: '', guidance: '', use_when: '' },
			{ token: 'make', label: 'Make', description: '', guidance: '', use_when: '' }
		];

		const container = document.createElement('div');
		document.body.appendChild(container);

		mount(TokenSelector, {
			target: container,
			props: { axis: 'task', tokens, selected: [], maxSelect: 1, onToggle: vi.fn(), onTabNext, onTabPrev }
		});
		flushSync();

		// Focus last chip (index 1) then press Tab
		const chips = container.querySelectorAll('[role="option"]');
		expect(chips.length).toBe(2);
		(chips[1] as HTMLElement).focus();
		flushSync();

		// Dispatch Tab on the grid (which wraps the chips)
		const grid = container.querySelector('[role="listbox"]') as HTMLElement;
		grid.dispatchEvent(new KeyboardEvent('keydown', { key: 'Tab', bubbles: true }));
		flushSync();

		expect(onTabNext).toHaveBeenCalledTimes(1);
		expect(onTabPrev).not.toHaveBeenCalled();
		document.body.removeChild(container);
	});

	// F5: Shift+Tab on first chip fires onTabPrev callback
	it('F5: Shift+Tab on first chip fires onTabPrev callback', async () => {
		const { default: TokenSelector } = await import('$lib/TokenSelector.svelte');
		const onTabNext = vi.fn();
		const onTabPrev = vi.fn();
		const tokens = [
			{ token: 'show', label: 'Show', description: '', guidance: '', use_when: '' },
			{ token: 'make', label: 'Make', description: '', guidance: '', use_when: '' }
		];

		const container = document.createElement('div');
		document.body.appendChild(container);

		mount(TokenSelector, {
			target: container,
			props: { axis: 'task', tokens, selected: [], maxSelect: 1, onToggle: vi.fn(), onTabNext, onTabPrev }
		});
		flushSync();

		// Focus first chip (index 0) then press Shift+Tab
		const chips = container.querySelectorAll('[role="option"]');
		(chips[0] as HTMLElement).focus();
		flushSync();

		const grid = container.querySelector('[role="listbox"]') as HTMLElement;
		grid.dispatchEvent(new KeyboardEvent('keydown', { key: 'Tab', shiftKey: true, bubbles: true }));
		flushSync();

		expect(onTabPrev).toHaveBeenCalledTimes(1);
		expect(onTabNext).not.toHaveBeenCalled();
		document.body.removeChild(container);
	});
});

describe('ADR-0139 — T3: Action keyboard shortcuts (F6/F7/F8)', () => {
	let container: HTMLDivElement;

	beforeEach(() => {
		vi.clearAllMocks();
		mockClipboard.writeText.mockClear();
		container = document.createElement('div');
		document.body.appendChild(container);
	});

	afterEach(() => {
		document.body.removeChild(container);
	});

	// F6: Cmd+Shift+C fires copyCommand (writes command string to clipboard)
	it('F6: Cmd+Shift+C fires copyCommand', async () => {
		const { default: Page } = await import('../routes/+page.svelte');
		mount(Page, { target: container });
		await new Promise((r) => setTimeout(r, 50));
		flushSync();

		document.dispatchEvent(
			new KeyboardEvent('keydown', { key: 'c', shiftKey: true, metaKey: true, bubbles: true })
		);
		flushSync();
		await new Promise((r) => setTimeout(r, 20));

		expect(mockClipboard.writeText).toHaveBeenCalled();
		const callArg = mockClipboard.writeText.mock.calls[0]?.[0];
		expect(typeof callArg).toBe('string');
		expect(callArg).toMatch(/^bar build/);
	});

	// F7: Cmd+Shift+P fires copyPrompt (writes rendered prompt to clipboard)
	it('F7: Cmd+Shift+P fires copyPrompt', async () => {
		const { default: Page } = await import('../routes/+page.svelte');
		mount(Page, { target: container });
		await new Promise((r) => setTimeout(r, 50));
		flushSync();

		document.dispatchEvent(
			new KeyboardEvent('keydown', { key: 'p', shiftKey: true, metaKey: true, bubbles: true })
		);
		flushSync();
		await new Promise((r) => setTimeout(r, 20));

		expect(mockClipboard.writeText).toHaveBeenCalledWith('MOCK RENDERED PROMPT');
	});

	// F8: Cmd+Shift+U fires sharePrompt (writes URL to clipboard)
	it('F8: Cmd+Shift+U fires sharePrompt', async () => {
		const { default: Page } = await import('../routes/+page.svelte');
		mount(Page, { target: container });
		await new Promise((r) => setTimeout(r, 50));
		flushSync();

		Object.defineProperty(window, 'location', {
			value: { origin: 'http://localhost', pathname: '/', hash: '' },
			writable: true
		});
		Object.defineProperty(window, 'history', {
			value: { replaceState: vi.fn() },
			writable: true
		});

		document.dispatchEvent(
			new KeyboardEvent('keydown', { key: 'u', shiftKey: true, metaKey: true, bubbles: true })
		);
		flushSync();
		await new Promise((r) => setTimeout(r, 20));

		expect(mockClipboard.writeText).toHaveBeenCalled();
		const callArg = mockClipboard.writeText.mock.calls[0]?.[0];
		expect(typeof callArg).toBe('string');
		expect(callArg).toContain('http://localhost');
	});
});
