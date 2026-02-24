/**
 * ADR-0140: Keyboard Focus Model Fixes and Shortcut Legend
 * Specifying validations for F1k–F5k.
 * Written BEFORE implementation — all tests must fail red initially.
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
		{ token: 'show', label: 'Explain', description: '', guidance: '', use_when: '' }
	]),
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
	renderPrompt: vi.fn().mockReturnValue('MOCK RENDERED PROMPT')
}));

// 9 tokens — enough to render the filter input (threshold is >8)
const MANY_TOKENS = Array.from({ length: 9 }, (_, i) => ({
	token: `tok${i}`,
	label: `Token ${i}`,
	description: '',
	guidance: '',
	use_when: ''
}));

const THREE_TOKENS = [
	{ token: 'alpha', label: 'Alpha', description: '', guidance: '', use_when: '' },
	{ token: 'beta', label: 'Beta', description: '', guidance: '', use_when: '' },
	{ token: 'gamma', label: 'Gamma', description: '', guidance: '', use_when: '' }
];

// ---------------------------------------------------------------------------
// K1 — Listbox Tab foothold and panel Tab containment
// ---------------------------------------------------------------------------

describe('ADR-0140 — K1: Tab from filter stays in panel (F2k)', () => {
	// F2k: Tab from filter input focuses a chip, does not escape to LOAD COMMAND
	it('F2k: Tab on filter input focuses the active chip', async () => {
		const { default: TokenSelector } = await import('$lib/TokenSelector.svelte');
		const container = document.createElement('div');
		document.body.appendChild(container);

		mount(TokenSelector, {
			target: container,
			props: {
				axis: 'method',
				tokens: MANY_TOKENS,
				selected: [],
				maxSelect: 1,
				onToggle: vi.fn(),
				onTabNext: vi.fn(),
				onTabPrev: vi.fn()
			}
		});
		flushSync();

		const filter = container.querySelector('.filter-input') as HTMLInputElement | null;
		expect(filter).toBeTruthy();
		filter!.focus();
		flushSync();

		// Dispatch Tab on the filter — should move focus to first chip, not exit component
		filter!.dispatchEvent(new KeyboardEvent('keydown', { key: 'Tab', bubbles: true }));
		flushSync();
		await new Promise((r) => setTimeout(r, 10));

		const firstChip = container.querySelector('[role="option"]') as HTMLElement | null;
		expect(firstChip).toBeTruthy();
		expect(document.activeElement).toBe(firstChip);

		document.body.removeChild(container);
	});
});

describe('ADR-0140 — K1: Mid-panel Tab stays in panel (F3k)', () => {
	// F3k: Tab from a non-last chip wraps to the last chip, not LOAD COMMAND
	it('F3k: Tab from non-last chip moves focus to last chip', async () => {
		const { default: TokenSelector } = await import('$lib/TokenSelector.svelte');
		const container = document.createElement('div');
		document.body.appendChild(container);

		mount(TokenSelector, {
			target: container,
			props: {
				axis: 'task',
				tokens: THREE_TOKENS,
				selected: [],
				maxSelect: 1,
				onToggle: vi.fn(),
				onTabNext: vi.fn(), // defined → mid-panel Tab should wrap
				onTabPrev: vi.fn()
			}
		});
		flushSync();

		// Focus first chip (index 0, not last)
		const chips = container.querySelectorAll('[role="option"]');
		expect(chips.length).toBe(3);
		(chips[0] as HTMLElement).focus();
		flushSync();

		// Dispatch Tab on the listbox
		const grid = container.querySelector('[role="listbox"]') as HTMLElement;
		grid.dispatchEvent(new KeyboardEvent('keydown', { key: 'Tab', bubbles: true }));
		flushSync();
		await new Promise((r) => setTimeout(r, 10));

		// Focus should land on last chip, not leave the component
		const lastChip = chips[chips.length - 1] as HTMLElement;
		expect(document.activeElement).toBe(lastChip);

		document.body.removeChild(container);
	});
});

describe('ADR-0140 — K1: Shift+Tab from task first chip returns to tab-bar (F4k)', () => {
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

	// F4k: Shift+Tab from the first chip of the task panel focuses the active tab button
	it('F4k: Shift+Tab from first task chip focuses the active tab-bar button', async () => {
		const { default: Page } = await import('../routes/+page.svelte');
		mount(Page, { target: container });
		await new Promise((r) => setTimeout(r, 50));
		flushSync();

		// task is active by default; it has one chip: 'show' (index 0, also index 0 === first)
		const chips = container.querySelectorAll('[role="option"]');
		expect(chips.length).toBeGreaterThan(0);
		(chips[0] as HTMLElement).focus();
		flushSync();

		const grid = container.querySelector('[role="listbox"]') as HTMLElement;
		grid.dispatchEvent(new KeyboardEvent('keydown', { key: 'Tab', shiftKey: true, bubbles: true }));
		flushSync();
		await new Promise((r) => setTimeout(r, 20));
		flushSync();

		// The active tab button (task, aria-selected=true) should have focus
		const activeTab = container.querySelector(
			'[role="tab"][aria-selected="true"]'
		) as HTMLElement | null;
		expect(activeTab).toBeTruthy();
		expect(document.activeElement).toBe(activeTab);
	});
});

// ---------------------------------------------------------------------------
// K2 — DOM order: Tab from active tab reaches panel before LOAD COMMAND
// ---------------------------------------------------------------------------

describe('ADR-0140 — K2: Tab from tab button reaches panel not LOAD COMMAND (F1k)', () => {
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

	// F1k: The load-cmd-toggle appears AFTER the axis panel in DOM order
	it('F1k: load-cmd-toggle appears after the axis panel listbox in DOM order', async () => {
		const { default: Page } = await import('../routes/+page.svelte');
		mount(Page, { target: container });
		await new Promise((r) => setTimeout(r, 50));
		flushSync();

		const listbox = container.querySelector('[role="listbox"]') as HTMLElement | null;
		const loadCmdBtn = container.querySelector('.load-cmd-toggle') as HTMLElement | null;
		expect(listbox).toBeTruthy();
		expect(loadCmdBtn).toBeTruthy();

		// Compare DOM positions: listbox should come BEFORE load-cmd-toggle
		const position = listbox!.compareDocumentPosition(loadCmdBtn!);
		// Node.DOCUMENT_POSITION_FOLLOWING = 4 (loadCmdBtn comes after listbox)
		expect(position & Node.DOCUMENT_POSITION_FOLLOWING).toBe(Node.DOCUMENT_POSITION_FOLLOWING);
	});
});

// ---------------------------------------------------------------------------
// K3 — Keyboard shortcut legend
// ---------------------------------------------------------------------------

describe('ADR-0140 — K3: Shortcut legend present (F5k)', () => {
	let container: HTMLDivElement;

	beforeEach(() => {
		vi.clearAllMocks();
		container = document.createElement('div');
		document.body.appendChild(container);
	});

	afterEach(() => {
		document.body.removeChild(container);
	});

	// F5k: A .shortcut-legend <details> element exists with at least 10 table rows
	it('F5k: shortcut legend details element is present with 10+ shortcut rows', async () => {
		const { default: Page } = await import('../routes/+page.svelte');
		mount(Page, { target: container });
		await new Promise((r) => setTimeout(r, 50));
		flushSync();

		const legend = container.querySelector('.shortcut-legend') as HTMLDetailsElement | null;
		expect(legend).toBeTruthy();
		expect(legend!.tagName.toLowerCase()).toBe('details');

		const rows = legend!.querySelectorAll('tr');
		// At least 10 rows (header + 9 shortcuts, or 10 shortcuts)
		expect(rows.length).toBeGreaterThanOrEqual(10);
	});
});

// ---------------------------------------------------------------------------
// K4 — Shift+Tab from chip stops at filter before exiting panel
// ---------------------------------------------------------------------------

describe('ADR-0141 — K4: Shift+Tab from first chip focuses filter (F6k)', () => {
	// F6k: When filter is visible, Shift+Tab on first chip focuses the filter, not previous tab
	it('F6k: Shift+Tab on first chip when filter is rendered focuses filter input', async () => {
		const { default: TokenSelector } = await import('$lib/TokenSelector.svelte');
		const onTabPrev = vi.fn();
		const container = document.createElement('div');
		document.body.appendChild(container);

		mount(TokenSelector, {
			target: container,
			props: {
				axis: 'method',
				tokens: MANY_TOKENS,
				selected: [],
				maxSelect: 1,
				onToggle: vi.fn(),
				onTabNext: vi.fn(),
				onTabPrev
			}
		});
		flushSync();

		const filter = container.querySelector('.filter-input') as HTMLInputElement | null;
		expect(filter).toBeTruthy();

		const chips = container.querySelectorAll('[role="option"]');
		(chips[0] as HTMLElement).focus();
		flushSync();

		const grid = container.querySelector('[role="listbox"]') as HTMLElement;
		grid.dispatchEvent(new KeyboardEvent('keydown', { key: 'Tab', shiftKey: true, bubbles: true }));
		flushSync();
		await new Promise((r) => setTimeout(r, 10));

		expect(document.activeElement).toBe(filter);
		expect(onTabPrev).not.toHaveBeenCalled();

		document.body.removeChild(container);
	});
});

describe('ADR-0141 — K4: Shift+Tab from filter does not call onTabPrev (F7k)', () => {
	// F7k: Shift+Tab on the filter is not intercepted — browser handles it naturally,
	// returning focus to the active tab button (correct reverse of tab-bar → filter).
	it('F7k: Shift+Tab on filter input does not fire onTabPrev', async () => {
		const { default: TokenSelector } = await import('$lib/TokenSelector.svelte');
		const onTabPrev = vi.fn();
		const container = document.createElement('div');
		document.body.appendChild(container);

		mount(TokenSelector, {
			target: container,
			props: {
				axis: 'method',
				tokens: MANY_TOKENS,
				selected: [],
				maxSelect: 1,
				onToggle: vi.fn(),
				onTabNext: vi.fn(),
				onTabPrev
			}
		});
		flushSync();

		const filter = container.querySelector('.filter-input') as HTMLInputElement | null;
		expect(filter).toBeTruthy();
		filter!.focus();
		flushSync();

		filter!.dispatchEvent(new KeyboardEvent('keydown', { key: 'Tab', shiftKey: true, bubbles: true }));
		flushSync();
		await new Promise((r) => setTimeout(r, 10));

		expect(onTabPrev).not.toHaveBeenCalled();

		document.body.removeChild(container);
	});
});
