import { flushSync } from 'svelte';
import { mount } from 'svelte';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import TokenSelector from '$lib/TokenSelector.svelte';

describe('TokenSelector — Mobile Meta Panel Accessibility', () => {
	let container: HTMLDivElement;

	beforeEach(() => {
		vi.clearAllMocks();
		container = document.createElement('div');
		document.body.appendChild(container);
	});

	const tokens = [
		{ token: 'show', label: 'Explain', description: 'Explain or describe', use_when: 'Use when explaining', guidance: 'Follow best practices' },
		{ token: 'make', label: 'Create', description: 'Create new content', use_when: 'Use when creating', guidance: 'Tips here' }
	];

	it('meta-panel shows use_when when token is clicked', () => {
		mount(TokenSelector, {
			target: container,
			props: {
				axis: 'task',
				tokens,
				selected: [],
				maxSelect: 1,
				onToggle: vi.fn()
			}
		});
		
		const tokenChip = container.querySelector('.token-chip');
		expect(tokenChip).toBeTruthy();
		
		(tokenChip as HTMLElement).click();
		flushSync();
		
		const metaPanel = container.querySelector('.meta-panel');
		expect(metaPanel).toBeTruthy();
		const useWhenText = metaPanel?.textContent || '';
		expect(useWhenText).toContain('When to use');
	});

	it('meta-panel shows description and guidance text', () => {
		mount(TokenSelector, {
			target: container,
			props: {
				axis: 'task',
				tokens,
				selected: [],
				maxSelect: 1,
				onToggle: vi.fn()
			}
		});
		
		const tokenChip = container.querySelector('.token-chip');
		(tokenChip as HTMLElement).click();
		flushSync();
		
		const metaPanel = container.querySelector('.meta-panel');
		const panelText = metaPanel?.textContent || '';
		
		expect(panelText).toContain('Explain or describe');
		expect(panelText).toContain('When to use');
		expect(panelText).toContain('Use when explaining');
	});

	it('meta-panel appears when a token chip is clicked', () => {
		mount(TokenSelector, {
			target: container,
			props: {
				axis: 'task',
				tokens,
				selected: [],
				maxSelect: 1,
				onToggle: vi.fn()
			}
		});

		// No panel before any chip is clicked
		expect(container.querySelector('.meta-panel')).toBeNull();

		const tokenChip = container.querySelector('.token-chip');
		(tokenChip as HTMLElement).click();
		flushSync();

		// Panel present when guidance drawer is open
		expect(container.querySelector('.meta-panel')).toBeTruthy();
	});

	it('no backdrop element (removed to allow token chip clicks through)', () => {
		mount(TokenSelector, {
			target: container,
			props: {
				axis: 'task',
				tokens,
				selected: [],
				maxSelect: 1,
				onToggle: vi.fn()
			}
		});

		const tokenChip = container.querySelector('.token-chip');
		(tokenChip as HTMLElement).click();
		flushSync();

		// Backdrop removed: it intercepted chip clicks on mobile (onfocus fires before click,
		// backdrop appears at z-index 190, then synthetic click lands on backdrop not chip)
		expect(container.querySelector('.meta-backdrop')).toBeNull();
	});

	it('meta-panel can be closed via close button', () => {
		mount(TokenSelector, {
			target: container,
			props: {
				axis: 'task',
				tokens,
				selected: [],
				maxSelect: 1,
				onToggle: vi.fn()
			}
		});
		
		const tokenChip = container.querySelector('.token-chip');
		(tokenChip as HTMLElement).click();
		flushSync();
		
		let metaPanel = container.querySelector('.meta-panel');
		expect(metaPanel).toBeTruthy();
		
		const closeBtn = container.querySelector('.meta-close');
		(closeBtn as HTMLElement).click();
		flushSync();
		
		metaPanel = container.querySelector('.meta-panel');
		expect(metaPanel).toBeNull();
	});

	it('meta-panel has a Select button that calls onToggle and dismisses the drawer', () => {
		const onToggle = vi.fn();
		mount(TokenSelector, {
			target: container,
			props: { axis: 'task', tokens, selected: [], maxSelect: 1, onToggle }
		});

		const tokenChip = container.querySelector('.token-chip');
		(tokenChip as HTMLElement).click();
		flushSync();

		const selectBtn = container.querySelector('.meta-select-btn') as HTMLElement;
		expect(selectBtn).toBeTruthy();
		expect(selectBtn.textContent).toContain('Select');

		selectBtn.click();
		flushSync();

		// onToggle called with the token
		expect(onToggle).toHaveBeenCalledWith('show');
		// drawer dismissed
		expect(container.querySelector('.meta-panel')).toBeNull();
	});

	it('Select button shows "Deselect" and removes token when already selected', () => {
		const onToggle = vi.fn();
		mount(TokenSelector, {
			target: container,
			props: { axis: 'task', tokens, selected: ['show'], maxSelect: 1, onToggle }
		});

		const tokenChip = container.querySelector('.token-chip');
		(tokenChip as HTMLElement).click();
		flushSync();

		const selectBtn = container.querySelector('.meta-select-btn') as HTMLElement;
		expect(selectBtn.textContent).toContain('Deselect');

		selectBtn.click();
		flushSync();

		expect(onToggle).toHaveBeenCalledWith('show');
		expect(container.querySelector('.meta-panel')).toBeNull();
	});

	it('Select button shows "At limit" and is disabled when axis is at capacity', () => {
		mount(TokenSelector, {
			target: container,
			props: { axis: 'task', tokens, selected: ['make'], maxSelect: 1, onToggle: vi.fn() }
		});

		// Click the 'show' chip (not selected, but make is already selected = at cap)
		const chips = container.querySelectorAll('.token-chip');
		const showChip = Array.from(chips).find(
			(c) => c.querySelector('code')?.textContent === 'show'
		) as HTMLElement;
		showChip.click();
		flushSync();

		const selectBtn = container.querySelector('.meta-select-btn') as HTMLButtonElement;
		expect(selectBtn.textContent).toContain('At limit');
		expect(selectBtn.disabled).toBe(true);
	});
});
