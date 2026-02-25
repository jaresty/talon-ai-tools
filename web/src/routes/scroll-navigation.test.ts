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
	getPersonaIntentTokens: vi.fn().mockReturnValue([]),
	AXES: ['completeness', 'scope', 'method', 'form', 'channel', 'directional'],
	toPersonaSlug: vi.fn().mockReturnValue(''),
	getUsagePatterns: vi.fn().mockReturnValue([]),
	getStarterPacks: vi.fn().mockReturnValue([])
}));

vi.mock('$lib/incompatibilities.js', () => ({
	findConflicts: vi.fn().mockReturnValue([])
}));

function fireWheel(el: Element, deltaX: number, deltaY: number) {
	const event = new WheelEvent('wheel', {
		bubbles: true,
		cancelable: true,
		deltaX,
		deltaY
	});
	el.dispatchEvent(event);
}

function activeTabLabel(container: HTMLDivElement): string | undefined {
	return container.querySelector<HTMLElement>('[role="tab"][aria-selected="true"]')?.textContent?.trim();
}

// AXES_WITH_PERSONA order: ['persona', 'task', 'completeness', 'scope', 'method', 'form', 'channel', 'directional']
// Default activeTab = 'task'; left swipe (deltaX > 0 = scroll right = go to prev) → 'persona'
// left swipe (deltaX < 0 = scroll left = advance) → 'completeness'

describe('Page — Desktop Horizontal Scroll Tab Navigation', () => {
	let container: HTMLDivElement;

	beforeEach(() => {
		vi.clearAllMocks();
		mockLocalStorage.getItem.mockReturnValue(null);
		container = document.createElement('div');
		document.body.appendChild(container);
	});

	// F1g — dominant horizontal WheelEvent advances the active tab
	it('F1g: a dominant horizontal WheelEvent (deltaX=50, deltaY=10) on .layout advances the active tab', async () => {
		const { default: Page } = await import('../routes/+page.svelte');
		mount(Page, { target: container });
		await new Promise(r => setTimeout(r, 100));

		expect(activeTabLabel(container)).toBe('task');

		const layout = container.querySelector('.layout') as HTMLElement;
		fireWheel(layout, -50, 10); // negative deltaX = scroll left = advance tab
		flushSync();

		expect(activeTabLabel(container)).toBe('completeness');
	});

	// F2g — diagonal WheelEvent does not change the active tab
	it('F2g: a diagonal WheelEvent (deltaX=30, deltaY=30) does not change the active tab', async () => {
		const { default: Page } = await import('../routes/+page.svelte');
		mount(Page, { target: container });
		await new Promise(r => setTimeout(r, 100));

		const before = activeTabLabel(container);
		const layout = container.querySelector('.layout') as HTMLElement;
		fireWheel(layout, 30, 30); // equal deltaX/Y — not dominant
		flushSync();

		expect(activeTabLabel(container)).toBe(before);
	});

	// F3g — second WheelEvent within 400ms of a tab change does not advance a second tab
	it('F3g: a second WheelEvent within 400ms of a tab change does not advance a second tab', async () => {
		const { default: Page } = await import('../routes/+page.svelte');
		mount(Page, { target: container });
		await new Promise(r => setTimeout(r, 100));

		const layout = container.querySelector('.layout') as HTMLElement;
		fireWheel(layout, -50, 5); // first qualifying wheel → 'completeness'
		flushSync();
		expect(activeTabLabel(container)).toBe('completeness');

		// Immediately fire again within 400ms cooldown
		fireWheel(layout, -50, 5);
		flushSync();
		// Must still be 'completeness', not 'scope'
		expect(activeTabLabel(container)).toBe('completeness');
	});

	// F4g — WheelEvent inside .h-scroll-boundary does not change the active tab
	it('F4g: a horizontal WheelEvent whose target is inside a .h-scroll-boundary does not change the active tab', async () => {
		const { default: Page } = await import('../routes/+page.svelte');
		mount(Page, { target: container });
		await new Promise(r => setTimeout(r, 100));

		// Inject a .h-scroll-boundary element into the selector panel
		const panel = container.querySelector('.selector-panel') as HTMLElement;
		const boundary = document.createElement('div');
		boundary.className = 'h-scroll-boundary';
		panel.appendChild(boundary);
		flushSync();

		const before = activeTabLabel(container);
		// Fire wheel event from inside the boundary — should not reach the navigation handler
		fireWheel(boundary, -50, 5);
		flushSync();

		expect(activeTabLabel(container)).toBe(before);
	});

	// F5g — prefers-reduced-motion: no transition class/style on tab switch
	it('F5g: with prefers-reduced-motion: reduce, a qualifying WheelEvent switches tabs without CSS transition', async () => {
		// Simulate prefers-reduced-motion
		window.matchMedia = vi.fn().mockImplementation((query: string) => ({
			matches: query === '(prefers-reduced-motion: reduce)',
			media: query,
			onchange: null,
			addListener: vi.fn(),
			removeListener: vi.fn(),
			addEventListener: vi.fn(),
			removeEventListener: vi.fn(),
			dispatchEvent: vi.fn()
		}));

		const { default: Page } = await import('../routes/+page.svelte');
		mount(Page, { target: container });
		await new Promise(r => setTimeout(r, 100));

		const layout = container.querySelector('.layout') as HTMLElement;
		const panel = container.querySelector('.selector-panel') as HTMLElement;
		fireWheel(layout, -50, 5);
		flushSync();

		// Tab must change
		expect(activeTabLabel(container)).toBe('completeness');
		// Panel must not have a transition style set (instant switch)
		expect(panel.style.transition).not.toMatch(/transform/);
	});

	// F6g — localStorage opt-out disables navigation
	it('F6g: with gestures.horizontalScrollNav=false in localStorage, a qualifying WheelEvent does not change the active tab', async () => {
		mockLocalStorage.getItem.mockImplementation((key: string) =>
			key === 'bar-scroll-nav-enabled' ? 'false' : null
		);

		const { default: Page } = await import('../routes/+page.svelte');
		mount(Page, { target: container });
		await new Promise(r => setTimeout(r, 100));

		const before = activeTabLabel(container);
		const layout = container.querySelector('.layout') as HTMLElement;
		fireWheel(layout, -50, 5);
		flushSync();

		expect(activeTabLabel(container)).toBe(before);
	});

	// F7g — qualifying WheelEvent routes through the existing tab-change path
	it('F7g: a qualifying WheelEvent changes the active tab exactly as a tab click would (same aria-selected result)', async () => {
		const { default: Page } = await import('../routes/+page.svelte');
		mount(Page, { target: container });
		await new Promise(r => setTimeout(r, 100));

		// Record state after a direct tab click to 'completeness'
		const completenessTab = container.querySelector<HTMLElement>('[id="tab-completeness"]')!;
		completenessTab.click();
		flushSync();
		const afterClick = activeTabLabel(container);
		expect(afterClick).toBe('completeness');

		// Reset to 'task'
		const taskTab = container.querySelector<HTMLElement>('[id="tab-task"]')!;
		taskTab.click();
		flushSync();
		expect(activeTabLabel(container)).toBe('task');

		// Now advance via wheel — should produce the same result as click
		const layout = container.querySelector('.layout') as HTMLElement;
		fireWheel(layout, -50, 5);
		flushSync();
		expect(activeTabLabel(container)).toBe('completeness');
	});
});
