// ADR-0170: persona voice/audience/tone/intent sections use TokenSelector chip grids
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

const makeTokenMeta = (token: string) => ({
	token,
	label: token,
	description: `description of ${token}`,
	guidance: '',
	use_when: '',
	kanji: '',
	category: '',
	routing_concept: '',
	metadata: null
});

vi.mock('$lib/grammar.js', () => ({
	loadGrammar: vi.fn().mockResolvedValue({
		hierarchy: { axis_priority: [], axis_soft_caps: {}, axis_incompatibilities: {} },
		axes: { definitions: {}, labels: {}, guidance: {}, use_when: {} },
		tasks: { descriptions: {}, labels: {}, guidance: {} },
		persona: {
			presets: {
				designer_to_pm: {
					key: 'designer_to_pm',
					label: 'Designer to PM',
					voice: 'as designer',
					audience: 'to product manager',
					tone: 'directly',
					spoken: ''
				}
			},
			axes: { voice: [], audience: [], tone: [] }
		},
		patterns: [],
		reference_key: '',
		execution_reminder: '',
		meta_interpretation_guidance: ''
	}),
	getAxisTokens: vi.fn().mockReturnValue([]),
	getTaskTokens: vi.fn().mockReturnValue([]),
	getPersonaPresets: vi.fn().mockReturnValue([
		{ key: 'designer_to_pm', label: 'Designer to PM', voice: 'as designer', audience: 'to product manager', tone: 'directly', spoken: '' }
	]),
	getPersonaAxisTokens: vi.fn().mockReturnValue([]),
	getPersonaAxisTokensMeta: vi.fn().mockImplementation((_grammar: unknown, axis: string) => {
		if (axis === 'voice') return [makeTokenMeta('as designer'), makeTokenMeta('as programmer')];
		if (axis === 'audience') return [makeTokenMeta('to product manager')];
		if (axis === 'tone') return [makeTokenMeta('directly')];
		if (axis === 'intent') return [makeTokenMeta('teach'), makeTokenMeta('inform')];
		return [];
	}),
	getPersonaIntentTokens: vi.fn().mockReturnValue(['teach', 'inform']),
	AXES: ['completeness', 'scope', 'method', 'form', 'channel', 'directional'],
	toPersonaSlug: vi.fn((s: string) => s.toLowerCase().replace(/\s+/g, '-')),
	getUsagePatterns: vi.fn().mockReturnValue([]),
	getStarterPacks: vi.fn().mockReturnValue([]),
	getCompositionData: vi.fn().mockReturnValue(null),
	getChipState: vi.fn().mockReturnValue(null),
	getReverseChipState: vi.fn().mockReturnValue(null),
	getChipStateWithReason: vi.fn().mockReturnValue({ state: null, naturalWith: [], cautionWith: [] }),
	personaTokenHint: vi.fn().mockReturnValue(''),
	personaTokenDistinctionText: vi.fn().mockReturnValue(''),
	getPresetHint: vi.fn().mockImplementation((_grammar: unknown, key: string) => {
		if (key === 'designer_to_pm') return 'explain design to PM';
		return '';
	})
}));

vi.mock('$lib/incompatibilities.js', () => ({
	findConflicts: vi.fn().mockReturnValue([])
}));

describe('ADR-0170: Persona chip grids', () => {
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

	it('CG-1: renders chip grids for voice, audience, tone, intent — not select elements', async () => {
		await mountAndOpenPersonaTab();
		expect(container.querySelectorAll('.persona-select').length).toBe(0);
		expect(container.querySelector('[aria-label="voice tokens"]')).not.toBeNull();
		expect(container.querySelector('[aria-label="audience tokens"]')).not.toBeNull();
		expect(container.querySelector('[aria-label="tone tokens"]')).not.toBeNull();
		expect(container.querySelector('[aria-label="intent tokens"]')).not.toBeNull();
	});

	it('CG-2: override group has "or customize" label', async () => {
		await mountAndOpenPersonaTab();
		const label = container.querySelector('.override-group-label');
		expect(label).not.toBeNull();
		expect(label?.textContent?.toLowerCase()).toContain('customize');
	});

	it('CG-3: voice, audience, and tone grids are inside the override group', async () => {
		await mountAndOpenPersonaTab();
		const overrideGroup = container.querySelector('.override-group');
		expect(overrideGroup).not.toBeNull();
		expect(overrideGroup?.querySelector('[aria-label="voice tokens"]')).not.toBeNull();
		expect(overrideGroup?.querySelector('[aria-label="audience tokens"]')).not.toBeNull();
		expect(overrideGroup?.querySelector('[aria-label="tone tokens"]')).not.toBeNull();
	});

	it('CG-4: intent grid is outside the override group', async () => {
		await mountAndOpenPersonaTab();
		const overrideGroup = container.querySelector('.override-group');
		expect(overrideGroup?.querySelector('[aria-label="intent tokens"]')).toBeNull();
		expect(container.querySelector('[aria-label="intent tokens"]')).not.toBeNull();
	});

	it('CG-5: preset axis summary strip shows axis chips when a preset is active', async () => {
		await mountAndOpenPersonaTab();
		const chip = Array.from(container.querySelectorAll('.persona-chip')).find((el) =>
			el.textContent?.includes('Designer')
		) as HTMLElement;
		chip.click();
		flushSync();

		const summary = container.querySelector('.preset-axis-summary');
		expect(summary).not.toBeNull();
		expect(summary?.textContent).toContain('voice=');
	});

	it('CG-8: active preset constituent tokens appear selected in voice/audience/tone grids', async () => {
		await mountAndOpenPersonaTab();
		const chip = Array.from(container.querySelectorAll('.persona-chip')).find((el) =>
			el.textContent?.includes('Designer')
		) as HTMLElement;
		chip.click();
		flushSync();

		const voiceGrid = container.querySelector('[aria-label="voice tokens"]');
		const selectedVoice = voiceGrid?.querySelector('[aria-selected="true"]');
		expect(selectedVoice).not.toBeNull();
		expect(selectedVoice?.textContent).toContain('as designer');
	});

	it('CG-9: overriding voice from preset preserves audience and tone', async () => {
		await mountAndOpenPersonaTab();
		// activate preset
		const presetChip = Array.from(container.querySelectorAll('.persona-chip')).find((el) =>
			el.textContent?.includes('Designer')
		) as HTMLElement;
		presetChip.click();
		flushSync();

		// click a different voice token (two-click pattern: first opens panel, second selects)
		const voiceGrid = container.querySelector('[aria-label="voice tokens"]');
		const programmerChip = Array.from(voiceGrid?.querySelectorAll('[role="option"]') ?? []).find(
			(el) => el.textContent?.includes('as programmer')
		) as HTMLElement;
		programmerChip.dispatchEvent(new PointerEvent('pointerdown', { bubbles: true }));
		programmerChip.click();
		flushSync();
		programmerChip.dispatchEvent(new PointerEvent('pointerdown', { bubbles: true }));
		programmerChip.click();
		flushSync();

		// audience and tone should still be selected from the preset
		const audienceGrid = container.querySelector('[aria-label="audience tokens"]');
		const toneGrid = container.querySelector('[aria-label="tone tokens"]');
		expect(audienceGrid?.querySelector('[aria-selected="true"]')?.textContent).toContain('to product manager');
		expect(toneGrid?.querySelector('[aria-selected="true"]')?.textContent).toContain('directly');
	});

	it('CG-7: preset chips render a subtitle from the first heuristic', async () => {
		await mountAndOpenPersonaTab();
		const chip = Array.from(container.querySelectorAll('.persona-chip')).find((el) =>
			el.textContent?.includes('Designer')
		);
		expect(chip).not.toBeNull();
		expect(chip?.querySelector('.persona-chip-hint')).not.toBeNull();
		expect(chip?.querySelector('.persona-chip-hint')?.textContent).toContain('explain design');
	});

	it('CG-6: preset axis summary strip is absent when no preset is selected', async () => {
		await mountAndOpenPersonaTab();
		expect(container.querySelector('.preset-axis-summary')).toBeNull();
	});
});
