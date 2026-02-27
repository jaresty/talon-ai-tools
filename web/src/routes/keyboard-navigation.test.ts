/**
 * ADR-0139: SPA Tab Keyboard Navigation and Action Shortcuts
 * Specifying validations for F1–F8 and regression coverage for F1b/F2b/F4b/F5b.
 */
import { flushSync } from 'svelte';
import { mount } from 'svelte';
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest';
import { getAxisTokens } from '$lib/grammar.js';

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
	getPersonaIntentTokens: vi.fn().mockReturnValue([]),
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

// ---------------------------------------------------------------------------
// Regression coverage: gaps that allowed T1/T2 bugs to ship undetected
// ---------------------------------------------------------------------------

describe('ADR-0141 — K1: ArrowKey focus stays on tab strip (F1c/F2c)', () => {
	let container: HTMLDivElement;

	beforeEach(() => {
		vi.clearAllMocks();
		mockClipboard.writeText.mockClear();
		container = document.createElement('div');
		document.body.appendChild(container);
	});

	afterEach(() => {
		document.body.removeChild(container);
		vi.mocked(getAxisTokens).mockReturnValue([]);
	});

	// F1c: ArrowRight must leave focus on the active tab button, not move it to a chip
	it('F1c: ArrowRight on tab-bar leaves focus on the newly-active tab button', async () => {
		vi.mocked(getAxisTokens).mockImplementation((_grammar, axis) =>
			axis === 'completeness'
				? [{ token: 'deep', label: 'Deep', description: '', guidance: '', use_when: '' }]
				: []
		);

		const { default: Page } = await import('../routes/+page.svelte');
		mount(Page, { target: container });
		await new Promise((r) => setTimeout(r, 50));
		flushSync();

		const nav = container.querySelector('nav.tab-bar') as HTMLElement;
		nav.dispatchEvent(new KeyboardEvent('keydown', { key: 'ArrowRight', bubbles: true }));
		flushSync();
		await new Promise((r) => setTimeout(r, 20));
		flushSync();

		// Focus must be on the active tab button (completeness), NOT on a chip
		const activeTab = container.querySelector('[role="tab"][aria-selected="true"]') as HTMLElement | null;
		expect(activeTab).toBeTruthy();
		expect(activeTab?.textContent?.trim()).toBe('completeness');
		expect(document.activeElement).toBe(activeTab);
	});

	// F2c: ArrowLeft must leave focus on the active tab button, not move it to a chip
	it('F2c: ArrowLeft on tab-bar leaves focus on the newly-active tab button', async () => {
		vi.mocked(getAxisTokens).mockImplementation((_grammar, axis) =>
			axis === 'completeness'
				? [{ token: 'deep', label: 'Deep', description: '', guidance: '', use_when: '' }]
				: []
		);

		const { default: Page } = await import('../routes/+page.svelte');
		mount(Page, { target: container });
		await new Promise((r) => setTimeout(r, 50));
		flushSync();

		const nav = container.querySelector('nav.tab-bar') as HTMLElement;
		// Advance to completeness
		nav.dispatchEvent(new KeyboardEvent('keydown', { key: 'ArrowRight', bubbles: true }));
		flushSync();
		await new Promise((r) => setTimeout(r, 20));
		flushSync();

		// ArrowLeft back to task
		nav.dispatchEvent(new KeyboardEvent('keydown', { key: 'ArrowLeft', bubbles: true }));
		flushSync();
		await new Promise((r) => setTimeout(r, 20));
		flushSync();

		// Focus must be on the active tab button (task), NOT on a chip
		const activeTab = container.querySelector('[role="tab"][aria-selected="true"]') as HTMLElement | null;
		expect(activeTab).toBeTruthy();
		expect(activeTab?.textContent?.trim()).toBe('task');
		expect(document.activeElement).toBe(activeTab);
	});
});

describe('ADR-0139 — T2 wiring regression: +page.svelte passes callbacks (F4b/F5b)', () => {
	afterEach(() => {
		vi.mocked(getAxisTokens).mockReturnValue([]);
	});

	// F4b: Integration — Tab from last chip of task in the full page advances the axis
	it('F4b: Tab from last task chip advances to completeness axis and focuses first chip', async () => {
		vi.mocked(getAxisTokens).mockImplementation((_grammar, axis) =>
			axis === 'completeness'
				? [{ token: 'deep', label: 'Deep', description: '', guidance: '', use_when: '' }]
				: []
		);

		const container = document.createElement('div');
		document.body.appendChild(container);

		const { default: Page } = await import('../routes/+page.svelte');
		mount(Page, { target: container });
		await new Promise((r) => setTimeout(r, 50));
		flushSync();

		// Task panel has one chip: 'show' (index 0 === filtered.length - 1)
		const chips = container.querySelectorAll('[role="option"]');
		expect(chips.length).toBe(1);
		(chips[0] as HTMLElement).focus();
		flushSync();

		const grid = container.querySelector('[role="listbox"]') as HTMLElement;
		grid.dispatchEvent(new KeyboardEvent('keydown', { key: 'Tab', bubbles: true }));
		flushSync();
		await new Promise((r) => setTimeout(r, 20));
		flushSync();

		// completeness tab should be active
		const tabs = container.querySelectorAll('[role="tab"]');
		const completenessTab = Array.from(tabs).find((t) => t.textContent?.trim() === 'completeness');
		expect(completenessTab?.getAttribute('aria-selected')).toBe('true');

		// first chip in completeness ('deep') should have focus
		const deepChip = container.querySelector('[role="option"]') as HTMLElement | null;
		expect(deepChip?.textContent).toContain('deep');
		expect(document.activeElement).toBe(deepChip);

		document.body.removeChild(container);
	});

	// F5b: Integration — Shift+Tab from first chip of completeness retreats to task
	it('F5b: Shift+Tab from first completeness chip retreats to task axis and focuses last chip', async () => {
		vi.mocked(getAxisTokens).mockImplementation((_grammar, axis) =>
			axis === 'completeness'
				? [
						{ token: 'deep', label: 'Deep', description: '', guidance: '', use_when: '' },
						{ token: 'full', label: 'Full', description: '', guidance: '', use_when: '' }
					]
				: []
		);

		const container = document.createElement('div');
		document.body.appendChild(container);

		const { default: Page } = await import('../routes/+page.svelte');
		mount(Page, { target: container });
		await new Promise((r) => setTimeout(r, 50));
		flushSync();

		// Advance to completeness via tab bar
		const nav = container.querySelector('nav.tab-bar') as HTMLElement;
		nav.dispatchEvent(new KeyboardEvent('keydown', { key: 'ArrowRight', bubbles: true }));
		flushSync();
		await new Promise((r) => setTimeout(r, 20));
		flushSync();

		// Focus first chip (deep, index 0)
		const chips = container.querySelectorAll('[role="option"]');
		(chips[0] as HTMLElement).focus();
		flushSync();

		// Shift+Tab — triggers onTabPrev → goToPrevTab
		const grid = container.querySelector('[role="listbox"]') as HTMLElement;
		grid.dispatchEvent(new KeyboardEvent('keydown', { key: 'Tab', shiftKey: true, bubbles: true }));
		flushSync();
		await new Promise((r) => setTimeout(r, 20));
		flushSync();

		// task tab should be active
		const tabs = container.querySelectorAll('[role="tab"]');
		const taskTab = Array.from(tabs).find((t) => t.textContent?.trim() === 'task');
		expect(taskTab?.getAttribute('aria-selected')).toBe('true');

		// task's only chip ('show') should have focus
		const showChip = container.querySelector('[role="option"]') as HTMLElement | null;
		expect(showChip?.textContent).toContain('show');
		expect(document.activeElement).toBe(showChip);

		document.body.removeChild(container);
	});
});

// ---------------------------------------------------------------------------
// ADR-0141 — K2: Persona panel focus loss on Tab-exhaustion wrap (F3c)
// ---------------------------------------------------------------------------

describe('ADR-0141 — K2: Tab-exhaustion to persona panel does not lose focus (F3c)', () => {
	afterEach(() => {
		vi.mocked(getAxisTokens).mockReturnValue([]);
	});

	// F3c: Tab from last directional chip wraps to persona panel; focus must not land on <body>
	it('F3c: Tab-exhaustion from directional panel focuses first element in persona panel', async () => {
		vi.mocked(getAxisTokens).mockImplementation((_grammar, axis) =>
			axis === 'directional'
				? [{ token: 'fog', label: 'Fog', description: '', guidance: '', use_when: '' }]
				: []
		);

		const container = document.createElement('div');
		document.body.appendChild(container);

		const { default: Page } = await import('../routes/+page.svelte');
		mount(Page, { target: container });
		await new Promise((r) => setTimeout(r, 50));
		flushSync();

		// Navigate to directional tab
		const nav = container.querySelector('nav.tab-bar') as HTMLElement;
		// default activeTab=task(1); directional is index 7 → 6 ArrowRights
		for (let i = 0; i < 6; i++) {
			nav.dispatchEvent(new KeyboardEvent('keydown', { key: 'ArrowRight', bubbles: true }));
			flushSync();
		}
		await new Promise((r) => setTimeout(r, 20));
		flushSync();

		// Focus the only directional chip (fog, index 0 === last)
		const chips = container.querySelectorAll('[role="option"]');
		expect(chips.length).toBeGreaterThan(0);
		(chips[0] as HTMLElement).focus();
		flushSync();

		// Tab from last chip triggers goToNextTab → persona
		const grid = container.querySelector('[role="listbox"]') as HTMLElement;
		grid.dispatchEvent(new KeyboardEvent('keydown', { key: 'Tab', bubbles: true }));
		flushSync();
		await new Promise((r) => setTimeout(r, 30));
		flushSync();

		// Focus must NOT be on <body>
		expect(document.activeElement?.tagName).not.toBe('BODY');

		// Active tab must be persona
		const activeTab = container.querySelector('[role="tab"][aria-selected="true"]');
		expect(activeTab?.textContent?.trim()).toBe('persona');

		document.body.removeChild(container);
	});
});

// ---------------------------------------------------------------------------
// ADR-0145 — KS: Global shortcut + filter focus + Enter-to-toggle
// ---------------------------------------------------------------------------

describe('ADR-0145 — KS: Alt+./Alt+, global shortcuts and filter Enter-to-toggle', () => {
	let container: HTMLDivElement;

	beforeEach(() => {
		vi.clearAllMocks();
		container = document.createElement('div');
		document.body.appendChild(container);
	});

	afterEach(() => {
		document.body.removeChild(container);
	});

	// KS1: Alt+. from non-textarea context switches to next tab
	it('KS1: Alt+. switches to next tab', async () => {
		const { default: Page } = await import('../routes/+page.svelte');
		mount(Page, { target: container });
		await new Promise((r) => setTimeout(r, 100));
		flushSync();

		const tabsBefore = container.querySelectorAll('[role="tab"]');
		const activeBeforeIdx = Array.from(tabsBefore).findIndex(
			(t) => t.getAttribute('aria-selected') === 'true'
		);

		document.dispatchEvent(
			new KeyboardEvent('keydown', { key: '.', code: 'Period', altKey: true, bubbles: true })
		);
		flushSync();

		const tabsAfter = container.querySelectorAll('[role="tab"]');
		const activeAfterIdx = Array.from(tabsAfter).findIndex(
			(t) => t.getAttribute('aria-selected') === 'true'
		);
		const expectedNextIdx = (activeBeforeIdx + 1) % tabsAfter.length;
		expect(activeAfterIdx).toBe(expectedNextIdx);
	});

	// KS2: Alt+. from a textarea does NOT switch tabs
	it('KS2: Alt+. dispatched with target=TEXTAREA does not switch tabs', async () => {
		const { default: Page } = await import('../routes/+page.svelte');
		mount(Page, { target: container });
		await new Promise((r) => setTimeout(r, 100));
		flushSync();

		const tabsBefore = container.querySelectorAll('[role="tab"]');
		const activeBeforeIdx = Array.from(tabsBefore).findIndex(
			(t) => t.getAttribute('aria-selected') === 'true'
		);

		// Create a real textarea and dispatch from it
		const textarea = document.createElement('textarea');
		container.appendChild(textarea);
		textarea.focus();

		textarea.dispatchEvent(
			new KeyboardEvent('keydown', { key: '.', code: 'Period', altKey: true, bubbles: true })
		);
		flushSync();

		const tabsAfter = container.querySelectorAll('[role="tab"]');
		const activeAfterIdx = Array.from(tabsAfter).findIndex(
			(t) => t.getAttribute('aria-selected') === 'true'
		);
		expect(activeAfterIdx).toBe(activeBeforeIdx);
	});

	// KS3: Alt+, switches to previous tab
	it('KS3: Alt+, switches to previous tab', async () => {
		const { default: Page } = await import('../routes/+page.svelte');
		mount(Page, { target: container });
		await new Promise((r) => setTimeout(r, 100));
		flushSync();

		const tabsBefore = container.querySelectorAll('[role="tab"]');
		const n = tabsBefore.length;
		const activeBeforeIdx = Array.from(tabsBefore).findIndex(
			(t) => t.getAttribute('aria-selected') === 'true'
		);

		document.dispatchEvent(
			new KeyboardEvent('keydown', { key: ',', code: 'Comma', altKey: true, bubbles: true })
		);
		flushSync();

		const tabsAfter = container.querySelectorAll('[role="tab"]');
		const activeAfterIdx = Array.from(tabsAfter).findIndex(
			(t) => t.getAttribute('aria-selected') === 'true'
		);
		const expectedPrevIdx = (activeBeforeIdx - 1 + n) % n;
		expect(activeAfterIdx).toBe(expectedPrevIdx);
	});

	// KS-FILTER: Alt+. focuses filter input after switching tabs
});
