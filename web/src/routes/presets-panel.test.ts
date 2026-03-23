/**
 * ADR-0165: SPA Named Preset Panel
 * Written BEFORE implementation — all tests must fail red initially.
 */
import { flushSync, mount } from 'svelte';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import { waitFor } from '@testing-library/svelte';

const mockLocalStorage = (() => {
	let store: Record<string, string> = {};
	return {
		getItem: vi.fn((k: string) => store[k] ?? null),
		setItem: vi.fn((k: string, v: string) => { store[k] = v; }),
		removeItem: vi.fn((k: string) => { delete store[k]; }),
		clear: vi.fn(() => { store = {}; }),
		_reset: () => { store = {}; }
	};
})();

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
		meta_interpretation_guidance: '',
		axes: { definitions: {}, labels: {} }
	}),
	getAxisTokens: vi.fn().mockReturnValue([]),
	getTaskTokens: vi.fn().mockReturnValue([]),
	getPersonaPresets: vi.fn().mockReturnValue([]),
	getPersonaAxisTokens: vi.fn().mockReturnValue([]),
	getPersonaIntentTokens: vi.fn().mockReturnValue([]),
	AXES: ['task'],
	toPersonaSlug: vi.fn().mockReturnValue(''),
	getUsagePatterns: vi.fn().mockReturnValue([]),
	getStarterPacks: vi.fn().mockReturnValue([]),
	personaTokenHint: vi.fn().mockReturnValue(''),
	personaTokenDistinctionText: vi.fn().mockReturnValue('')
}));
vi.mock('$lib/incompatibilities.js', () => ({ findConflicts: vi.fn().mockReturnValue([]) }));
vi.mock('$lib/renderPrompt.js', () => ({ renderPrompt: vi.fn().mockReturnValue('') }));
vi.mock('$lib/parseCommand.js', () => ({ parseCommand: vi.fn().mockReturnValue({ selected: {}, persona: {}, subject: '', addendum: '', unrecognized: [] }) }));

async function mountPage() {
	const Page = (await import('../routes/+page.svelte')).default;
	const target = document.createElement('div');
	document.body.appendChild(target);
	mount(Page, { target });
	flushSync();
	await waitFor(() => {
		if (!target.querySelector('.presets-panel')) throw new Error('presets-panel not rendered');
	}, { timeout: 2000 });
	flushSync();
	return target;
}

describe('ADR-0165: Preset Panel', () => {
	beforeEach(() => {
		mockLocalStorage._reset();
	});

	it('PR1: preset panel is present in the DOM', async () => {
		const target = await mountPage();
		expect(target.querySelector('.presets-panel')).toBeTruthy();
		document.body.removeChild(target);
	});

	it('PR2: shows "No presets saved." when localStorage has no presets', async () => {
		const target = await mountPage();
		const empty = target.querySelector('.presets-empty');
		expect(empty?.textContent?.trim()).toBe('No presets saved.');
		document.body.removeChild(target);
	});

	it('PR3: Save button is disabled when preset name input is empty', async () => {
		const target = await mountPage();
		const btn = target.querySelector('.presets-save-btn') as HTMLButtonElement | null;
		expect(btn).toBeTruthy();
		expect(btn?.disabled).toBe(true);
		document.body.removeChild(target);
	});

	it('PR4: Save button becomes enabled when name input has text', async () => {
		const target = await mountPage();
		const input = target.querySelector('.presets-name-input') as HTMLInputElement | null;
		expect(input).toBeTruthy();
		input!.value = 'my preset';
		input!.dispatchEvent(new Event('input', { bubbles: true }));
		flushSync();
		const btn = target.querySelector('.presets-save-btn') as HTMLButtonElement | null;
		expect(btn?.disabled).toBe(false);
		document.body.removeChild(target);
	});

	it('PR5: clicking Save writes to localStorage and shows preset in list', async () => {
		const target = await mountPage();
		const input = target.querySelector('.presets-name-input') as HTMLInputElement | null;
		input!.value = 'daily-plan';
		input!.dispatchEvent(new Event('input', { bubbles: true }));
		flushSync();
		(target.querySelector('.presets-save-btn') as HTMLButtonElement).click();
		flushSync();
		expect(mockLocalStorage.setItem).toHaveBeenCalledWith('bar-presets', expect.any(String));
		const name = target.querySelector('.preset-item-name');
		expect(name?.textContent).toBe('daily-plan');
		document.body.removeChild(target);
	});

	it('PR6: clicking ✕ removes the preset from the list', async () => {
		// Seed a preset in localStorage before mount
		const { savePreset } = await import('$lib/presets.js');
		savePreset(mockLocalStorage as unknown as Storage, 'old-preset', ['make'], { task: ['make'], scope: [], method: [], completeness: [], form: [], channel: [], directional: [] }, {});
		const target = await mountPage();
		const deleteBtn = target.querySelector('.preset-delete-btn') as HTMLButtonElement | null;
		expect(deleteBtn).toBeTruthy();
		deleteBtn!.click();
		flushSync();
		expect(target.querySelector('.presets-empty')).toBeTruthy();
		document.body.removeChild(target);
	});

	it('PR7: clicking Load restores token selections without clearing subject', async () => {
		const { savePreset } = await import('$lib/presets.js');
		savePreset(
			mockLocalStorage as unknown as Storage,
			'my-config',
			['make', 'struct'],
			{ task: ['make'], scope: ['struct'], method: [], completeness: [], form: [], channel: [], directional: [] },
			{}
		);
		const target = await mountPage();
		// Set subject text to verify it is preserved after load
		const subjectArea = target.querySelector('textarea.input-area') as HTMLTextAreaElement | null;
		expect(subjectArea).toBeTruthy();
		subjectArea!.value = 'original subject';
		subjectArea!.dispatchEvent(new Event('input', { bubbles: true }));
		flushSync();
		const loadBtn = target.querySelector('.preset-load-btn') as HTMLButtonElement | null;
		expect(loadBtn).toBeTruthy();
		loadBtn!.click();
		flushSync();
		// Subject is preserved
		const subjectAreaAfter = target.querySelector('textarea.input-area') as HTMLTextAreaElement | null;
		expect(subjectAreaAfter?.value ?? '').toBe('original subject');
		document.body.removeChild(target);
	});
});
