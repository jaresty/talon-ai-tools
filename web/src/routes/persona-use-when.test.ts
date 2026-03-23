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

const PRESET_USE_WHEN = 'Use when a developer is explaining technical details to another developer.';
const AUDIENCE_USE_WHEN = 'Address managers focused on outcomes and risk.';

vi.mock('$lib/grammar.js', () => ({
	loadGrammar: vi.fn().mockResolvedValue({
		hierarchy: { axis_priority: [], axis_soft_caps: {}, axis_incompatibilities: {} },
		axes: { definitions: {}, labels: {}, guidance: {}, use_when: {} },
		tasks: { descriptions: {}, labels: {}, guidance: {} },
		persona: {
			presets: {
				engineer_to_engineer: {
					key: 'engineer_to_engineer',
					label: 'Engineer → Engineer',
					voice: 'as-programmer',
					audience: 'to-senior-engineer',
					tone: '',
					spoken: ''
				}
			},
			axes: { voice: [], audience: ['to managers'], tone: [] },
			metadata: {
				presets: {
					engineer_to_engineer: {
						definition: 'Peer-level technical explanation.',
						heuristics: [PRESET_USE_WHEN],
						distinctions: []
					}
				},
				audience: {
					'to managers': {
						definition: 'Address managers.',
						heuristics: [AUDIENCE_USE_WHEN],
						distinctions: []
					}
				}
			}
		},
		patterns: [],
		reference_key: { task: '', addendum: '', constraints: '', constraints_axes: {}, persona: '', subject: '' },
		execution_reminder: '',
		meta_interpretation_guidance: ''
	}),
	getAxisTokens: vi.fn().mockReturnValue([]),
	getTaskTokens: vi.fn().mockReturnValue([]),
	getPersonaPresets: vi.fn().mockReturnValue([
		{ key: 'engineer_to_engineer', label: 'Engineer → Engineer', voice: 'as programmer', audience: 'to senior engineer', tone: '', spoken: '' }
	]),
	getPersonaAxisTokens: vi.fn().mockImplementation((_grammar, axis) => {
		if (axis === 'audience') return ['to managers'];
		return [];
	}),
	getPersonaIntentTokens: vi.fn().mockReturnValue([]),
	getPersonaAxisTokensMeta: vi.fn().mockReturnValue([]),
	getPresetHint: vi.fn().mockReturnValue(''),
	AXES: ['completeness', 'scope', 'method', 'form', 'channel', 'directional'],
	toPersonaSlug: vi.fn((s: string) => s.toLowerCase().replace(/\s+/g, '-')),
	getUsagePatterns: vi.fn().mockReturnValue([]),
	getStarterPacks: vi.fn().mockReturnValue([]),
	getCompositionData: vi.fn().mockReturnValue(null),
	getChipState: vi.fn().mockReturnValue(null),
	getReverseChipState: vi.fn().mockReturnValue(null),
	getChipStateWithReason: vi.fn().mockReturnValue({ state: null, naturalWith: [], cautionWith: [] }),
	// ADR-0156: structured metadata helpers replace persona.use_when/guidance reads
	personaTokenHint: vi.fn().mockImplementation((_grammar, axis, token) => {
		if (axis === 'presets' && token === 'engineer_to_engineer') return PRESET_USE_WHEN;
		if (axis === 'audience' && token === 'to managers') return AUDIENCE_USE_WHEN;
		return '';
	}),
	personaTokenDistinctionText: vi.fn().mockReturnValue('')
}));

vi.mock('$lib/incompatibilities.js', () => ({
	findConflicts: vi.fn().mockReturnValue([])
}));

describe('Persona use_when visibility', () => {
	let container: HTMLDivElement;

	beforeEach(() => {
		vi.clearAllMocks();
		container = document.createElement('div');
		document.body.appendChild(container);
	});

	afterEach(() => {
		document.body.removeChild(container);
	});

	async function mountAndOpenPersonaTab() {
		const { default: Page } = await import('../routes/+page.svelte');
		mount(Page, { target: container });
		await new Promise((r) => setTimeout(r, 100));

		const personaTab = Array.from(container.querySelectorAll('.tab')).find(
			(el) => el.textContent?.trim() === 'persona'
		);
		(personaTab as HTMLElement).click();
		flushSync();
	}

	it('clicking a preset chip shows its axis summary strip', async () => {
		await mountAndOpenPersonaTab();

		expect(container.querySelector('.preset-axis-summary')).toBeNull();

		const chip = Array.from(container.querySelectorAll('.persona-chip')).find((el) =>
			el.textContent?.includes('Engineer')
		) as HTMLElement;
		chip.click();
		flushSync();

		const panel = container.querySelector('.preset-axis-summary');
		expect(panel).not.toBeNull();
		expect(panel?.textContent).toContain('voice=');
	});

	it('clicking the active preset again hides the axis summary strip', async () => {
		await mountAndOpenPersonaTab();

		const chip = Array.from(container.querySelectorAll('.persona-chip')).find((el) =>
			el.textContent?.includes('Engineer')
		) as HTMLElement;
		chip.click();
		flushSync();
		expect(container.querySelector('.preset-axis-summary')).not.toBeNull();

		chip.click();
		flushSync();
		expect(container.querySelector('.preset-axis-summary')).toBeNull();
	});
});
