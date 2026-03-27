/**
 * ADR-0000: stateCodec round-trip invariant over Unicode input.
 * Written BEFORE implementation — tests must fail red initially.
 */
import { describe, it, expect } from 'vitest';
import { encodeState, decodeState } from './stateCodec.js';

describe('stateCodec', () => {
	it('round-trips ASCII state without loss', () => {
		const state = { subject: 'hello', addendum: 'world', selected: {}, persona: {} };
		expect(decodeState(encodeState(state))).toEqual(state);
	});

	it('round-trips state containing non-Latin1 characters (Unicode)', () => {
		const state = { subject: 'café ☕ naïve résumé', addendum: '日本語', selected: {}, persona: {} };
		expect(decodeState(encodeState(state))).toEqual(state);
	});

	it('round-trips emoji', () => {
		const state = { subject: '🎉🚀', addendum: '', selected: {}, persona: {} };
		expect(decodeState(encodeState(state))).toEqual(state);
	});

	it('decodeState returns null for malformed input', () => {
		expect(decodeState('!!!not-valid-base64!!!')).toBeNull();
	});
});
