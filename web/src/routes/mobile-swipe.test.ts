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

	// ── Tab switching (delayed by slide-out animation) ────────────────────────

	it('left swipe advances to next tab after the slide-out animation (~250ms)', async () => {
		const { default: Page } = await import('../routes/+page.svelte');
		mount(Page, { target: container });
		await new Promise(r => setTimeout(r, 100));

		expect(activeTabLabel(container)).toBe('task');

		const panel = container.querySelector('.selector-panel') as HTMLElement;
		fireTouchStart(panel, 300, 200);
		fireTouchEnd(panel, 150, 210); // dx = -150, dy = 10
		flushSync();

		// Tab does NOT change immediately — slide-out animation plays first
		expect(activeTabLabel(container)).toBe('task');

		await new Promise(r => setTimeout(r, 300));
		expect(activeTabLabel(container)).toBe('completeness');
	});

	it('right swipe retreats to previous tab after the slide-out animation (~250ms)', async () => {
		const { default: Page } = await import('../routes/+page.svelte');
		mount(Page, { target: container });
		await new Promise(r => setTimeout(r, 100));

		// Advance to 'completeness' first
		const panel = container.querySelector('.selector-panel') as HTMLElement;
		fireTouchStart(panel, 300, 200);
		fireTouchEnd(panel, 150, 210);
		await new Promise(r => setTimeout(r, 300));
		expect(activeTabLabel(container)).toBe('completeness');

		// Right swipe back to 'task'
		fireTouchStart(panel, 150, 200);
		fireTouchEnd(panel, 300, 210); // dx = +150, dy = 10
		await new Promise(r => setTimeout(r, 300));
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

		const toggle = container.querySelector('.load-cmd-toggle') as HTMLElement;
		toggle.click();
		flushSync();

		const before = activeTabLabel(container);
		const input = container.querySelector('.load-cmd-input') as HTMLElement;
		expect(input).toBeTruthy();

		fireTouchStart(input, 300, 200);
		fireTouchEnd(input, 150, 210);
		flushSync();

		expect(activeTabLabel(container)).toBe(before);
	});

	// ── Panel drag feedback ───────────────────────────────────────────────────

	it('panel translates left (negative X) during a left touchmove', async () => {
		const { default: Page } = await import('../routes/+page.svelte');
		mount(Page, { target: container });
		await new Promise(r => setTimeout(r, 100));

		const panel = container.querySelector('.selector-panel') as HTMLElement;
		fireTouchStart(panel, 300, 200);
		fireTouchMove(panel, 240, 202); // dx = -60
		flushSync();

		expect(panel.style.transform).toMatch(/translateX\(-60px\)/);
	});

	it('panel translates right (positive X) during a right touchmove', async () => {
		const { default: Page } = await import('../routes/+page.svelte');
		mount(Page, { target: container });
		await new Promise(r => setTimeout(r, 100));

		const panel = container.querySelector('.selector-panel') as HTMLElement;
		fireTouchStart(panel, 200, 200);
		fireTouchMove(panel, 260, 202); // dx = +60
		flushSync();

		expect(panel.style.transform).toMatch(/translateX\(60px\)/);
	});

	it('panel returns to translateX(0px) after an aborted swipe', async () => {
		const { default: Page } = await import('../routes/+page.svelte');
		mount(Page, { target: container });
		await new Promise(r => setTimeout(r, 100));

		const panel = container.querySelector('.selector-panel') as HTMLElement;
		fireTouchStart(panel, 300, 200);
		fireTouchMove(panel, 260, 202); // dx = -40, dragging
		flushSync();

		fireTouchEnd(panel, 265, 202); // dx = -35, below threshold → snap back
		flushSync();

		expect(panel.style.transform).toMatch(/translateX\(0px\)/);
	});

	it('vertical touchmove does not translate the panel horizontally', async () => {
		const { default: Page } = await import('../routes/+page.svelte');
		mount(Page, { target: container });
		await new Promise(r => setTimeout(r, 100));

		const panel = container.querySelector('.selector-panel') as HTMLElement;
		fireTouchStart(panel, 200, 100);
		fireTouchMove(panel, 210, 300); // dx = 10, dy = 200 — vertical
		flushSync();

		// No horizontal translation for a vertical drag
		const transform = panel.style.transform;
		expect(transform === '' || transform === 'translateX(0px)' || !transform.includes('translateX(-') && !transform.match(/translateX\(\d+px\)/)).toBe(true);
	});

	// ── Ghost click prevention ────────────────────────────────────────────────

	it('a ghost click inside .layout after a swipe is absorbed by the capture listener', async () => {
		const { default: Page } = await import('../routes/+page.svelte');
		mount(Page, { target: container });
		await new Promise(r => setTimeout(r, 100));

		const panel = container.querySelector('.selector-panel') as HTMLElement;
		const fabBtn = container.querySelector('.fab-btn') as HTMLElement;

		fireTouchStart(panel, 300, 200);
		fireTouchEnd(panel, 150, 210); // confirmed swipe
		flushSync();

		// Simulate the ghost click immediately after (within 600ms window)
		fabBtn.dispatchEvent(new MouseEvent('click', { bubbles: true }));
		flushSync();

		expect(container.querySelector('.action-overlay')?.classList.contains('mobile-visible')).toBe(false);
	});

	it('touchend has defaultPrevented=true when a swipe completes (belt-and-suspenders)', async () => {
		const { default: Page } = await import('../routes/+page.svelte');
		mount(Page, { target: container });
		await new Promise(r => setTimeout(r, 100));

		const panel = container.querySelector('.selector-panel') as HTMLElement;
		fireTouchStart(panel, 300, 200);

		const evt = new Event('touchend', { bubbles: true, cancelable: true });
		Object.defineProperty(evt, 'changedTouches', { value: [{ clientX: 150, clientY: 210 }] });
		panel.dispatchEvent(evt);
		flushSync();

		expect(evt.defaultPrevented).toBe(true);
	});
});
