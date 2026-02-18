/**
 * F5 specifying validation — ADR-0135
 *
 * Selected-chip badges in +page.svelte must be keyboard-focusable and
 * activatable via Enter/Space. Because the badge markup lives inline in
 * +page.svelte (not an extracted component), we test the DOM contract
 * by rendering a minimal fixture that replicates the badge element and
 * asserting the required attributes and event behaviour.
 */
import { describe, it, expect, vi } from 'vitest';
import { render, fireEvent } from '@testing-library/svelte';
import SelectedChipFixture from './SelectedChipFixture.svelte';

describe('TokenSelector — F5 selected-chip badge keyboard accessibility', () => {
	it('selected-chip badge has tabindex="0"', () => {
		render(SelectedChipFixture, { props: { token: 'show', onRemove: vi.fn() } });
		const badge = document.querySelector('.selected-chip')!;
		expect(badge.getAttribute('tabindex')).toBe('0');
	});

	it('selected-chip badge has role="button"', () => {
		render(SelectedChipFixture, { props: { token: 'show', onRemove: vi.fn() } });
		const badge = document.querySelector('.selected-chip')!;
		expect(badge.getAttribute('role')).toBe('button');
	});

	it('Enter on selected-chip badge calls onRemove', async () => {
		const onRemove = vi.fn();
		render(SelectedChipFixture, { props: { token: 'show', onRemove } });
		const badge = document.querySelector('.selected-chip')! as HTMLElement;
		await fireEvent.focus(badge);
		await fireEvent.keyDown(badge, { key: 'Enter' });
		expect(onRemove).toHaveBeenCalledWith('show');
	});

	it('Space on selected-chip badge calls onRemove', async () => {
		const onRemove = vi.fn();
		render(SelectedChipFixture, { props: { token: 'show', onRemove } });
		const badge = document.querySelector('.selected-chip')! as HTMLElement;
		await fireEvent.keyDown(badge, { key: ' ' });
		expect(onRemove).toHaveBeenCalledWith('show');
	});
});
