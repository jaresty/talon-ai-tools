import { get } from 'svelte/store';
import { describe, it, expect } from 'vitest';

describe('stores', () => {
	it('stores exports selected store', async () => {
		const { selected } = await import('./stores.js');
		expect(get(selected)).toEqual({});
	});

	it('stores exports persona store', async () => {
		const { persona } = await import('./stores.js');
		const v = get(persona);
		expect(v).toMatchObject({ preset: '', voice: '', audience: '', tone: '', intent: '' });
	});

	it('stores exports subject store', async () => {
		const { subject } = await import('./stores.js');
		expect(get(subject)).toBe('');
	});

	it('stores exports addendum store', async () => {
		const { addendum } = await import('./stores.js');
		expect(get(addendum)).toBe('');
	});

	it('stores exports grammar store', async () => {
		const { grammar } = await import('./stores.js');
		expect(get(grammar)).toBeNull();
	});

	it('stores exports conflicts store', async () => {
		const { conflicts } = await import('./stores.js');
		expect(get(conflicts)).toEqual([]);
	});

	it('selected store is writable', async () => {
		const { selected } = await import('./stores.js');
		selected.set({ method: ['diagnose'] });
		expect(get(selected)).toEqual({ method: ['diagnose'] });
		selected.set({});
	});
});
