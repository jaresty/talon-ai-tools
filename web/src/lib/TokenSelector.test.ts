import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/svelte';
import TokenSelector from './TokenSelector.svelte';

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

	it('clicking the same chip again closes the panel', async () => {
		renderSelector();
		const chip = screen.getByText('wardley').closest('.token-chip')!;
		await fireEvent.click(chip); // open
		await fireEvent.click(chip); // close
		expect(screen.queryByText('When to use')).toBeNull();
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

	it('clicking chip calls onToggle', async () => {
		const onToggle = vi.fn();
		renderSelector({ onToggle });
		const chip = screen.getByText('wardley').closest('.token-chip')!;
		await fireEvent.click(chip);
		expect(onToggle).toHaveBeenCalledWith('wardley');
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
