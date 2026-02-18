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
	getTaskTokens: vi.fn().mockReturnValue([
		{ token: 'show', label: 'Explain', description: 'Explain or describe' }
	]),
	getPersonaPresets: vi.fn().mockReturnValue([]),
	getPersonaAxisTokens: vi.fn().mockReturnValue([]),
	AXES: ['completeness', 'scope', 'method', 'form', 'channel', 'directional'],
	toPersonaSlug: vi.fn().mockReturnValue(''),
	getUsagePatterns: vi.fn().mockReturnValue([])
}));

vi.mock('$lib/incompatibilities.js', () => ({
	findConflicts: vi.fn().mockReturnValue([])
}));

describe('Page — Mobile Tabbed Axis Interface', () => {
	let container: HTMLDivElement;

	beforeEach(() => {
		vi.clearAllMocks();
		container = document.createElement('div');
		document.body.appendChild(container);
	});

	it('renders horizontal tab bar for axis navigation', async () => {
		const { default: Page } = await import('../routes/+page.svelte');
		mount(Page, { target: container });
		expect(container.querySelector('.tab-bar')).toBeTruthy();
	});

	it('tab bar contains all axis tabs', async () => {
		const { default: Page } = await import('../routes/+page.svelte');
		mount(Page, { target: container });
		const tabs = container.querySelectorAll('.tab-bar .tab');
		const tabLabels = Array.from(tabs).map(t => t.textContent);
		expect(tabLabels).toContain('persona');
		expect(tabLabels).toContain('task');
		expect(tabLabels).toContain('completeness');
		expect(tabLabels).toContain('scope');
		expect(tabLabels).toContain('method');
		expect(tabLabels).toContain('form');
		expect(tabLabels).toContain('channel');
		expect(tabLabels).toContain('directional');
	});
});
