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
	getUsagePatterns: vi.fn().mockReturnValue([])
}));

vi.mock('$lib/incompatibilities.js', () => ({
	findConflicts: vi.fn().mockReturnValue([])
}));

describe('Page — Mobile Floating Action Button', () => {
	let container: HTMLDivElement;

	beforeEach(() => {
		vi.clearAllMocks();
		container = document.createElement('div');
		document.body.appendChild(container);
	});

	it('has action buttons in the DOM', async () => {
		const { default: Page } = await import('../routes/+page.svelte');
		mount(Page, { target: container });
		
		await new Promise(r => setTimeout(r, 100));
		
		const actionRow = container.querySelector('.action-row');
		expect(actionRow).toBeTruthy();
	});

	it('has copy and share buttons', async () => {
		const { default: Page } = await import('../routes/+page.svelte');
		mount(Page, { target: container });
		
		await new Promise(r => setTimeout(r, 100));
		
		const copyBtn = container.querySelector('.copy-btn');
		const shareBtn = container.querySelector('.share-btn');
		expect(copyBtn).toBeTruthy();
		expect(shareBtn).toBeTruthy();
	});
});
