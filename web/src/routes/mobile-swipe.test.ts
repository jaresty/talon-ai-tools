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

function fireTouchMove(el: Element, clientX: number, clientY: number) {
	const event = new Event('touchmove', { bubbles: true, cancelable: true });
	Object.defineProperty(event, 'touches', { value: [{ clientX, clientY }] });
	el.dispatchEvent(event);
}

function fireTouchStart(el: Element, clientX: number, clientY: number) {
	const event = new Event('touchstart', { bubbles: true, cancelable: true });
	Object.defineProperty(event, 'touches', { value: [{ clientX, clientY }] });
	el.dispatchEvent(event);
}

function fireTouchEnd(el: Element, clientX: number, clientY: number) {
	const event = new Event('touchend', { bubbles: true, cancelable: true });
	Object.defineProperty(event, 'changedTouches', { value: [{ clientX, clientY }] });
	el.dispatchEvent(event);
}

function activeTabLabel(container: HTMLDivElement): string | undefined {
	return container.querySelector<HTMLElement>('[role="tab"][aria-selected="true"]')?.textContent?.trim();
}

// AXES_WITH_PERSONA order: ['persona', 'task', 'completeness', 'scope', 'method', 'form', 'channel', 'directional']
// Default activeTab = 'task'; left swipe → 'completeness'; right swipe → 'persona'

describe('Page — Swipe to Switch Tabs', () => {
	let container: HTMLDivElement;

	beforeEach(() => {
		vi.clearAllMocks();
		container = document.createElement('div');
		document.body.appendChild(container);
	});

	it('left swipe (>50px, horizontal-dominant) on .selector-panel advances to next tab', async () => {
		const { default: Page } = await import('../routes/+page.svelte');
		mount(Page, { target: container });
		await new Promise(r => setTimeout(r, 100));

		expect(activeTabLabel(container)).toBe('task');

		const panel = container.querySelector('.selector-panel') as HTMLElement;
		fireTouchStart(panel, 300, 200);
		fireTouchEnd(panel, 150, 210); // dx = -150, dy = 10
		flushSync();

		expect(activeTabLabel(container)).toBe('completeness');
	});

	it('right swipe (>50px, horizontal-dominant) on .selector-panel retreats to previous tab', async () => {
		const { default: Page } = await import('../routes/+page.svelte');
		mount(Page, { target: container });
		await new Promise(r => setTimeout(r, 100));

		// Advance once to 'completeness'
		const panel = container.querySelector('.selector-panel') as HTMLElement;
		fireTouchStart(panel, 300, 200);
		fireTouchEnd(panel, 150, 210);
		flushSync();
		expect(activeTabLabel(container)).toBe('completeness');

		// Right swipe back to 'task'
		fireTouchStart(panel, 150, 200);
		fireTouchEnd(panel, 300, 210); // dx = +150, dy = 10
		flushSync();

		expect(activeTabLabel(container)).toBe('task');
	});

	it('vertical swipe does NOT change the active tab', async () => {
		const { default: Page } = await import('../routes/+page.svelte');
		mount(Page, { target: container });
		await new Promise(r => setTimeout(r, 100));

		const panel = container.querySelector('.selector-panel') as HTMLElement;
		const before = activeTabLabel(container);

		fireTouchStart(panel, 200, 100);
		fireTouchEnd(panel, 210, 400); // dx = 10, dy = 300 — vertical
		flushSync();

		expect(activeTabLabel(container)).toBe(before);
	});

	it('short swipe (<50px) does NOT change the active tab', async () => {
		const { default: Page } = await import('../routes/+page.svelte');
		mount(Page, { target: container });
		await new Promise(r => setTimeout(r, 100));

		const panel = container.querySelector('.selector-panel') as HTMLElement;
		const before = activeTabLabel(container);

		fireTouchStart(panel, 300, 200);
		fireTouchEnd(panel, 265, 202); // dx = -35, below 50px threshold
		flushSync();

		expect(activeTabLabel(container)).toBe(before);
	});

	it('swipe starting on an input element does NOT change the active tab', async () => {
		const { default: Page } = await import('../routes/+page.svelte');
		mount(Page, { target: container });
		await new Promise(r => setTimeout(r, 100));

		// Open load-cmd section to expose the input
		const toggle = container.querySelector('.load-cmd-toggle') as HTMLElement;
		toggle.click();
		flushSync();

		const before = activeTabLabel(container);
		const input = container.querySelector('.load-cmd-input') as HTMLElement;
		expect(input).toBeTruthy();

		// Touch starts on the input — should be ignored
		fireTouchStart(input, 300, 200);
		fireTouchEnd(input, 150, 210); // dx = -150, would advance tab if not blocked
		flushSync();

		expect(activeTabLabel(container)).toBe(before);
	});

	// ── Visual feedback ───────────────────────────────────────────────────────

	it('shows .swipe-hint with next tab name during a left touchmove', async () => {
		const { default: Page } = await import('../routes/+page.svelte');
		mount(Page, { target: container });
		await new Promise(r => setTimeout(r, 100));

		const panel = container.querySelector('.selector-panel') as HTMLElement;
		fireTouchStart(panel, 300, 200);
		fireTouchMove(panel, 240, 202); // dx = -60, horizontal-dominant
		flushSync();

		const hint = container.querySelector('.swipe-hint');
		expect(hint).toBeTruthy();
		expect(hint?.textContent).toContain('completeness'); // next after 'task'
	});

	it('shows .swipe-hint with prev tab name during a right touchmove', async () => {
		const { default: Page } = await import('../routes/+page.svelte');
		mount(Page, { target: container });
		await new Promise(r => setTimeout(r, 100));

		const panel = container.querySelector('.selector-panel') as HTMLElement;
		fireTouchStart(panel, 200, 200);
		fireTouchMove(panel, 260, 202); // dx = +60, horizontal-dominant
		flushSync();

		const hint = container.querySelector('.swipe-hint');
		expect(hint).toBeTruthy();
		expect(hint?.textContent).toContain('persona'); // prev before 'task'
	});

	it('.swipe-hint disappears after touchend', async () => {
		const { default: Page } = await import('../routes/+page.svelte');
		mount(Page, { target: container });
		await new Promise(r => setTimeout(r, 100));

		const panel = container.querySelector('.selector-panel') as HTMLElement;
		fireTouchStart(panel, 300, 200);
		fireTouchMove(panel, 240, 202);
		flushSync();
		expect(container.querySelector('.swipe-hint')).toBeTruthy();

		fireTouchEnd(panel, 150, 210);
		flushSync();
		expect(container.querySelector('.swipe-hint')).toBeFalsy();
	});

	it('does not show .swipe-hint for vertical touchmove', async () => {
		const { default: Page } = await import('../routes/+page.svelte');
		mount(Page, { target: container });
		await new Promise(r => setTimeout(r, 100));

		const panel = container.querySelector('.selector-panel') as HTMLElement;
		fireTouchStart(panel, 200, 100);
		fireTouchMove(panel, 210, 300); // dx = 10, dy = 200 — vertical
		flushSync();

		expect(container.querySelector('.swipe-hint')).toBeFalsy();
	});

	// ── Ghost click prevention ────────────────────────────────────────────────

	it('touchend has defaultPrevented=true when a swipe completes (prevents ghost click)', async () => {
		const { default: Page } = await import('../routes/+page.svelte');
		mount(Page, { target: container });
		await new Promise(r => setTimeout(r, 100));

		const panel = container.querySelector('.selector-panel') as HTMLElement;
		fireTouchStart(panel, 300, 200);

		// Dispatch the touchend manually so we can inspect defaultPrevented
		const evt = new Event('touchend', { bubbles: true, cancelable: true });
		Object.defineProperty(evt, 'changedTouches', { value: [{ clientX: 150, clientY: 210 }] });
		panel.dispatchEvent(evt);
		flushSync();

		expect(evt.defaultPrevented).toBe(true);
	});
});
