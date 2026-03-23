/**
 * Thread 2: grammar.ts types reference_key as a struct, not a string (ADR-0176).
 * This test will fail to compile until Grammar.reference_key is typed as a struct.
 */
import { describe, it, expect } from 'vitest';
import type { Grammar } from './grammar.js';

describe('Grammar.reference_key shape', () => {
	it('reference_key is an object with a task field, not a string', () => {
		// Construct a minimal Grammar-shaped object with reference_key as struct.
		// TypeScript will error here if reference_key is typed as string.
		const rk: Grammar['reference_key'] = {
			task: 'Primary action.',
			addendum: 'Modifies HOW.',
			constraints: 'Jointly applied.',
			constraints_axes: { scope: 'Which dimension.' },
			persona: 'Communication identity.',
			subject: 'Input data only.',
		};
		expect(typeof rk.task).toBe('string');
		expect(typeof rk.constraints_axes).toBe('object');
	});
});
