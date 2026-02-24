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
			use_when: {
				presets: { engineer_to_engineer: PRESET_USE_WHEN },
				audience: { 'to managers': AUDIENCE_USE_WHEN }
			}
		},
		patterns: []
	}),
	getAxisTokens: vi.fn().mockReturnValue([]),
	getTaskTokens: vi.fn().mockReturnValue([]),
	getPersonaPresets: vi.fn().mockReturnValue([
		{ key: 'engineer_to_engineer', label: 'Engineer → Engineer' }
	]),
	getPersonaAxisTokens: vi.fn().mockImplementation((_grammar, axis) => {
		if (axis === 'audience') return ['to managers'];
		return [];
	}),
	AXES: ['completeness', 'scope', 'method', 'form', 'channel', 'directional'],
	toPersonaSlug: vi.fn((s: string) => s.toLowerCase().replace(/\s+/g, '-')),
	getUsagePatterns: vi.fn().mockReturnValue([]),
	getStarterPacks: vi.fn().mockReturnValue([])
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

	it('clicking a preset chip shows its use_when panel', async () => {
		await mountAndOpenPersonaTab();

		expect(container.querySelector('.persona-use-when')).toBeNull();

		const chip = Array.from(container.querySelectorAll('.persona-chip')).find((el) =>
			el.textContent?.includes('Engineer')
		) as HTMLElement;
		chip.click();
		flushSync();

		const panel = container.querySelector('.persona-use-when');
		expect(panel).not.toBeNull();
		expect(panel?.textContent).toContain('When to use');
		expect(panel?.textContent).toContain('developer');
	});

	it('clicking the active preset again hides the use_when panel', async () => {
		await mountAndOpenPersonaTab();

		const chip = Array.from(container.querySelectorAll('.persona-chip')).find((el) =>
			el.textContent?.includes('Engineer')
		) as HTMLElement;
		chip.click();
		flushSync();
		expect(container.querySelector('.persona-use-when')).not.toBeNull();

		chip.click();
		flushSync();
		expect(container.querySelector('.persona-use-when')).toBeNull();
	});

	it('selecting an audience value shows its use_when hint', async () => {
		await mountAndOpenPersonaTab();

		expect(container.querySelector('.persona-hint')).toBeNull();

		const selects = container.querySelectorAll('.persona-select');
		const audienceSelect = Array.from(selects).find(
			(el) => el.parentElement?.querySelector('span')?.textContent === 'Audience'
		) as HTMLSelectElement;

		audienceSelect.value = 'to managers';
		audienceSelect.dispatchEvent(new Event('change', { bubbles: true }));
		flushSync();

		const hint = container.querySelector('.persona-hint');
		expect(hint).not.toBeNull();
		expect(hint?.textContent).toContain('managers');
	});

	it('clearing audience selection hides the use_when hint', async () => {
		await mountAndOpenPersonaTab();

		const selects = container.querySelectorAll('.persona-select');
		const audienceSelect = Array.from(selects).find(
			(el) => el.parentElement?.querySelector('span')?.textContent === 'Audience'
		) as HTMLSelectElement;

		audienceSelect.value = 'to managers';
		audienceSelect.dispatchEvent(new Event('change', { bubbles: true }));
		flushSync();
		expect(container.querySelector('.persona-hint')).not.toBeNull();

		audienceSelect.value = '';
		audienceSelect.dispatchEvent(new Event('change', { bubbles: true }));
		flushSync();
		expect(container.querySelector('.persona-hint')).toBeNull();
	});
});
