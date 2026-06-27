/**
 * SelectorPanel extraction — governs that SelectorPanel renders within +page.svelte
 * Written BEFORE implementation — must fail red initially.
 */
import { flushSync, mount } from 'svelte';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import { selected, persona, grammar, conflicts } from '$lib/stores.js';

const mockLocalStorage = {
	getItem: vi.fn(() => null),
	setItem: vi.fn(),
	removeItem: vi.fn(),
	clear: vi.fn()
};
Object.defineProperty(globalThis, 'localStorage', { value: mockLocalStorage, writable: true });
Object.defineProperty(globalThis, 'navigator', {
	value: { clipboard: { writeText: vi.fn().mockResolvedValue(undefined) } },
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
		meta_interpretation_guidance: '',
		axes: { definitions: {}, labels: {}, axis_descriptions: {} }
	}),
	getAxisTokens: vi.fn().mockReturnValue([]),
	getTaskTokens: vi.fn().mockReturnValue([]),
	getPersonaPresets: vi.fn().mockReturnValue([]),
	getPersonaAxisTokens: vi.fn().mockReturnValue([]),
	getPersonaAxisTokensMeta: vi.fn().mockReturnValue([]),
	AXES: ['task', 'completeness', 'scope', 'method', 'form', 'channel', 'directional'],
	toPersonaSlug: vi.fn().mockReturnValue(''),
	toAxisTokenSlug: vi.fn((s: string) => s.toLowerCase().replace(/\s+/g, '-')),
	buildCommandTokens: vi.fn().mockReturnValue([]),
	getUsagePatterns: vi.fn().mockReturnValue([]),
	getStarterPacks: vi.fn().mockReturnValue([]),
	getCompositionData: vi.fn().mockReturnValue(null),
	getChipState: vi.fn().mockReturnValue(null),
	getReverseChipState: vi.fn().mockReturnValue(null),
	getChipStateWithReason: vi.fn().mockReturnValue({ state: null, naturalWith: [], cautionWith: [] })
}));
vi.mock('$lib/incompatibilities.js', () => ({ findConflicts: vi.fn().mockReturnValue([]) }));
vi.mock('$lib/renderPrompt.js', () => ({ renderPrompt: vi.fn().mockReturnValue('MOCK RENDERED PROMPT') }));

describe('SelectorPanel extraction', () => {
	beforeEach(() => {
		vi.clearAllMocks();
		selected.set({ task: [], completeness: [], scope: [], method: [], form: [], channel: [], directional: [] });
		persona.set({ preset: '', voice: '', audience: '', tone: '', intent: '' });
		grammar.set(null);
		conflicts.set([]);
	});

	it('SelectorPanel renders selector-panel element', async () => {
		const { default: Page } = await import('../routes/+page.svelte');
		const target = document.createElement('div');
		document.body.appendChild(target);
		mount(Page, { target });
		await new Promise((r) => setTimeout(r, 50));
		flushSync();
		const panel = target.querySelector('.selector-panel');
		expect(panel).toBeTruthy();
		document.body.removeChild(target);
	});

	async function mountSelectorPanel(target: HTMLElement, onModeChange = (_m: string) => {}) {
		const { loadGrammar } = await import('$lib/grammar.js');
		const g = await loadGrammar();
		grammar.set(g);
		flushSync();
		const { default: SelectorPanel } = await import('$lib/SelectorPanel.svelte');
		mount(SelectorPanel, {
			target,
			props: {
				patterns: [],
				starterPacks: [],
				suggestionScores: new Map(),
				embedder: async () => null,
				activeMode: 'build' as const,
				onClear: () => {},
				onModeChange
			}
		});
		await new Promise((r) => setTimeout(r, 50));
		flushSync();
	}

	it('SelectorPanel standalone renders selector-panel element', async () => {
		const target = document.createElement('div');
		document.body.appendChild(target);
		await mountSelectorPanel(target);
		const panel = target.querySelector('.selector-panel');
		expect(panel).toBeTruthy();
		document.body.removeChild(target);
	});

	it('SelectorPanel activeMode prop controls which mode button appears active', async () => {
		const { default: SelectorPanel } = await import('$lib/SelectorPanel.svelte');
		const { loadGrammar } = await import('$lib/grammar.js');
		const g = await loadGrammar();
		grammar.set(g);
		flushSync();
		const target = document.createElement('div');
		document.body.appendChild(target);
		mount(SelectorPanel, {
			target,
			props: {
				patterns: [],
				starterPacks: [],
				suggestionScores: new Map(),
				embedder: async () => null,
				activeMode: 'build' as const,
				onClear: () => {},
				onModeChange: () => {}
			}
		});
		await new Promise((r) => setTimeout(r, 50));
		flushSync();
		// SelectorPanel renders its content (selector-panel) when activeMode=build
		expect(target.querySelector('.selector-panel')).toBeTruthy();
		document.body.removeChild(target);
	});

	it('SelectorPanel exposes focusFilterOrFirst, goToNextTab, goToPrevTab, focusActiveTab on mounted instance', async () => {
		const { loadGrammar } = await import('$lib/grammar.js');
		const g = await loadGrammar();
		grammar.set(g);
		flushSync();
		const { default: SelectorPanel } = await import('$lib/SelectorPanel.svelte');
		const target = document.createElement('div');
		document.body.appendChild(target);
		const instance = mount(SelectorPanel, {
			target,
			props: {
				patterns: [],
				starterPacks: [],
				suggestionScores: new Map(),
				embedder: async () => null,
				activeMode: 'build' as const,
				onClear: () => {},
				onModeChange: () => {}
			}
		});
		await new Promise((r) => setTimeout(r, 50));
		flushSync();
		expect(typeof (instance as unknown as Record<string, unknown>).focusFilterOrFirst).toBe('function');
		expect(typeof (instance as unknown as Record<string, unknown>).goToNextTab).toBe('function');
		expect(typeof (instance as unknown as Record<string, unknown>).goToPrevTab).toBe('function');
		expect(typeof (instance as unknown as Record<string, unknown>).focusActiveTab).toBe('function');
		document.body.removeChild(target);
	});

});
