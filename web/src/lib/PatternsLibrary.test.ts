import { flushSync, mount } from 'svelte';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import PatternsLibrary from './PatternsLibrary.svelte';
import type { StarterPack } from './grammar.js';

const MOCK_SELECTED = { task: ['probe'], method: ['diagnose'] };

vi.mock('$lib/parseCommand.js', () => ({
	parseCommand: vi.fn().mockReturnValue({
		selected: { task: ['probe'], method: ['diagnose'] },
		persona: { preset: '', voice: '', audience: '', tone: '' },
		subject: '',
		addendum: '',
		unrecognized: []
	})
}));

const MOCK_GRAMMAR = {
	tasks: { descriptions: {} },
	axes: { definitions: {} },
	hierarchy: { axis_soft_caps: {} }
} as any;

const MOCK_PACKS: StarterPack[] = [
	{ name: 'debug', framing: 'Diagnosing a bug or system failure', command: 'bar build probe diagnose adversarial unknowns' },
	{ name: 'design', framing: 'Architectural or interface design decision', command: 'bar build show branch trade balance' }
];

describe('PatternsLibrary starter packs', () => {
	// P1: starters section renders when starterPacks has items
	it('P1: renders starter packs toggle section when starterPacks is non-empty', () => {
		const container = document.createElement('div');
		mount(PatternsLibrary, {
			target: container,
			props: { patterns: [], starterPacks: MOCK_PACKS, grammar: MOCK_GRAMMAR, onLoad: vi.fn() }
		});
		expect(container.querySelector('.starters')).not.toBeNull();
	});

	// P2: no starters section when starterPacks is empty
	it('P2: no starter packs section when starterPacks is empty', () => {
		const container = document.createElement('div');
		mount(PatternsLibrary, {
			target: container,
			props: { patterns: [], starterPacks: [], grammar: MOCK_GRAMMAR, onLoad: vi.fn() }
		});
		expect(container.querySelector('.starters')).toBeNull();
	});

	// P3: clicking the toggle expands the packs grid
	it('P3: clicking toggle expands the starter packs grid', () => {
		const container = document.createElement('div');
		mount(PatternsLibrary, {
			target: container,
			props: { patterns: [], starterPacks: MOCK_PACKS, grammar: MOCK_GRAMMAR, onLoad: vi.fn() }
		});
		// Grid not visible initially
		expect(container.querySelector('.starters .patterns-grid')).toBeNull();
		// Click toggle
		const toggle = container.querySelector('.starters .patterns-toggle') as HTMLButtonElement;
		toggle.click();
		flushSync();
		// Grid now visible with pack cards
		const grid = container.querySelector('.starters .patterns-grid');
		expect(grid).not.toBeNull();
		expect(grid!.querySelectorAll('.pattern-card').length).toBe(MOCK_PACKS.length);
	});

	// P4: clicking a pack card calls onLoad with pack metadata and parsed tokens
	it('P4: clicking a pack card calls onLoad with title, desc, and parsed tokens', () => {
		const onLoad = vi.fn();
		const container = document.createElement('div');
		mount(PatternsLibrary, {
			target: container,
			props: { patterns: [], starterPacks: MOCK_PACKS, grammar: MOCK_GRAMMAR, onLoad }
		});
		// Expand then click first card
		const toggle = container.querySelector('.starters .patterns-toggle') as HTMLButtonElement;
		toggle.click();
		flushSync();
		const card = container.querySelector('.starters .pattern-card') as HTMLButtonElement;
		card.click();
		flushSync();
		expect(onLoad).toHaveBeenCalledWith(
			expect.objectContaining({
				title: 'debug',
				desc: 'Diagnosing a bug or system failure',
				command: 'bar build probe diagnose adversarial unknowns',
				tokens: MOCK_SELECTED
			})
		);
	});
});
