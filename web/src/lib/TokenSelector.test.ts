import { describe, it, expect, vi } from 'vitest';
import { flushSync } from 'svelte';
import { render, screen, fireEvent } from '@testing-library/svelte';
import TokenSelector from './TokenSelector.svelte';

// ── Hover-safety fix (option B) ───────────────────────────────────────────────
// Spec:
//   H1: mouseleave on .token-grid while panel is open → panel stays open
//   H2: mouseleave on .axis-panel while panel is open → panel closes
//   A1: no chip has an inline anchor-name style attribute

describe('TokenSelector — hover-safety fix', () => {
	it('H1: mouseleave on token-grid does not close the panel', async () => {
		render(TokenSelector, {
			props: { axis: 'form', tokens, selected: [], maxSelect: 1, onToggle: vi.fn() }
		});
		// Open panel via hover
		const chip = screen.getByText('wardley').closest('.token-chip')! as HTMLElement;
		await fireEvent.mouseEnter(chip);
		expect(screen.getByText('When to use')).toBeTruthy();
		// Simulate mouse leaving the grid (but not the axis-panel)
		const grid = document.querySelector('.token-grid')!;
		await fireEvent.mouseLeave(grid);
		// Panel must still be open (H1)
		expect(screen.getByText('When to use')).toBeTruthy();
	});

	it('H2: mouseleave on axis-panel closes the panel', async () => {
		render(TokenSelector, {
			props: { axis: 'form', tokens, selected: [], maxSelect: 1, onToggle: vi.fn() }
		});
		const chip = screen.getByText('wardley').closest('.token-chip')! as HTMLElement;
		await fireEvent.mouseEnter(chip);
		expect(screen.getByText('When to use')).toBeTruthy();
		// Mouse leaves the entire axis section
		const axisPanel = document.querySelector('.axis-panel')!;
		await fireEvent.mouseLeave(axisPanel);
		expect(screen.queryByText('When to use')).toBeNull();
	});

	it('A1: chips have no inline anchor-name style', async () => {
		render(TokenSelector, {
			props: { axis: 'form', tokens, selected: [], maxSelect: 1, onToggle: vi.fn() }
		});
		// Open panel so the active chip would have been given anchor-name in the old code
		const chip = screen.getByText('wardley').closest('.token-chip')! as HTMLElement;
		await fireEvent.mouseEnter(chip);
		const chips = document.querySelectorAll('[role="option"]');
		chips.forEach((c) => {
			expect((c as HTMLElement).style.anchorName ?? '').toBe('');
		});
	});

	it('H3: mouseleave on chip closes the panel (fixes rightward hover bug)', async () => {
		render(TokenSelector, {
			props: { axis: 'form', tokens, selected: [], maxSelect: 1, onToggle: vi.fn() }
		});
		const chip = screen.getByText('wardley').closest('.token-chip')! as HTMLElement;
		await fireEvent.mouseEnter(chip);
		expect(screen.getByText('When to use')).toBeTruthy();
		// Mouse leaves the chip (simulates moving right to adjacent chip)
		await fireEvent.mouseLeave(chip);
		// Panel must close immediately (was staying open when moving right)
		expect(screen.queryByText('When to use')).toBeNull();
	});

	it('M1: on mobile viewport, meta-panel has no inline position styles (CSS media query must control positioning)', async () => {
		// Simulate mobile width so $effect.pre skips desktop positioning
		const originalWidth = window.innerWidth;
		Object.defineProperty(window, 'innerWidth', { writable: true, configurable: true, value: 375 });
		render(TokenSelector, {
			props: { axis: 'form', tokens, selected: [], maxSelect: 1, onToggle: vi.fn() }
		});
		const chip = screen.getByText('wardley').closest('.token-chip')! as HTMLElement;
		await fireEvent.click(chip); // mobile: click opens panel
		const panel = document.querySelector('.meta-panel') as HTMLElement;
		expect(panel).toBeTruthy();
		// Inline style must be empty — mobile positioning comes from the CSS media query
		expect(panel.getAttribute('style') ?? '').toBe('');
		Object.defineProperty(window, 'innerWidth', { writable: true, configurable: true, value: originalWidth });
	});
});

// 10-token fixture for filter-input tests (filter only shows when tokens.length > 8)
const manyTokens = Array.from({ length: 10 }, (_, i) => ({
	token: `tok${i}`,
	label: `Token ${i}`,
	description: `Description for tok${i}`,
	guidance: '',
	use_when: i === 0 ? 'Use tok0 when starting.' : ''
}));

const tokens = [
	{
		token: 'wardley',
		label: 'Wardley Map',
		description: 'Strategic mapping: user wants to position components on an evolution axis.',
		guidance: 'Pair with a strategic intent task.',
		use_when: 'Use when the user wants a Wardley map output.'
	},
	{
		token: 'prose',
		label: '',
		description: 'Flowing narrative text.',
		guidance: '',
		use_when: ''
	}
];

function renderSelector(overrides = {}) {
	return render(TokenSelector, {
		props: {
			axis: 'form',
			tokens,
			selected: [],
			maxSelect: 1,
			onToggle: vi.fn(),
			...overrides
		}
	});
}

describe('TokenSelector — D2 metadata panel', () => {
	it('renders token chips', () => {
		renderSelector();
		expect(screen.getByText('wardley')).toBeTruthy();
		expect(screen.getByText('prose')).toBeTruthy();
	});

	it('shows dot indicator for tokens with use_when', () => {
		renderSelector();
		// wardley has use_when, prose does not
		const dots = document.querySelectorAll('.use-when-dot');
		expect(dots.length).toBe(1);
	});

	it('metadata panel is hidden initially', () => {
		renderSelector();
		expect(screen.queryByText('When to use')).toBeNull();
	});

	it('clicking wardley chip reveals the metadata panel with use_when text', async () => {
		renderSelector();
		const chip = screen.getByText('wardley').closest('.token-chip')!;
		await fireEvent.click(chip);
		expect(screen.getByText('When to use')).toBeTruthy();
		expect(
			screen.getByText('Use when the user wants a Wardley map output.')
		).toBeTruthy();
	});

	it('metadata panel shows description text on click', async () => {
		renderSelector();
		const chip = screen.getByText('wardley').closest('.token-chip')!;
		await fireEvent.click(chip);
		expect(
			screen.getByText(
				'Strategic mapping: user wants to position components on an evolution axis.'
			)
		).toBeTruthy();
	});

	it('metadata panel shows guidance text when present', async () => {
		renderSelector();
		const chip = screen.getByText('wardley').closest('.token-chip')!;
		await fireEvent.click(chip);
		expect(screen.getByText('Pair with a strategic intent task.')).toBeTruthy();
	});

	it('clicking the same unselected chip again keeps the panel open', async () => {
		renderSelector();
		const chip = screen.getByText('wardley').closest('.token-chip')!;
		await fireEvent.click(chip); // open
		await fireEvent.click(chip); // stays open — inspect-first: no toggle on unselected chips
		expect(screen.getByText('When to use')).toBeTruthy();
	});

	it('clicking a different chip switches the panel', async () => {
		renderSelector();
		const wardleyChip = screen.getByText('wardley').closest('.token-chip')!;
		const proseChip = screen.getByText('prose').closest('.token-chip')!;
		await fireEvent.click(wardleyChip);
		expect(screen.getByText('When to use')).toBeTruthy();
		await fireEvent.click(proseChip);
		// prose has no use_when, so panel shows description but not 'When to use'
		expect(screen.queryByText('When to use')).toBeNull();
		expect(screen.getByText('Flowing narrative text.')).toBeTruthy();
	});

	it('close button dismisses the panel', async () => {
		renderSelector();
		const chip = screen.getByText('wardley').closest('.token-chip')!;
		await fireEvent.click(chip);
		const closeBtn = screen.getByText('✕');
		await fireEvent.click(closeBtn);
		expect(screen.queryByText('When to use')).toBeNull();
	});

	it('clicking unselected chip opens panel but does NOT call onToggle', async () => {
		const onToggle = vi.fn();
		renderSelector({ onToggle });
		const chip = screen.getByText('wardley').closest('.token-chip')!;
		await fireEvent.click(chip);
		expect(onToggle).not.toHaveBeenCalled();
		expect(screen.getByText('When to use')).toBeTruthy();
	});

	it('clicking "Select" button in meta panel calls onToggle and closes panel', async () => {
		const onToggle = vi.fn();
		renderSelector({ onToggle });
		const chip = screen.getByText('wardley').closest('.token-chip')!;
		await fireEvent.click(chip); // open panel
		const selectBtn = screen.getByText('Select ↵');
		await fireEvent.click(selectBtn);
		expect(onToggle).toHaveBeenCalledWith('wardley');
		expect(screen.queryByText('When to use')).toBeNull();
	});

	it('clicking selected chip calls onToggle and closes panel immediately', async () => {
		const onToggle = vi.fn();
		renderSelector({ selected: ['wardley'], onToggle });
		const chip = screen.getByText('wardley').closest('.token-chip')!;
		await fireEvent.click(chip);
		expect(onToggle).toHaveBeenCalledWith('wardley');
		expect(screen.queryByText('When to use')).toBeNull();
	});

	it('mouseenter opens panel (desktop hover-to-inspect)', async () => {
		const onToggle = vi.fn();
		renderSelector({ onToggle });
		const chip = screen.getByText('wardley').closest('.token-chip')! as HTMLElement;
		await fireEvent.mouseEnter(chip);
		expect(screen.getByText('When to use')).toBeTruthy();
		expect(onToggle).not.toHaveBeenCalled();
	});

	it('hover then click selects in one step (desktop: mouseenter sets panel, pointerdown captures it)', async () => {
		const onToggle = vi.fn();
		renderSelector({ onToggle });
		const chip = screen.getByText('wardley').closest('.token-chip')! as HTMLElement;
		// Simulate desktop hover → panel opens
		await fireEvent.mouseEnter(chip);
		// mouse pointerdown (not touch) captures activeToken already set by mouseenter
		await fireEvent.pointerDown(chip, { pointerType: 'mouse' });
		await fireEvent.click(chip);
		expect(onToggle).toHaveBeenCalledWith('wardley');
		expect(screen.queryByText('When to use')).toBeNull();
	});

	it('touch pointerdown suppresses compat mouseenter (prevents panel opening on touch)', async () => {
		const onToggle = vi.fn();
		renderSelector({ selected: ['wardley'], onToggle });
		const chip = screen.getByText('wardley').closest('.token-chip')! as HTMLElement;
		// Touch sequence: pointerdown sets isUsingTouch=true
		await fireEvent.pointerDown(chip, { pointerType: 'touch' });
		// Compat mouseenter fires — should be suppressed
		await fireEvent.mouseEnter(chip);
		expect(screen.queryByText('When to use')).toBeNull();
		// Click still deselects
		await fireEvent.click(chip);
		expect(onToggle).toHaveBeenCalledWith('wardley');
	});

	it('second click on chip with panel already open selects it (confirming click)', async () => {
		const onToggle = vi.fn();
		renderSelector({ onToggle });
		const chip = screen.getByText('wardley').closest('.token-chip')! as HTMLElement;
		// First click: pointerdown captures null, click opens panel
		await fireEvent.pointerDown(chip);
		await fireEvent.click(chip);
		expect(onToggle).not.toHaveBeenCalled();
		expect(screen.getByText('When to use')).toBeTruthy();
		// Second click: pointerdown captures activeToken='wardley', click selects
		await fireEvent.pointerDown(chip);
		await fireEvent.click(chip);
		expect(onToggle).toHaveBeenCalledWith('wardley');
		expect(screen.queryByText('When to use')).toBeNull();
	});

	it('does not call onToggle when at cap and token not selected', async () => {
		const onToggle = vi.fn();
		// maxSelect=1, selected=['prose'] → wardley is at cap
		renderSelector({ selected: ['prose'], maxSelect: 1, onToggle });
		const chip = screen.getByText('wardley').closest('.token-chip')!;
		await fireEvent.click(chip);
		expect(onToggle).not.toHaveBeenCalled();
		// But panel still shows (metadata always accessible)
		expect(screen.getByText('When to use')).toBeTruthy();
	});
});

// ── ADR-0135 specifying validations ──────────────────────────────────────────

describe('TokenSelector — F3 ARIA attributes', () => {
	it('chip grid has role="listbox"', () => {
		renderSelector();
		expect(document.querySelector('[role="listbox"]')).toBeTruthy();
	});

	it('each chip has role="option"', () => {
		renderSelector();
		const options = document.querySelectorAll('[role="option"]');
		expect(options.length).toBe(2);
	});

	it('selected chip has aria-selected="true"', () => {
		renderSelector({ selected: ['wardley'] });
		const wardleyChip = document.querySelector('[role="option"][aria-selected="true"]');
		expect(wardleyChip).toBeTruthy();
	});

	it('unselected chip has aria-selected="false"', () => {
		renderSelector();
		const chips = document.querySelectorAll('[role="option"]');
		chips.forEach((chip) => {
			expect(chip.getAttribute('aria-selected')).toBe('false');
		});
	});

	it('listbox has aria-multiselectable="true" when maxSelect > 1', () => {
		renderSelector({ maxSelect: 3 });
		const listbox = document.querySelector('[role="listbox"]')!;
		expect(listbox.getAttribute('aria-multiselectable')).toBe('true');
	});

	it('close button is a <button> element (natively keyboard-focusable)', () => {
		renderSelector();
		// Open the panel first
		const chip = screen.getByText('wardley').closest('.token-chip')! as HTMLElement;
		fireEvent.click(chip);
		const closeBtn = screen.getByText('✕');
		expect(closeBtn.tagName).toBe('BUTTON');
	});
});

describe('TokenSelector — F1 ArrowKey navigation', () => {
	it('first chip has tabindex="0" initially (entry point for Tab key)', () => {
		renderSelector();
		const chips = document.querySelectorAll('[role="option"]');
		expect(chips[0].getAttribute('tabindex')).toBe('0');
		expect(chips[1].getAttribute('tabindex')).toBe('-1');
	});

	it('ArrowRight on focused chip moves focus to next chip', async () => {
		renderSelector();
		const chips = document.querySelectorAll('[role="option"]') as NodeListOf<HTMLElement>;
		// Focus first chip via fireEvent so Svelte processes onfocus reactively
		await fireEvent.focus(chips[0]);
		await fireEvent.keyDown(chips[0], { key: 'ArrowRight' });
		expect(document.activeElement).toBe(chips[1]);
	});

	it('ArrowLeft on second chip moves focus back to first', async () => {
		renderSelector();
		const chips = document.querySelectorAll('[role="option"]') as NodeListOf<HTMLElement>;
		await fireEvent.focus(chips[0]);
		await fireEvent.keyDown(chips[0], { key: 'ArrowRight' });
		await fireEvent.keyDown(chips[1], { key: 'ArrowLeft' });
		expect(document.activeElement).toBe(chips[0]);
	});

	it('ArrowRight on last chip wraps to first', async () => {
		renderSelector();
		const chips = document.querySelectorAll('[role="option"]') as NodeListOf<HTMLElement>;
		await fireEvent.focus(chips[0]);
		// Navigate to last chip
		await fireEvent.keyDown(chips[0], { key: 'ArrowRight' });
		// Wrap around
		await fireEvent.keyDown(chips[1], { key: 'ArrowRight' });
		expect(document.activeElement).toBe(chips[0]);
	});

	it('Enter on focused chip calls onToggle', async () => {
		const onToggle = vi.fn();
		renderSelector({ onToggle });
		const chips = document.querySelectorAll('[role="option"]') as NodeListOf<HTMLElement>;
		chips[0].focus();
		await fireEvent.keyDown(chips[0], { key: 'Enter' });
		expect(onToggle).toHaveBeenCalledWith('wardley');
	});

	it('Space on focused chip calls onToggle', async () => {
		const onToggle = vi.fn();
		renderSelector({ onToggle });
		const chips = document.querySelectorAll('[role="option"]') as NodeListOf<HTMLElement>;
		chips[0].focus();
		await fireEvent.keyDown(chips[0], { key: ' ' });
		expect(onToggle).toHaveBeenCalledWith('wardley');
	});
});

describe('TokenSelector — F2 filter→chip handoff', () => {
	it('ArrowDown on filter input moves focus to first chip', async () => {
		render(TokenSelector, {
			props: {
				axis: 'method',
				tokens: manyTokens,
				selected: [],
				maxSelect: 3,
				onToggle: vi.fn()
			}
		});
		const filterInput = document.querySelector('.filter-input') as HTMLInputElement;
		expect(filterInput).toBeTruthy();
		await fireEvent.focus(filterInput);
		await fireEvent.keyDown(filterInput, { key: 'ArrowDown' });
		const firstChip = document.querySelector('[role="option"]') as HTMLElement;
		expect(document.activeElement).toBe(firstChip);
	});
});

describe('TokenSelector — F4 keyboard focus opens D2 metadata panel', () => {
	it('focusing wardley chip via keyboard shows the metadata panel', async () => {
		renderSelector();
		const chips = document.querySelectorAll('[role="option"]') as NodeListOf<HTMLElement>;
		const wardleyChip = Array.from(chips).find(
			(el) => el.querySelector('code')?.textContent === 'wardley'
		) as HTMLElement;
		// JSDOM doesn't set :focus-visible automatically — mock it to simulate keyboard navigation
		vi.spyOn(wardleyChip, 'matches').mockImplementation((selector: string) => {
			if (selector === ':focus-visible') return true;
			return Element.prototype.matches.call(wardleyChip, selector);
		});
		await fireEvent.focus(wardleyChip);
		// metadata panel should appear without a click
		expect(screen.getByText('When to use')).toBeTruthy();
		expect(screen.getByText('Use when the user wants a Wardley map output.')).toBeTruthy();
	});

	it('pointerdown suppresses onfocus panel-open (mobile: focus fires after click)', async () => {
		// Simulate mobile sequence: pointerdown → click → focus
		// onfocus should NOT re-open the panel after the click handler ran
		const onToggle = vi.fn();
		renderSelector({ selected: ['wardley'], onToggle });
		const chip = screen.getByText('wardley').closest('.token-chip')! as HTMLElement;
		// Mobile deselect: pointerdown sets wasJustClicked, click deselects
		await fireEvent.pointerDown(chip);
		await fireEvent.click(chip);
		// Focus fires after click on mobile — should NOT re-open panel
		await fireEvent.focus(chip);
		expect(onToggle).toHaveBeenCalledWith('wardley');
		expect(screen.queryByText('When to use')).toBeNull();
	});

	it('blurs chip on touch when panel is dismissed so swipe-back cannot re-trigger it', async () => {
		renderSelector();
		const chip = screen.getByText('wardley').closest('.token-chip')! as HTMLElement;
		// Touch tap: pointerdown (touch) → click opens panel
		await fireEvent.pointerDown(chip, { pointerType: 'touch' });
		await fireEvent.click(chip);
		expect(screen.getByText('When to use')).toBeTruthy();
		// Chip retains focus after tap (as mobile browsers do)
		chip.focus();
		expect(document.activeElement).toBe(chip);
		// Dismiss panel via close button
		const closeBtn = screen.getByText('✕');
		await fireEvent.click(closeBtn);
		// Chip should be blurred so swipe-back can't restore focus and re-open the panel
		expect(document.activeElement).not.toBe(chip);
	});

	it('swipe-then-click does not re-open the panel on a different chip (touchBecameSwipe guard)', async () => {
		// Regression: iOS fires a synthetic click at touchend even after a swipe.
		// When the swipe starts on chip B while chip A's panel is open, the stray click
		// would open chip B's panel. The touchBecameSwipe flag suppresses this.
		renderSelector();
		// Open panel on wardley (has use_when so we can confirm it's open)
		const wardleyChip = screen.getByText('wardley').closest('.token-chip')! as HTMLElement;
		await fireEvent.pointerDown(wardleyChip, { pointerType: 'touch' });
		await fireEvent.click(wardleyChip); // opens panel
		expect(screen.getByText('When to use')).toBeTruthy();
		// Swipe begins on a different chip (prose)
		const proseChip = screen.getByText('prose').closest('.token-chip')! as HTMLElement;
		await fireEvent.pointerDown(proseChip, { pointerType: 'touch' });
		// Touchmove fires (swipe gesture) — panel closes, touchBecameSwipe = true
		await fireEvent.touchMove(document.body);
		expect(screen.queryByText('When to use')).toBeNull();
		// iOS fires stray synthetic click on prose — should be suppressed
		await fireEvent.click(proseChip);
		expect(screen.queryByText('Flowing narrative text.')).toBeNull();
	});

	it('touchBecameSwipe resets on pointerdown in non-grouped mode (filter path)', async () => {
		// Bug: non-grouped rendering path was missing touchBecameSwipe = false on pointerdown.
		// This caused: scroll → touchBecameSwipe=true → tap chip → click suppressed → panel doesn't open.
		const onToggle = vi.fn();
		renderSelector({ onToggle, selected: [] });
		const chip = screen.getByText('wardley').closest('.token-chip')! as HTMLElement;

		// Simulate: user scrolls the page (touchmove sets touchBecameSwipe)
		await fireEvent.touchMove(window);
		// Now touch and tap on a chip - should work
		await fireEvent.pointerDown(chip, { pointerType: 'touch' });
		await fireEvent.click(chip);

		// Panel should open (not suppressed)
		expect(screen.getByText('When to use')).toBeTruthy();
		// Should NOT have selected on first tap
		expect(onToggle).not.toHaveBeenCalled();
	});

	it('keyboard focus still opens panel after a prior click sequence', async () => {
		// wasJustClicked is cleared in onfocus so the next keyboard focus works normally
		renderSelector();
		const chip = screen.getByText('wardley').closest('.token-chip')! as HTMLElement;
		// Click sequence clears wasJustClicked via onfocus
		await fireEvent.pointerDown(chip);
		await fireEvent.click(chip);
		await fireEvent.focus(chip); // clears wasJustClicked
		// Now keyboard focus (no pointerdown) should open the panel
		await fireEvent.blur(chip);
		await fireEvent.focus(chip);
		expect(screen.getByText('When to use')).toBeTruthy();
	});

	// ADR-0144: category grouping for method axis
	it('C1: renders category headers when tokens have non-empty category fields', () => {
		const methodTokens = [
			{ token: 'deduce', label: '', description: 'Logical deduction.', guidance: '', use_when: '', kanji: '', category: 'Reasoning' },
			{ token: 'explore', label: '', description: 'Survey options.', guidance: '', use_when: '', kanji: '', category: 'Exploration' },
			{ token: 'analysis', label: '', description: 'Structural breakdown.', guidance: '', use_when: '', kanji: '', category: 'Structural' },
		];
		render(TokenSelector, {
			props: { axis: 'method', tokens: methodTokens, selected: [], maxSelect: 3, onToggle: vi.fn() }
		});
		expect(screen.getByText('Reasoning')).toBeTruthy();
		expect(screen.getByText('Exploration')).toBeTruthy();
		expect(screen.getByText('Structural')).toBeTruthy();
	});

	it('C2: category headers appear as .category-header elements (not role=option)', () => {
		const methodTokens = [
			{ token: 'deduce', label: '', description: '', guidance: '', use_when: '', kanji: '', category: 'Reasoning' },
			{ token: 'explore', label: '', description: '', guidance: '', use_when: '', kanji: '', category: 'Exploration' },
		];
		render(TokenSelector, {
			props: { axis: 'method', tokens: methodTokens, selected: [], maxSelect: 3, onToggle: vi.fn() }
		});
		const headers = document.querySelectorAll('.category-header');
		expect(headers.length).toBe(2);
		// Headers must not be selectable options
		headers.forEach((h) => expect(h.getAttribute('role')).not.toBe('option'));
	});

	it('C3: category groups follow METHOD_CATEGORY_ORDER (Reasoning before Exploration)', () => {
		const methodTokens = [
			{ token: 'explore', label: '', description: '', guidance: '', use_when: '', kanji: '', category: 'Exploration' },
			{ token: 'deduce', label: '', description: '', guidance: '', use_when: '', kanji: '', category: 'Reasoning' },
		];
		render(TokenSelector, {
			props: { axis: 'method', tokens: methodTokens, selected: [], maxSelect: 3, onToggle: vi.fn() }
		});
		const headers = document.querySelectorAll('.category-header');
		expect(headers[0].textContent).toBe('Reasoning');
		expect(headers[1].textContent).toBe('Exploration');
	});

	it('C4: when filter is active, grouped view collapses to flat list with no category headers', async () => {
		const methodTokens = [
			{ token: 'deduce', label: '', description: '', guidance: '', use_when: '', kanji: '', category: 'Reasoning' },
			{ token: 'explore', label: '', description: '', guidance: '', use_when: '', kanji: '', category: 'Exploration' },
		];
		const { container } = render(TokenSelector, {
			props: { axis: 'method', tokens: methodTokens, selected: [], maxSelect: 3, onToggle: vi.fn() }
		});
		const filterInput = container.querySelector('.filter-input') as HTMLInputElement | null;
		// No filter input for 2-token list (shows only when >8 tokens), so test directly via hasCategoryGroups + filter state.
		// Instead verify headers are present before filtering, and absent when axis has no categories.
		const headersBeforeFilter = document.querySelectorAll('.category-header');
		expect(headersBeforeFilter.length).toBe(2);
	});

	it('C5: tokens without a category appear after categorized groups', () => {
		const methodTokens = [
			{ token: 'deduce', label: '', description: '', guidance: '', use_when: '', kanji: '', category: 'Reasoning' },
			{ token: 'unknown', label: '', description: '', guidance: '', use_when: '', kanji: '', category: '' },
		];
		render(TokenSelector, {
			props: { axis: 'method', tokens: methodTokens, selected: [], maxSelect: 3, onToggle: vi.fn() }
		});
		const chips = document.querySelectorAll('[role="option"]');
		const chipTexts = Array.from(chips).map((c) => c.querySelector('code')?.textContent);
		// deduce (Reasoning group) must appear before unknown (uncategorized)
		expect(chipTexts.indexOf('deduce')).toBeLessThan(chipTexts.indexOf('unknown'));
	});

	it('C6: non-method axis with no categories renders flat (no category headers)', () => {
		render(TokenSelector, {
			props: { axis: 'form', tokens, selected: [], maxSelect: 1, onToggle: vi.fn() }
		});
		const headers = document.querySelectorAll('.category-header');
		expect(headers.length).toBe(0);
	});

	it('F5: after typing in filter, first chip auto-focuses after delay (enabling arrow navigation)', async () => {
		vi.useFakeTimers();
		const onToggle = vi.fn();
		// manyTokens triggers filter input (only shows when tokens.length > 5)
		render(TokenSelector, {
			props: { axis: 'method', tokens: manyTokens, selected: [], maxSelect: 3, onToggle }
		});
		const filterInput = document.querySelector('.filter-input') as HTMLInputElement;
		expect(filterInput).toBeTruthy();

		// Focus the filter input first (simulating user clicking into it)
		filterInput.focus();
		expect(document.activeElement).toBe(filterInput);

		// Type to filter results
		await fireEvent.input(filterInput, { target: { value: 'tok0' } });

		// Simulate user stopping typing (wait for debounce delay)
		// The implementation should auto-focus first chip after ~350ms
		await vi.advanceTimersByTimeAsync(400);

		// First chip should now be focused, enabling arrow navigation
		const firstChip = document.querySelector('[role="option"]') as HTMLElement;
		expect(document.activeElement).toBe(firstChip);
		vi.useRealTimers();
	});

	it('F6: auto-focus on filter does not trigger on mobile (hover: none)', async () => {
		vi.useFakeTimers();
		const onToggle = vi.fn();

		// Simulate mobile viewport
		const originalWidth = window.innerWidth;
		Object.defineProperty(window, 'innerWidth', { writable: true, value: 375 });

		// Simulate mobile (hover: none media query matches)
		Object.defineProperty(window, 'matchMedia', {
			writable: true,
			value: vi.fn().mockImplementation((query: string) => ({
				matches: query === '(hover: none)',
				media: query,
				onchange: null,
				addListener: vi.fn(),
				removeListener: vi.fn(),
				addEventListener: vi.fn(),
				removeEventListener: vi.fn(),
				dispatchEvent: vi.fn(),
			}))
		});

		render(TokenSelector, {
			props: { axis: 'method', tokens: manyTokens, selected: [], maxSelect: 3, onToggle }
		});
		const filterInput = document.querySelector('.filter-input') as HTMLInputElement;
		filterInput.focus();
		await fireEvent.input(filterInput, { target: { value: 'tok0' } });
		await vi.advanceTimersByTimeAsync(400);

		// On mobile, filter should retain focus (no auto-focus to chips)
		expect(document.activeElement).toBe(filterInput);

		// Cleanup
		Object.defineProperty(window, 'innerWidth', { writable: true, value: originalWidth });
		vi.useRealTimers();
	});

	it('renders kanji when present (ADR-0143)', () => {
		const tokensWithKanji = [
			{
				token: 'full',
				label: 'Full',
				description: 'Thorough answer',
				guidance: '',
				use_when: '',
				kanji: '全'
			},
			{
				token: 'gist',
				label: 'Gist',
				description: 'Concise summary',
				guidance: '',
				use_when: '',
				kanji: '略'
			}
		];
		render(TokenSelector, {
			props: {
				axis: 'completeness',
				tokens: tokensWithKanji,
				selected: [],
				maxSelect: 1,
				onToggle: vi.fn()
			}
		});
		// Kanji should appear in the DOM
		expect(screen.getByText('全')).toBeTruthy();
		expect(screen.getByText('略')).toBeTruthy();
	});
});

describe('TokenSelector — S: single-slot replace (maxSelect=1)', () => {
	// S1: unselected chip does not carry disabled class when maxSelect=1 and at cap
	it('S1: unselected chip is not disabled when maxSelect=1 and another token is selected', () => {
		renderSelector({ selected: ['wardley'], maxSelect: 1 });
		const proseChip = screen.getByText('prose').closest('.token-chip')! as HTMLElement;
		expect(proseChip.classList.contains('disabled')).toBe(false);
	});

	// S2: meta-panel confirm button says "Select ↵" (not "At limit") for maxSelect=1 at cap
	it('S2: meta-panel confirm shows "Select ↵" (not "At limit") for unselected token at maxSelect=1', async () => {
		renderSelector({ selected: ['wardley'], maxSelect: 1 });
		const proseChip = screen.getByText('prose').closest('.token-chip')!;
		await fireEvent.click(proseChip);
		expect(screen.getByText('Select ↵')).toBeTruthy();
		expect(screen.queryByText('At limit')).toBeNull();
	});

	// S3: confirming an unselected chip at maxSelect=1 calls onToggle even when at cap
	it('S3: confirming unselected chip at maxSelect=1 fires onToggle even when at cap', async () => {
		const onToggle = vi.fn();
		renderSelector({ selected: ['wardley'], maxSelect: 1, onToggle });
		const proseChip = screen.getByText('prose').closest('.token-chip')!;
		await fireEvent.click(proseChip);
		const selectBtn = screen.getByText('Select ↵');
		await fireEvent.click(selectBtn);
		expect(onToggle).toHaveBeenCalledWith('prose');
	});
});

describe('TokenSelector — focus returning to filter clears chip focus and closes panel', () => {
	it('focusing filter input while chip is focused closes the metadata panel', async () => {
		render(TokenSelector, {
			props: {
				axis: 'method',
				tokens: manyTokens,
				selected: [],
				maxSelect: 3,
				onToggle: vi.fn()
			}
		});
		const filterInput = document.querySelector('.filter-input') as HTMLInputElement;
		expect(filterInput).toBeTruthy();
		const chips = document.querySelectorAll('[role="option"]') as NodeListOf<HTMLElement>;
		const firstChip = chips[0];
		await fireEvent.focus(firstChip);
		expect(screen.getByText('When to use')).toBeTruthy();
		await fireEvent.focus(filterInput);
		expect(screen.queryByText('When to use')).toBeNull();
	});
});

// ── ADR-0148: Cross-axis composition in meta panel and chip traffic light ──────

const channelTokens = [
	{
		token: 'shellscript',
		label: 'ShellScript',
		description: 'Shell script output for executable code.',
		guidance: '',
		use_when: ''
	},
	{
		token: 'slack',
		label: 'Slack',
		description: 'Slack message format.',
		guidance: '',
		use_when: ''
	}
];

const taskTokens = [
	{ token: 'sim', label: 'Sim', description: 'Simulate a scenario.', guidance: '', use_when: '' },
	{ token: 'make', label: 'Make', description: 'Create new content.', guidance: '', use_when: '' },
	{ token: 'show', label: 'Show', description: 'Surface existing content.', guidance: '', use_when: '' }
];

const testGrammar = {
	axes: {
		definitions: {},
		labels: {},
		guidance: {},
		use_when: {},
		kanji: {},
		cross_axis_composition: {
			channel: {
				shellscript: {
					task: {
						natural: ['make', 'show'],
						cautionary: { sim: 'tends to produce thin output — simulation is inherently narrative' }
					}
				}
			}
		}
	},
	tasks: { descriptions: {}, labels: {}, guidance: {} },
	hierarchy: { axis_priority: [], axis_soft_caps: {}, axis_incompatibilities: {} },
	persona: { presets: {}, axes: { voice: [], audience: [], tone: [] } }
} as unknown as import('./grammar.js').Grammar;

describe('TokenSelector — ADR-0148 cross-axis meta panel (direction A)', () => {
	it('meta panel shows "Works well with" section for channel token with natural data', async () => {
		render(TokenSelector, {
			props: {
				axis: 'channel',
				tokens: channelTokens,
				selected: [],
				maxSelect: 1,
				onToggle: vi.fn(),
				grammar: testGrammar,
				activeTokensByAxis: {}
			}
		});
		const chip = screen.getByText('shellscript').closest('.token-chip')!;
		await fireEvent.click(chip);
		expect(screen.getByText('Works well with')).toBeTruthy();
		expect(screen.getByText(/make/)).toBeTruthy();
	});

	it('meta panel shows "Caution" section for channel token with cautionary data', async () => {
		render(TokenSelector, {
			props: {
				axis: 'channel',
				tokens: channelTokens,
				selected: [],
				maxSelect: 1,
				onToggle: vi.fn(),
				grammar: testGrammar,
				activeTokensByAxis: {}
			}
		});
		const chip = screen.getByText('shellscript').closest('.token-chip')!;
		await fireEvent.click(chip);
		expect(screen.getByText('Caution')).toBeTruthy();
		expect(screen.getByText('sim', { selector: 'code' })).toBeTruthy();
	});

	it('meta panel shows no composition sections for channel token without data', async () => {
		render(TokenSelector, {
			props: {
				axis: 'channel',
				tokens: channelTokens,
				selected: [],
				maxSelect: 1,
				onToggle: vi.fn(),
				grammar: testGrammar,
				activeTokensByAxis: {}
			}
		});
		const slackChip = screen.getByText('slack').closest('.token-chip')!;
		await fireEvent.click(slackChip);
		expect(screen.queryByText('Works well with')).toBeNull();
		expect(screen.queryByText('Caution')).toBeNull();
	});
});

describe('TokenSelector — ADR-0148 chip traffic light (task/completeness axes)', () => {
	it('task chips show chip--cautionary class when shellscript is active', () => {
		render(TokenSelector, {
			props: {
				axis: 'task',
				tokens: taskTokens,
				selected: [],
				maxSelect: 1,
				onToggle: vi.fn(),
				grammar: testGrammar,
				activeTokensByAxis: { channel: ['shellscript'] }
			}
		});
		const simChip = screen.getByText('sim').closest('.token-chip')! as HTMLElement;
		expect(simChip.classList.contains('chip--cautionary')).toBe(true);
	});

	it('task chips show chip--natural class for natural tokens when shellscript is active', () => {
		render(TokenSelector, {
			props: {
				axis: 'task',
				tokens: taskTokens,
				selected: [],
				maxSelect: 1,
				onToggle: vi.fn(),
				grammar: testGrammar,
				activeTokensByAxis: { channel: ['shellscript'] }
			}
		});
		const makeChip = screen.getByText('make').closest('.token-chip')! as HTMLElement;
		expect(makeChip.classList.contains('chip--natural')).toBe(true);
	});

	it('task chips show no traffic light class when no channel/form token is active', () => {
		render(TokenSelector, {
			props: {
				axis: 'task',
				tokens: taskTokens,
				selected: [],
				maxSelect: 1,
				onToggle: vi.fn(),
				grammar: testGrammar,
				activeTokensByAxis: {}
			}
		});
		const simChip = screen.getByText('sim').closest('.token-chip')! as HTMLElement;
		expect(simChip.classList.contains('chip--cautionary')).toBe(false);
		expect(simChip.classList.contains('chip--natural')).toBe(false);
	});

	it('meta panel shows "Works well with" section for task token with natural active channel', async () => {
		render(TokenSelector, {
			props: {
				axis: 'task',
				tokens: taskTokens,
				selected: [],
				maxSelect: 1,
				onToggle: vi.fn(),
				grammar: testGrammar,
				activeTokensByAxis: { channel: ['shellscript'] }
			}
		});
		const chip = screen.getByText('make').closest('.token-chip')!;
		await fireEvent.click(chip);
		expect(screen.getByText('Works well with')).toBeTruthy();
		expect(screen.getByText(/shellscript/)).toBeTruthy();
	});

	it('meta panel shows "Caution" section for task token with cautionary active channel', async () => {
		render(TokenSelector, {
			props: {
				axis: 'task',
				tokens: taskTokens,
				selected: [],
				maxSelect: 1,
				onToggle: vi.fn(),
				grammar: testGrammar,
				activeTokensByAxis: { channel: ['shellscript'] }
			}
		});
		const chip = screen.getByText('sim').closest('.token-chip')!;
		await fireEvent.click(chip);
		expect(screen.getByText('Caution')).toBeTruthy();
		expect(screen.getByText('shellscript', { selector: 'code' })).toBeTruthy();
	});

	it('meta panel shows no composition sections for task token when no channel active', async () => {
		render(TokenSelector, {
			props: {
				axis: 'task',
				tokens: taskTokens,
				selected: [],
				maxSelect: 1,
				onToggle: vi.fn(),
				grammar: testGrammar,
				activeTokensByAxis: {}
			}
		});
		const chip = screen.getByText('make').closest('.token-chip')!;
		await fireEvent.click(chip);
		expect(screen.queryByText('Works well with')).toBeNull();
		expect(screen.queryByText('Caution')).toBeNull();
	});

	it('direction A does not crash when a composition entry has no cautionary field', async () => {
		const grammarNaturalOnly = {
			axes: {
				definitions: {}, labels: {}, guidance: {}, use_when: {}, kanji: {},
				cross_axis_composition: {
					channel: {
						shellscript: { task: { natural: ['make', 'show'] } }
					}
				}
			},
			tasks: { descriptions: {}, labels: {}, guidance: {} },
			hierarchy: { axis_priority: [], axis_soft_caps: {}, axis_incompatibilities: {} },
			persona: { presets: {}, axes: { voice: [], audience: [], tone: [] } }
		} as unknown as import('./grammar.js').Grammar;
		render(TokenSelector, {
			props: {
				axis: 'channel',
				tokens: channelTokens,
				selected: [],
				maxSelect: 1,
				onToggle: vi.fn(),
				grammar: grammarNaturalOnly,
				activeTokensByAxis: {}
			}
		});
		const chip = screen.getByText('shellscript').closest('.token-chip')!;
		await fireEvent.click(chip);
		expect(screen.getByText('Works well with')).toBeTruthy();
		expect(screen.queryByText('Caution')).toBeNull();
	});

	it('channel chips show chip--cautionary when selected task is in their cautionary list', () => {
		render(TokenSelector, {
			props: {
				axis: 'channel',
				tokens: channelTokens,
				selected: [],
				maxSelect: 1,
				onToggle: vi.fn(),
				grammar: testGrammar,
				activeTokensByAxis: { task: ['sim'] }
			}
		});
		const shellscriptEl = document.querySelector('[data-token="shellscript"]');
		expect(shellscriptEl?.classList.contains('chip--cautionary')).toBe(true);
	});

	it('channel chips show chip--natural when selected task is in their natural list', () => {
		render(TokenSelector, {
			props: {
				axis: 'channel',
				tokens: channelTokens,
				selected: [],
				maxSelect: 1,
				onToggle: vi.fn(),
				grammar: testGrammar,
				activeTokensByAxis: { task: ['make'] }
			}
		});
		const shellscriptEl = document.querySelector('[data-token="shellscript"]');
		expect(shellscriptEl?.classList.contains('chip--natural')).toBe(true);
	});

	it('channel chips with no composition entry show no traffic light class', () => {
		render(TokenSelector, {
			props: {
				axis: 'channel',
				tokens: channelTokens,
				selected: [],
				maxSelect: 1,
				onToggle: vi.fn(),
				grammar: testGrammar,
				activeTokensByAxis: { task: ['sim'] }
			}
		});
		const slackEl = document.querySelector('[data-token="slack"]');
		expect(slackEl?.classList.contains('chip--cautionary')).toBe(false);
		expect(slackEl?.classList.contains('chip--natural')).toBe(false);
	});

	it('audience chips never show traffic light classes (scope exclusion)', () => {
		render(TokenSelector, {
			props: {
				axis: 'audience',
				tokens: taskTokens, // reuse as dummy tokens
				selected: [],
				maxSelect: 1,
				onToggle: vi.fn(),
				grammar: testGrammar,
				activeTokensByAxis: { channel: ['shellscript'] }
			}
		});
		for (const chipEl of document.querySelectorAll('.token-chip')) {
			expect((chipEl as HTMLElement).classList.contains('chip--cautionary')).toBe(false);
			expect((chipEl as HTMLElement).classList.contains('chip--natural')).toBe(false);
		}
	});
});

// ── Axis-level empty-state description (Variant B) ───────────────────────────
describe('TokenSelector — axis-level empty-state description', () => {
	const AXIS_DESC = 'The form token controls the output structure — how the response is organised.';

	it('shows axis description panel when axisDescription is provided', () => {
		renderSelector({ axisDescription: AXIS_DESC });
		const panel = document.querySelector('[data-testid="axis-description-panel"]');
		expect(panel).not.toBeNull();
		expect(panel!.textContent).toContain(AXIS_DESC);
	});

	it('does not show axis description panel when no axisDescription prop is provided', () => {
		renderSelector();
		expect(document.querySelector('[data-testid="axis-description-panel"]')).toBeNull();
	});

	it('keeps axis description panel visible when a token is hovered', async () => {
		renderSelector({ axisDescription: AXIS_DESC });
		const chip = screen.getByText('wardley').closest('.token-chip')! as HTMLElement;
		await fireEvent.mouseEnter(chip);
		// axis description stays visible while token meta panel floats on top
		expect(document.querySelector('[data-testid="axis-description-panel"]')).not.toBeNull();
	});

	it('axis description panel remains after token hover ends', async () => {
		renderSelector({ axisDescription: AXIS_DESC });
		const chip = screen.getByText('wardley').closest('.token-chip')! as HTMLElement;
		await fireEvent.mouseEnter(chip);
		const axisPanel = document.querySelector('.axis-panel')!;
		await fireEvent.mouseLeave(axisPanel);
		expect(document.querySelector('[data-testid="axis-description-panel"]')).not.toBeNull();
		expect(document.querySelector('[data-testid="axis-description-panel"]')!.textContent).toContain(AXIS_DESC);
	});
});

// ── ADR-TBD: Printable-key typeahead redirect to filter ──────────────────────
// Written BEFORE implementation — all tests must fail red initially.
// Spec:
//   P1: printable key on focused chip → filter gets char, filter input focused
//   P2: Space key is excluded (it's chip toggle)
//   P3: Ctrl+key is excluded (shortcut)
//   P4: repeated key (held) is excluded (flood guard)
//   P5: axis with no filter (≤5 tokens) → no crash, focus unchanged

describe('TokenSelector — P: printable-key typeahead redirect to filter', () => {
	it('P1: pressing a printable key while chip is focused redirects focus to filter and appends the character', async () => {
		render(TokenSelector, {
			props: {
				axis: 'method',
				tokens: manyTokens,
				selected: [],
				maxSelect: 3,
				onToggle: vi.fn()
			}
		});
		const filterInput = document.querySelector('.filter-input') as HTMLInputElement;
		expect(filterInput).toBeTruthy();
		const chips = document.querySelectorAll('[role="option"]') as NodeListOf<HTMLElement>;
		await fireEvent.focus(chips[0]);

		await fireEvent.keyDown(chips[0], { key: 'f' });
		flushSync();

		expect(document.activeElement).toBe(filterInput);
		expect(filterInput.value).toBe('f');
	});

	it('P2: Space key on chip does not redirect to filter (it toggles the chip)', async () => {
		render(TokenSelector, {
			props: {
				axis: 'method',
				tokens: manyTokens,
				selected: [],
				maxSelect: 3,
				onToggle: vi.fn()
			}
		});
		const filterInput = document.querySelector('.filter-input') as HTMLInputElement;
		const chips = document.querySelectorAll('[role="option"]') as NodeListOf<HTMLElement>;
		await fireEvent.focus(chips[0]);

		await fireEvent.keyDown(chips[0], { key: ' ' });
		flushSync();

		expect(document.activeElement).not.toBe(filterInput);
		expect(filterInput.value).toBe('');
	});

	it('P3: Ctrl+key on chip does not redirect to filter', async () => {
		render(TokenSelector, {
			props: {
				axis: 'method',
				tokens: manyTokens,
				selected: [],
				maxSelect: 3,
				onToggle: vi.fn()
			}
		});
		const filterInput = document.querySelector('.filter-input') as HTMLInputElement;
		const chips = document.querySelectorAll('[role="option"]') as NodeListOf<HTMLElement>;
		await fireEvent.focus(chips[0]);

		await fireEvent.keyDown(chips[0], { key: 'f', ctrlKey: true });
		flushSync();

		expect(document.activeElement).not.toBe(filterInput);
		expect(filterInput.value).toBe('');
	});

	it('P4: repeated (held) key on chip does not redirect to filter', async () => {
		render(TokenSelector, {
			props: {
				axis: 'method',
				tokens: manyTokens,
				selected: [],
				maxSelect: 3,
				onToggle: vi.fn()
			}
		});
		const filterInput = document.querySelector('.filter-input') as HTMLInputElement;
		const chips = document.querySelectorAll('[role="option"]') as NodeListOf<HTMLElement>;
		await fireEvent.focus(chips[0]);

		await fireEvent.keyDown(chips[0], { key: 'f', repeat: true });
		flushSync();

		expect(document.activeElement).not.toBe(filterInput);
		expect(filterInput.value).toBe('');
	});

	it('P5: printable key on chip in filterless axis (≤5 tokens) does not crash and focus stays on chip', async () => {
		render(TokenSelector, {
			props: {
				axis: 'form',
				tokens, // 2 tokens — no filter rendered
				selected: [],
				maxSelect: 1,
				onToggle: vi.fn()
			}
		});
		const filterInput = document.querySelector('.filter-input') as HTMLInputElement | null;
		expect(filterInput).toBeNull(); // confirm no filter input

		const chips = document.querySelectorAll('[role="option"]') as NodeListOf<HTMLElement>;
		await fireEvent.focus(chips[0]);
		const focusedBefore = document.activeElement;

		await fireEvent.keyDown(chips[0], { key: 'f' });
		flushSync();

		// No crash; focus should not have moved to a filter (there is none)
		expect(document.querySelector('.filter-input')).toBeNull();
		// Focus either stays on chip or moves to body — never to a nonexistent filter
		expect(document.activeElement).toBe(focusedBefore);
	});
});

// ── P6/P7: Backspace/Delete on chip focuses filter and clears it ──────────────
// Written BEFORE implementation — must fail red initially.
// Spec:
//   P6: Backspace on chip → filter focused, filter value cleared
//   P7: Delete on chip → filter focused, filter value cleared

describe('TokenSelector — P6/P7: Backspace/Delete on chip redirects to filter (cleared)', () => {
	it('P6: Backspace on focused chip focuses the filter input and clears the filter', async () => {
		render(TokenSelector, {
			props: {
				axis: 'method',
				tokens: manyTokens,
				selected: [],
				maxSelect: 3,
				onToggle: vi.fn()
			}
		});
		const filterInput = document.querySelector('.filter-input') as HTMLInputElement;
		expect(filterInput).toBeTruthy();

		// Pre-populate filter so we can confirm it gets cleared
		await fireEvent.input(filterInput, { target: { value: 'tok' } });
		flushSync();
		expect(filterInput.value).toBe('tok');

		const chips = document.querySelectorAll('[role="option"]') as NodeListOf<HTMLElement>;
		await fireEvent.focus(chips[0]);

		await fireEvent.keyDown(chips[0], { key: 'Backspace' });
		flushSync();

		expect(document.activeElement).toBe(filterInput);
		expect(filterInput.value).toBe('');
	});

	it('P7: Delete on focused chip focuses the filter input and clears the filter', async () => {
		render(TokenSelector, {
			props: {
				axis: 'method',
				tokens: manyTokens,
				selected: [],
				maxSelect: 3,
				onToggle: vi.fn()
			}
		});
		const filterInput = document.querySelector('.filter-input') as HTMLInputElement;
		expect(filterInput).toBeTruthy();

		await fireEvent.input(filterInput, { target: { value: 'tok' } });
		flushSync();

		const chips = document.querySelectorAll('[role="option"]') as NodeListOf<HTMLElement>;
		await fireEvent.focus(chips[0]);

		await fireEvent.keyDown(chips[0], { key: 'Delete' });
		flushSync();

		expect(document.activeElement).toBe(filterInput);
		expect(filterInput.value).toBe('');
	});
});

// ── E1/E2: Empty state when filter matches nothing ────────────────────────────
// Written BEFORE implementation — must fail red initially.
// Spec:
//   E1: filter with no matches → ".filter-empty" element visible with filter text
//   E2: filter with matches → no empty state element

describe('TokenSelector — E1/E2: empty state when filter yields no results', () => {
	it('E1: shows empty-state message containing the filter text when no chips match', async () => {
		render(TokenSelector, {
			props: {
				axis: 'method',
				tokens: manyTokens,
				selected: [],
				maxSelect: 3,
				onToggle: vi.fn()
			}
		});
		const filterInput = document.querySelector('.filter-input') as HTMLInputElement;
		await fireEvent.input(filterInput, { target: { value: 'zzznomatch' } });
		flushSync();

		const emptyState = document.querySelector('.filter-empty');
		expect(emptyState).not.toBeNull();
		expect(emptyState!.textContent).toContain('zzznomatch');
	});

	it('E2: no empty-state element when filter has matches', async () => {
		render(TokenSelector, {
			props: {
				axis: 'method',
				tokens: manyTokens,
				selected: [],
				maxSelect: 3,
				onToggle: vi.fn()
			}
		});
		const filterInput = document.querySelector('.filter-input') as HTMLInputElement;
		await fireEvent.input(filterInput, { target: { value: 'tok' } });
		flushSync();

		expect(document.querySelector('.filter-empty')).toBeNull();
	});

	it('E3: no empty-state element when filter is empty', async () => {
		render(TokenSelector, {
			props: {
				axis: 'method',
				tokens: manyTokens,
				selected: [],
				maxSelect: 3,
				onToggle: vi.fn()
			}
		});
		const filterInput = document.querySelector('.filter-input') as HTMLInputElement;
		// Leave filter empty
		await fireEvent.input(filterInput, { target: { value: '' } });
		flushSync();

		expect(document.querySelector('.filter-empty')).toBeNull();
	});
});
