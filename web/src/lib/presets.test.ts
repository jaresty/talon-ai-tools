import { describe, it, expect } from 'vitest';
import { savePreset, listPresets, deletePreset, slugifyPresetName, PRESETS_KEY } from './presets.js';

function mockStorage(): Storage {
	const store: Record<string, string> = {};
	return {
		getItem: (k: string) => store[k] ?? null,
		setItem: (k: string, v: string) => {
			store[k] = v;
		},
		removeItem: (k: string) => {
			delete store[k];
		},
		clear: () => {
			for (const k in store) delete store[k];
		},
		get length() {
			return Object.keys(store).length;
		},
		key: (i: number) => Object.keys(store)[i] ?? null
	} as Storage;
}

describe('slugifyPresetName', () => {
	it('S1: lowercases and replaces spaces with dashes', () => {
		expect(slugifyPresetName('Daily Plan')).toBe('daily-plan');
	});
	it('S2: strips leading/trailing dashes', () => {
		expect(slugifyPresetName('  my preset  ')).toBe('my-preset');
	});
	it('S3: collapses multiple separators', () => {
		expect(slugifyPresetName('a--b  c')).toBe('a-b-c');
	});
	it('S4: returns "preset" for empty/whitespace input', () => {
		expect(slugifyPresetName('')).toBe('preset');
		expect(slugifyPresetName('   ')).toBe('preset');
	});
});

describe('savePreset / listPresets', () => {
	it('P1: saves a preset and retrieves it via listPresets', () => {
		const s = mockStorage();
		savePreset(s, 'daily-plan', ['make', 'struct'], { task: ['make'], scope: ['struct'], method: [], completeness: [], form: [], channel: [], directional: [] }, {});
		const list = listPresets(s);
		expect(list).toHaveLength(1);
		expect(list[0].name).toBe('daily-plan');
		expect(list[0].tokens).toEqual(['make', 'struct']);
		expect(list[0].version).toBe(3);
		expect(list[0].source).toBe('spa');
	});

	it('P2: listPresets returns empty array when no presets saved', () => {
		const s = mockStorage();
		expect(listPresets(s)).toEqual([]);
	});

	it('P3: savePreset overwrites existing preset with same slugified name', () => {
		const s = mockStorage();
		savePreset(s, 'my preset', ['make'], { task: ['make'], scope: [], method: [], completeness: [], form: [], channel: [], directional: [] }, {});
		savePreset(s, 'my preset', ['show', 'struct'], { task: ['show'], scope: ['struct'], method: [], completeness: [], form: [], channel: [], directional: [] }, {});
		const list = listPresets(s);
		expect(list).toHaveLength(1);
		expect(list[0].tokens).toEqual(['show', 'struct']);
	});

	it('P4: listPresets returns multiple presets sorted by saved_at descending', () => {
		const s = mockStorage();
		savePreset(s, 'alpha', ['make'], { task: ['make'], scope: [], method: [], completeness: [], form: [], channel: [], directional: [] }, {});
		// Backdate alpha
		const raw = JSON.parse(s.getItem(PRESETS_KEY)!);
		raw['alpha'].saved_at = '2026-01-01T00:00:00.000Z';
		s.setItem(PRESETS_KEY, JSON.stringify(raw));
		savePreset(s, 'beta', ['show'], { task: ['show'], scope: [], method: [], completeness: [], form: [], channel: [], directional: [] }, {});
		const list = listPresets(s);
		expect(list[0].name).toBe('beta'); // newer first
		expect(list[1].name).toBe('alpha');
	});

	it('P5: round-trip preserves tokens and persona across stringify/parse', () => {
		const s = mockStorage();
		const tokens = ['persona=peer_engineer_explanation', 'make', 'full', 'struct', 'flow', 'bullets'];
		savePreset(
			s,
			'complex',
			tokens,
			{ task: ['make'], scope: ['struct'], method: ['flow'], completeness: ['full'], form: ['bullets'], channel: [], directional: [] },
			{ preset: 'peer_engineer_explanation' }
		);
		const list = listPresets(s);
		expect(list[0].tokens).toEqual(tokens);
		expect(list[0].result.persona.preset).toBe('peer_engineer_explanation');
	});
});

describe('deletePreset', () => {
	it('P6: deletePreset removes the named preset', () => {
		const s = mockStorage();
		savePreset(s, 'to-delete', ['make'], { task: ['make'], scope: [], method: [], completeness: [], form: [], channel: [], directional: [] }, {});
		deletePreset(s, 'to-delete');
		expect(listPresets(s)).toEqual([]);
	});

	it('P7: deletePreset is a no-op for nonexistent preset', () => {
		const s = mockStorage();
		expect(() => deletePreset(s, 'ghost')).not.toThrow();
		expect(listPresets(s)).toEqual([]);
	});

	it('P8: deletePreset matches by slugified name (spaces → dashes)', () => {
		const s = mockStorage();
		savePreset(s, 'my preset', ['make'], { task: ['make'], scope: [], method: [], completeness: [], form: [], channel: [], directional: [] }, {});
		deletePreset(s, 'my preset');
		expect(listPresets(s)).toEqual([]);
	});
});
