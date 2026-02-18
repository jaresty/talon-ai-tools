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

	it('meta-backdrop appears when a token is active', () => {
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

		// No backdrop before any chip is clicked
		expect(container.querySelector('.meta-backdrop')).toBeNull();

		const tokenChip = container.querySelector('.token-chip');
		(tokenChip as HTMLElement).click();
		flushSync();

		// Backdrop present when guidance drawer is open
		expect(container.querySelector('.meta-backdrop')).toBeTruthy();
	});

	it('clicking meta-backdrop closes the guidance drawer', () => {
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

		const backdrop = container.querySelector('.meta-backdrop') as HTMLElement;
		expect(backdrop).toBeTruthy();

		backdrop.click();
		flushSync();

		expect(container.querySelector('.meta-panel')).toBeNull();
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
});
