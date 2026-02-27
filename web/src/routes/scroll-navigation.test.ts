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

// jsdom does not ship Touch; add a minimal polyfill so touch-related tests can run
if (typeof (globalThis as any).Touch === 'undefined') {
	(globalThis as any).Touch = class Touch {
		identifier: number; target: EventTarget; clientX: number; clientY: number;
		screenX = 0; screenY = 0; pageX = 0; pageY = 0;
		radiusX = 0; radiusY = 0; rotationAngle = 0; force = 0;
		constructor(init: { identifier: number; target: EventTarget; clientX: number; clientY: number }) {
			Object.assign(this, init);
		}
	};
}

vi.mock('$lib/grammar.js', () => ({
	loadGrammar: vi.fn().mockResolvedValue({
		hierarchy: { axis_soft_caps: {} },
		tokens: {},
		persona_presets: [],
		persona: { use_when: {} }
	}),
	getAxisTokens: vi.fn().mockReturnValue([]),
	getTaskTokens: vi.fn().mockReturnValue([{ token: 'show', label: 'Explain' }]),
	getPersonaPresets: vi.fn().mockReturnValue([]),
	getPersonaAxisTokens: vi.fn().mockReturnValue([]),
	getPersonaIntentTokens: vi.fn().mockReturnValue([]),
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

vi.mock('$lib/renderPrompt.js', () => ({
	renderPrompt: vi.fn().mockReturnValue('MOCK RENDERED PROMPT')
}));

function activeTabLabel(container: HTMLDivElement): string | undefined {
	return container.querySelector<HTMLElement>('[role="tab"][aria-selected="true"]')?.textContent?.trim();
}

// AXES_WITH_PERSONA order: ['persona', 'task', 'completeness', 'scope', 'method', 'form', 'channel', 'directional']
// Default activeTab = 'task'

describe('Page — Directional Slide Animation', () => {
	let container: HTMLDivElement;

	beforeEach(() => {
		vi.clearAllMocks();
		mockLocalStorage.getItem.mockReturnValue(null);
		container = document.createElement('div');
		document.body.appendChild(container);
	});

	afterEach(() => {
		document.body.removeChild(container);
	});

	// SA1 — clicking a tab to the right adds slide-next class to .selector-panel
	it('SA1: clicking a tab to the right of the active tab adds slide-next class to .selector-panel', async () => {
		const { default: Page } = await import('../routes/+page.svelte');
		mount(Page, { target: container });
		await new Promise(r => setTimeout(r, 100));
		flushSync();

		expect(activeTabLabel(container)).toBe('task'); // starts on task (index 1)

		// Click 'completeness' (index 2 — to the right of task)
		const completenessTab = container.querySelector<HTMLElement>('[id="tab-completeness"]')!;
		expect(completenessTab).toBeTruthy();
		completenessTab.click();
		flushSync();

		const panel = container.querySelector('.selector-panel') as HTMLElement;
		expect(panel.classList.contains('slide-next')).toBe(true);
		expect(panel.classList.contains('slide-prev')).toBe(false);
	});

	// SA2 — clicking a tab to the left adds slide-prev class to .selector-panel
	it('SA2: clicking a tab to the left of the active tab adds slide-prev class to .selector-panel', async () => {
		const { default: Page } = await import('../routes/+page.svelte');
		mount(Page, { target: container });
		await new Promise(r => setTimeout(r, 100));
		flushSync();

		// First advance to 'completeness' (index 2) without animation concern
		const completenessTab = container.querySelector<HTMLElement>('[id="tab-completeness"]')!;
		completenessTab.click();
		flushSync();

		// Now click 'task' (index 1 — to the left of completeness)
		const taskTab = container.querySelector<HTMLElement>('[id="tab-task"]')!;
		taskTab.click();
		flushSync();

		const panel = container.querySelector('.selector-panel') as HTMLElement;
		expect(panel.classList.contains('slide-prev')).toBe(true);
		expect(panel.classList.contains('slide-next')).toBe(false);
	});

	// SA3 — animationend on .selector-panel removes the slide class
	it('SA3: animationend event on .selector-panel removes the slide class', async () => {
		const { default: Page } = await import('../routes/+page.svelte');
		mount(Page, { target: container });
		await new Promise(r => setTimeout(r, 100));
		flushSync();

		const completenessTab = container.querySelector<HTMLElement>('[id="tab-completeness"]')!;
		completenessTab.click();
		flushSync();

		const panel = container.querySelector('.selector-panel') as HTMLElement;
		expect(panel.classList.contains('slide-next')).toBe(true);

		// Fire animationend
		panel.dispatchEvent(new Event('animationend', { bubbles: true }));
		flushSync();

		expect(panel.classList.contains('slide-next')).toBe(false);
		expect(panel.classList.contains('slide-prev')).toBe(false);
	});

	// SA4 — goToNextTab(false, false) (mobile swipe path) does NOT set a slide class
	it('SA4: goToNextTab called with animate=false (mobile swipe path) does not add a slide class', async () => {
		const { default: Page } = await import('../routes/+page.svelte');
		mount(Page, { target: container });
		await new Promise(r => setTimeout(r, 100));
		flushSync();

		// Simulate the mobile swipe path: fire a touchstart/touchend sequence
		const panel = container.querySelector('.selector-panel') as HTMLElement;

		// Simulate a swipe: touchstart at x=200, touchend at x=50 (dx=-150 → next tab)
		panel.dispatchEvent(new TouchEvent('touchstart', {
			bubbles: true,
			touches: [new Touch({ identifier: 1, target: panel, clientX: 200, clientY: 0 })]
		}));
		panel.dispatchEvent(new TouchEvent('touchend', {
			bubbles: true,
			changedTouches: [new Touch({ identifier: 1, target: panel, clientX: 50, clientY: 0 })]
		}));

		// Wait for the swipe animation timeout (250ms) to complete
		await new Promise(r => setTimeout(r, 300));
		flushSync();

		// After swipe completes, slide-next/slide-prev must NOT be set (mobile has own slide-out)
		expect(panel.classList.contains('slide-next')).toBe(false);
		expect(panel.classList.contains('slide-prev')).toBe(false);
	});

	// SA5 — switching to the same tab does NOT add a slide class
	it('SA5: clicking the already-active tab does not add a slide class', async () => {
		const { default: Page } = await import('../routes/+page.svelte');
		mount(Page, { target: container });
		await new Promise(r => setTimeout(r, 100));
		flushSync();

		// Click the active tab (task) again
		const taskTab = container.querySelector<HTMLElement>('[id="tab-task"]')!;
		taskTab.click();
		flushSync();

		const panel = container.querySelector('.selector-panel') as HTMLElement;
		expect(panel.classList.contains('slide-next')).toBe(false);
		expect(panel.classList.contains('slide-prev')).toBe(false);
	});
});
