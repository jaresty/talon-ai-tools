import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/svelte';
import TokenSelector from './TokenSelector.svelte';

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
		// Use fireEvent.focus so Svelte processes the onfocus handler reactively
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
