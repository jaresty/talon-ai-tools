/**
 * ADR-0231: SPA Prompt History
 * Written BEFORE implementation — all tests must fail red initially.
 */
import { flushSync, mount } from 'svelte';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import { waitFor } from '@testing-library/svelte';
import { addHistoryEntry, loadHistory, deleteHistoryEntry, clearHistory, HISTORY_MAX } from '$lib/history.js';

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
		planning_directive: '',
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
	toAxisTokenSlug: vi.fn((s: string) => s.toLowerCase().replace(/\s+/g, '-')),
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
		if (!target.querySelector('.history-panel')) throw new Error('history-panel not rendered');
	}, { timeout: 2000 });
	flushSync();
	return target;
}

// ── Unit: history.ts pure functions ───────────────────────────────────────────

describe('ADR-0231: history module', () => {
	beforeEach(() => { mockLocalStorage._reset(); });

	it('H1: addHistoryEntry stores an entry readable by loadHistory', () => {
		addHistoryEntry(mockLocalStorage as unknown as Storage, {
			hash: 'abc123',
			trigger: 'copy-command',
			subject_preview: 'test subject',
			command_preview: 'show'
		});
		const entries = loadHistory(mockLocalStorage as unknown as Storage);
		expect(entries).toHaveLength(1);
		expect(entries[0].hash).toBe('abc123');
		expect(entries[0].trigger).toBe('copy-command');
	});

	it('H2: duplicate hash not written twice', () => {
		addHistoryEntry(mockLocalStorage as unknown as Storage, {
			hash: 'abc123', trigger: 'copy-command', subject_preview: '', command_preview: ''
		});
		addHistoryEntry(mockLocalStorage as unknown as Storage, {
			hash: 'abc123', trigger: 'copy-prompt', subject_preview: '', command_preview: ''
		});
		expect(loadHistory(mockLocalStorage as unknown as Storage)).toHaveLength(1);
	});

	it('H3: FIFO eviction — oldest dropped when exceeding HISTORY_MAX', () => {
		for (let i = 0; i < HISTORY_MAX + 5; i++) {
			addHistoryEntry(mockLocalStorage as unknown as Storage, {
				hash: `hash-${i}`, trigger: 'copy-command', subject_preview: '', command_preview: ''
			});
		}
		const entries = loadHistory(mockLocalStorage as unknown as Storage);
		expect(entries).toHaveLength(HISTORY_MAX);
		// Newest entries survive; oldest are dropped
		expect(entries[0].hash).toBe(`hash-${HISTORY_MAX + 4}`);
	});

	it('H4: deleteHistoryEntry removes the entry with matching ts', () => {
		addHistoryEntry(mockLocalStorage as unknown as Storage, {
			hash: 'abc', trigger: 'copy-command', subject_preview: '', command_preview: ''
		});
		addHistoryEntry(mockLocalStorage as unknown as Storage, {
			hash: 'def', trigger: 'copy-link', subject_preview: '', command_preview: ''
		});
		const before = loadHistory(mockLocalStorage as unknown as Storage);
		expect(before).toHaveLength(2);
		deleteHistoryEntry(mockLocalStorage as unknown as Storage, before[0].ts);
		expect(loadHistory(mockLocalStorage as unknown as Storage)).toHaveLength(1);
	});

	it('H5: clearHistory empties all entries', () => {
		addHistoryEntry(mockLocalStorage as unknown as Storage, {
			hash: 'abc', trigger: 'copy-command', subject_preview: '', command_preview: ''
		});
		clearHistory(mockLocalStorage as unknown as Storage);
		expect(loadHistory(mockLocalStorage as unknown as Storage)).toHaveLength(0);
	});
});

// ── Integration: page triggers ─────────────────────────────────────────────────

describe('ADR-0231: page trigger wiring', () => {
	beforeEach(() => {
		mockLocalStorage._reset();
		vi.clearAllMocks();
		Object.defineProperty(window, 'location', {
			value: { ...window.location, hash: '' },
			writable: true, configurable: true
		});
	});

	it('H6: copyCommand adds a history entry', async () => {
		const target = await mountPage();
		(target.querySelector('.action-row .copy-btn') as HTMLElement).click();
		await new Promise(r => setTimeout(r, 50));
		expect(loadHistory(mockLocalStorage as unknown as Storage)).toHaveLength(1);
		expect(loadHistory(mockLocalStorage as unknown as Storage)[0].trigger).toBe('copy-command');
		document.body.removeChild(target);
	});

	it('H7: copyPrompt adds a history entry', async () => {
		const target = await mountPage();
		(target.querySelector('.action-row .copy-prompt-btn') as HTMLElement).click();
		await new Promise(r => setTimeout(r, 50));
		expect(loadHistory(mockLocalStorage as unknown as Storage)).toHaveLength(1);
		expect(loadHistory(mockLocalStorage as unknown as Storage)[0].trigger).toBe('copy-prompt');
		document.body.removeChild(target);
	});

	it('H8: sharePromptNative adds a history entry', async () => {
		const target = await mountPage();
		(target.querySelector('.action-row .share-prompt-btn') as HTMLElement).click();
		await new Promise(r => setTimeout(r, 50));
		expect(loadHistory(mockLocalStorage as unknown as Storage)).toHaveLength(1);
		expect(loadHistory(mockLocalStorage as unknown as Storage)[0].trigger).toBe('share-prompt');
		document.body.removeChild(target);
	});

	it('H9: shareLink adds a history entry', async () => {
		const target = await mountPage();
		(target.querySelector('.action-row .share-link-btn') as HTMLElement).click();
		await new Promise(r => setTimeout(r, 50));
		expect(loadHistory(mockLocalStorage as unknown as Storage)).toHaveLength(1);
		expect(loadHistory(mockLocalStorage as unknown as Storage)[0].trigger).toBe('share-link');
		document.body.removeChild(target);
	});

	it('H10: copyLink adds a history entry', async () => {
		const target = await mountPage();
		(target.querySelector('.action-row .copy-link-btn') as HTMLElement).click();
		await new Promise(r => setTimeout(r, 50));
		expect(loadHistory(mockLocalStorage as unknown as Storage)).toHaveLength(1);
		expect(loadHistory(mockLocalStorage as unknown as Storage)[0].trigger).toBe('copy-link');
		document.body.removeChild(target);
	});

	it('H11: open-link (hash on mount) adds a history entry', async () => {
		// Seed a hash in location before mount
		const encoded = btoa(JSON.stringify({ selected: {}, subject: 'from link', addendum: '', persona: {} }));
		Object.defineProperty(window, 'location', {
			value: { ...window.location, hash: `#${encoded}` },
			writable: true, configurable: true
		});
		const target = await mountPage();
		await new Promise(r => setTimeout(r, 100));
		const entries = loadHistory(mockLocalStorage as unknown as Storage);
		expect(entries.some(e => e.trigger === 'open-link')).toBe(true);
		// Reset location
		Object.defineProperty(window, 'location', {
			value: { ...window.location, hash: '' },
			writable: true, configurable: true
		});
		document.body.removeChild(target);
	});
});

// ── Integration: panel UI ──────────────────────────────────────────────────────

describe('ADR-0231: history panel UI', () => {
	beforeEach(() => {
		mockLocalStorage._reset();
		vi.clearAllMocks();
		Object.defineProperty(window, 'location', {
			value: { ...window.location, hash: '' },
			writable: true, configurable: true
		});
	});

	it('H12: .history-panel is present in the DOM', async () => {
		const target = await mountPage();
		expect(target.querySelector('.history-panel')).toBeTruthy();
		document.body.removeChild(target);
	});

	it('H13: .history-empty shown when no entries', async () => {
		const target = await mountPage();
		expect(target.querySelector('.history-empty')).toBeTruthy();
		document.body.removeChild(target);
	});

	it('H14: clicking history entry restores state', async () => {
		// Seed an entry with a known subject
		const hash = btoa(JSON.stringify({
			selected: {}, subject: 'restored subject', addendum: '', persona: {}
		}));
		addHistoryEntry(mockLocalStorage as unknown as Storage, {
			hash, trigger: 'copy-command', subject_preview: 'restored subject', command_preview: ''
		});
		const target = await mountPage();
		flushSync();
		const entry = target.querySelector('.history-entry-load') as HTMLElement | null;
		expect(entry).toBeTruthy();
		entry!.click();
		flushSync();
		const textarea = target.querySelector('textarea.input-area') as HTMLTextAreaElement | null;
		expect(textarea?.value).toBe('restored subject');
		document.body.removeChild(target);
	});
});
