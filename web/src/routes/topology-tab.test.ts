/**
 * ADR-0236: topology axis tab must appear in the SPA tab bar between task and completeness.
 */
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

vi.mock('$lib/grammar.js', () => ({
	loadGrammar: vi.fn().mockResolvedValue({
		hierarchy: { axis_soft_caps: {} },
		tokens: {},
		persona_presets: [],
		persona: { use_when: {} },
		reference_key: { task: '', addendum: '', constraints: '', constraints_axes: {}, persona: '', subject: '' },
		execution_reminder: '',
		planning_directive: '',
		meta_interpretation_guidance: ''
	}),
	getAxisTokens: vi.fn().mockReturnValue([]),
	getTaskTokens: vi.fn().mockReturnValue([
		{ token: 'show', label: 'Explain', description: 'Explain or describe', guidance: '', use_when: '' }
	]),
	getPersonaPresets: vi.fn().mockReturnValue([]),
	getPersonaAxisTokens: vi.fn().mockReturnValue([]),
	getPersonaIntentTokens: vi.fn().mockReturnValue([]),
	getPersonaAxisTokensMeta: vi.fn().mockReturnValue([]),
	getPresetHint: vi.fn().mockReturnValue(''),
	personaTokenHint: vi.fn().mockReturnValue(''),
	personaTokenDistinctionText: vi.fn().mockReturnValue(''),
	AXES: ['topology', 'completeness', 'scope', 'method', 'form', 'channel', 'directional'],
	toPersonaSlug: vi.fn().mockReturnValue(''),
	toAxisTokenSlug: vi.fn().mockReturnValue(''),
	getUsagePatterns: vi.fn().mockReturnValue([]),
	getStarterPacks: vi.fn().mockReturnValue([]),
	getCompositionData: vi.fn().mockReturnValue(null),
	getChipState: vi.fn().mockReturnValue(null),
	getReverseChipState: vi.fn().mockReturnValue(null),
	getChipStateWithReason: vi.fn().mockReturnValue({ state: null, naturalWith: [], cautionWith: [] })
}));

vi.mock('$lib/incompatibilities.js', () => ({
	findConflicts: vi.fn().mockReturnValue([])
}));

vi.mock('$lib/renderPrompt.js', () => ({
	renderPrompt: vi.fn().mockReturnValue('MOCK RENDERED PROMPT')
}));

describe('Page — ADR-0236 topology tab', () => {
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

	it('topology tab exists in the tab bar', async () => {
		const { default: Page } = await import('../routes/+page.svelte');
		mount(Page, { target: container });
		await new Promise(r => setTimeout(r, 100));
		flushSync();

		const topologyTab = container.querySelector<HTMLElement>('[id="tab-topology"]');
		expect(topologyTab).toBeTruthy();
	});

	it('topology tab appears before completeness tab', async () => {
		const { default: Page } = await import('../routes/+page.svelte');
		mount(Page, { target: container });
		await new Promise(r => setTimeout(r, 100));
		flushSync();

		const tabs = Array.from(container.querySelectorAll<HTMLElement>('[role="tab"]'));
		const tabLabels = tabs.map(t => t.id.replace('tab-', ''));
		const topologyIdx = tabLabels.indexOf('topology');
		const completenessIdx = tabLabels.indexOf('completeness');

		expect(topologyIdx).toBeGreaterThanOrEqual(0);
		expect(completenessIdx).toBeGreaterThanOrEqual(0);
		expect(topologyIdx).toBeLessThan(completenessIdx);
	});
});
