import { describe, it, expect, vi } from 'vitest';
import { createEmbedder } from './embedder.js';

describe('createEmbedder', () => {
	it('E1: returns a function', () => {
		const embedder = createEmbedder();
		expect(typeof embedder).toBe('function');
	});

	it('E2: with stubbed pipeline, returns the Float32Array from the stub directly', async () => {
		const fakeVec = new Float32Array(384).fill(0.1);
		const embedder = createEmbedder({
			pipeline: async (_text: string) => fakeVec
		});
		const result = await embedder('test query');
		expect(result).toBeInstanceOf(Float32Array);
		expect(result!.length).toBe(384);
		expect(result).toBe(fakeVec);
	});

	it('E3: on pipeline error, returns null gracefully', async () => {
		const embedder = createEmbedder({
			pipeline: async () => { throw new Error('model not loaded'); }
		});
		const result = await embedder('test query');
		expect(result).toBeNull();
	});
});
