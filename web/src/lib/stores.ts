import { writable } from 'svelte/store';
import type { Grammar, PromptVariant } from '$lib/grammar.js';
import type { PersonaState } from '$lib/renderPrompt.js';

export const selected = writable<Record<string, string[]>>({});
export const persona = writable<PersonaState>({ preset: '', voice: '', audience: '', tone: '', intent: '' });
export const subject = writable('');
export const addendum = writable('');
// Lateral-seed control: number of random concrete nouns to inject (0 = off) and
// an optional seed for reproducible selection within the SPA.
export const seedWordsCount = writable(0);
export const seedWordsSeed = writable<number | null>(null);
// Mutation control: when true, --mutate perturbs one random active non-task
// token's stance. The SPA re-rolls the locus on each render (no seed stored).
export const mutateEnabled = writable(false);
// Prompt style: 'plain' uses the grammar's plain scaffolding text (the default);
// 'standard' restores the original derivation-span scaffolding. Web rendering only.
export const promptVariant = writable<PromptVariant>('plain');
export const grammar = writable<Grammar | null>(null);
export const conflicts = writable<{ tokenA: string; tokenB: string; reason: string }[]>([]);
