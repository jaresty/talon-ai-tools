import { describe, it, expect } from 'vitest';
import {
	getAxisTokens,
	getTaskTokens,
	getUsagePatterns,
	getStarterPacks,
	getPersonaAxisTokensMeta,
	getPersonaIntentTokens,
	getMethodTokensByCategory,
	toPersonaSlug,
	getReverseChipState,
	type Grammar
} from './grammar.js';
import { findConflicts } from './incompatibilities.js';

const minimalGrammar: Grammar = {
	axes: {
		definitions: {
			form: {
				prose: 'Flowing narrative text.',
				wardley: 'Strategic mapping: user wants to position components on an evolution axis.'
			}
		},
		labels: {
			form: {
				wardley: 'Wardley Map'
			}
		},
		guidance: {
			form: {
				wardley: 'Use with strategic planning tasks.'
			}
		},
		use_when: {
			form: {
				wardley: 'Use when the user wants a Wardley map output.'
			}
		}
	},
	tasks: {
		descriptions: {
			show: 'Reveal the structure, content, or meaning of the subject.',
			make: 'Produce or generate the artifact described in the subject.'
		},
		labels: { show: 'Show', make: 'Make' },
		guidance: {},
		use_when: {
			show: 'Explaining or describing something for an audience.',
			make: 'Creating new content or artifacts.'
		},
		kanji: { show: '示', make: '作' }
	},
	hierarchy: {
		axis_priority: ['completeness', 'scope', 'method', 'form', 'channel', 'directional'],
		axis_soft_caps: { scope: 2, method: 3 },
		axis_incompatibilities: {}
	},
	persona: {
		presets: {},
		axes: { voice: [], audience: ['to managers', 'to product manager'], tone: [] },
		docs: { audience: { 'to managers': 'Audience focused on outcomes and risk.' } },
		use_when: { audience: { 'to managers': 'Use when addressing outcome-focused leadership.' } },
		kanji: { audience: { 'to managers': '経営' }, voice: { 'as-expert': '專' } }
	},
	patterns: [
		{
			title: 'Example Pattern',
			command: 'bar build show mean full plain',
			example: 'bar build show mean full plain --subject "test"',
			desc: 'A test pattern.',
			tokens: { completeness: ['full'], scope: ['mean'] }
		}
	]
};

describe('toPersonaSlug', () => {
	it('converts spaces to hyphens and lowercases', () => {
		expect(toPersonaSlug('as Designer')).toBe('as-designer');
		expect(toPersonaSlug('Kent Beck')).toBe('kent-beck');
		expect(toPersonaSlug('already-kebab')).toBe('already-kebab');
	});

	it('handles empty string', () => {
		expect(toPersonaSlug('')).toBe('');
	});

	it('collapses multiple spaces into a single hyphen', () => {
		// \s+ matches one or more spaces — multiple spaces become one hyphen
		expect(toPersonaSlug('as  designer')).toBe('as-designer');
	});
});

describe('getAxisTokens', () => {
	it('returns sorted tokens with all fields', () => {
		const tokens = getAxisTokens(minimalGrammar, 'form');
		expect(tokens.map((t) => t.token)).toEqual(['prose', 'wardley']);
	});

	it('populates description from definitions', () => {
		const tokens = getAxisTokens(minimalGrammar, 'form');
		const wardley = tokens.find((t) => t.token === 'wardley')!;
		expect(wardley.description).toBe(
			'Strategic mapping: user wants to position components on an evolution axis.'
		);
	});

	it('populates label from labels', () => {
		const tokens = getAxisTokens(minimalGrammar, 'form');
		const wardley = tokens.find((t) => t.token === 'wardley')!;
		expect(wardley.label).toBe('Wardley Map');
	});

	it('populates use_when from use_when map', () => {
		const tokens = getAxisTokens(minimalGrammar, 'form');
		const wardley = tokens.find((t) => t.token === 'wardley')!;
		expect(wardley.use_when).toBe('Use when the user wants a Wardley map output.');
	});

	it('populates guidance from guidance map', () => {
		const tokens = getAxisTokens(minimalGrammar, 'form');
		const wardley = tokens.find((t) => t.token === 'wardley')!;
		expect(wardley.guidance).toBe('Use with strategic planning tasks.');
	});

	it('returns empty array for unknown axis', () => {
		expect(getAxisTokens(minimalGrammar, 'nonexistent')).toEqual([]);
	});

	it('handles missing optional fields gracefully', () => {
		const tokens = getAxisTokens(minimalGrammar, 'form');
		const prose = tokens.find((t) => t.token === 'prose')!;
		expect(prose.label).toBe('');
		expect(prose.guidance).toBe('');
		expect(prose.use_when).toBe('');
	});
});

describe('getTaskTokens', () => {
	it('returns sorted task tokens', () => {
		const tokens = getTaskTokens(minimalGrammar);
		expect(tokens.map((t) => t.token)).toEqual(['make', 'show']);
	});

	it('populates description and label', () => {
		const tokens = getTaskTokens(minimalGrammar);
		const show = tokens.find((t) => t.token === 'show')!;
		expect(show.description).toContain('Reveal');
		expect(show.label).toBe('Show');
	});

	it('populates use_when from tasks.use_when (ADR-0142)', () => {
		const tokens = getTaskTokens(minimalGrammar);
		const show = tokens.find((t) => t.token === 'show')!;
		expect(show.use_when).toBe('Explaining or describing something for an audience.');
	});

	it('populates kanji from tasks.kanji (ADR-0143)', () => {
		const tokens = getTaskTokens(minimalGrammar);
		const show = tokens.find((t) => t.token === 'show')!;
		expect(show.kanji).toBe('示');
	});
});

describe('getUsagePatterns', () => {
	it('returns patterns from grammar', () => {
		const patterns = getUsagePatterns(minimalGrammar);
		expect(patterns).toHaveLength(1);
		expect(patterns[0].title).toBe('Example Pattern');
	});

	it('returns empty array when patterns absent', () => {
		const noPatterns = { ...minimalGrammar, patterns: undefined };
		expect(getUsagePatterns(noPatterns)).toEqual([]);
	});
});

describe('getPersonaAxisTokensMeta', () => {
	it('returns sorted tokens with description and use_when from persona docs/use_when', () => {
		const metas = getPersonaAxisTokensMeta(minimalGrammar, 'audience');
		expect(metas.map((m) => m.token)).toEqual(['to managers', 'to product manager']);
		const mgr = metas.find((m) => m.token === 'to managers')!;
		expect(mgr.description).toBe('Audience focused on outcomes and risk.');
		expect(mgr.use_when).toBe('Use when addressing outcome-focused leadership.');
	});

	it('returns empty string for description/use_when when not in docs', () => {
		const metas = getPersonaAxisTokensMeta(minimalGrammar, 'audience');
		const pm = metas.find((m) => m.token === 'to product manager')!;
		expect(pm.description).toBe('');
		expect(pm.use_when).toBe('');
	});

	it('returns empty array for axis with no tokens', () => {
		expect(getPersonaAxisTokensMeta(minimalGrammar, 'voice')).toEqual([]);
	});

	it('handles grammar without persona docs or use_when', () => {
		const noMetaGrammar = {
			...minimalGrammar,
			persona: { ...minimalGrammar.persona, docs: undefined, use_when: undefined }
		};
		const metas = getPersonaAxisTokensMeta(noMetaGrammar, 'audience');
		expect(metas.length).toBe(2);
		expect(metas.every((m) => m.description === '' && m.use_when === '')).toBe(true);
	});

	it('populates kanji from persona.kanji (ADR-0143)', () => {
		const metas = getPersonaAxisTokensMeta(minimalGrammar, 'audience');
		const mgr = metas.find((m) => m.token === 'to managers')!;
		expect(mgr.kanji).toBe('経営');
	});

	it('populates guidance from persona.guidance when present', () => {
		const grammarWithGuidance = {
			...minimalGrammar,
			persona: {
				...minimalGrammar.persona,
				guidance: { audience: { 'to managers': 'Note: very outcome-focused; avoid implementation details.' } }
			}
		};
		const metas = getPersonaAxisTokensMeta(grammarWithGuidance, 'audience');
		const mgr = metas.find((m) => m.token === 'to managers')!;
		expect(mgr.guidance).toBe('Note: very outcome-focused; avoid implementation details.');
	});

	it('returns empty guidance when persona.guidance is absent', () => {
		const metas = getPersonaAxisTokensMeta(minimalGrammar, 'audience');
		expect(metas.every((m) => m.guidance === '')).toBe(true);
	});
});

describe('getPersonaIntentTokens', () => {
	it('returns sorted intent tokens from persona.intent.axis_tokens', () => {
		const grammarWithIntent = {
			...minimalGrammar,
			persona: {
				...minimalGrammar.persona,
				intent: { axis_tokens: { intent: ['persuade', 'announce', 'inform'] } }
			}
		};
		expect(getPersonaIntentTokens(grammarWithIntent)).toEqual(['announce', 'inform', 'persuade']);
	});

	it('returns empty array when persona.intent is absent', () => {
		expect(getPersonaIntentTokens(minimalGrammar)).toEqual([]);
	});
});

// ADR-0144: getMethodTokensByCategory groups method tokens by semantic family.
describe('getMethodTokensByCategory', () => {
	const categoryGrammar: Grammar = {
		...minimalGrammar,
		axes: {
			...minimalGrammar.axes,
			definitions: {
				method: {
					abduce: 'Generate explanatory hypotheses.',
					explore: 'Survey the option space.',
					analysis: 'Describe and structure the situation.',
					diagnose: 'Find the root cause.'
				}
			},
			categories: {
				method: {
					abduce: 'Reasoning',
					explore: 'Exploration',
					analysis: 'Structural',
					diagnose: 'Diagnostic'
				}
			}
		}
	};

	it('returns groups in canonical category order (ADR-0144)', () => {
		const groups = getMethodTokensByCategory(categoryGrammar);
		const cats = groups.map((g) => g.category);
		expect(cats).toEqual(['Reasoning', 'Exploration', 'Structural', 'Diagnostic']);
	});

	it('places each token in its category group', () => {
		const groups = getMethodTokensByCategory(categoryGrammar);
		const reasoning = groups.find((g) => g.category === 'Reasoning')!;
		expect(reasoning.tokens.map((t) => t.token)).toEqual(['abduce']);
	});

	it('places uncategorized tokens in a trailing group with empty category', () => {
		const withExtra: Grammar = {
			...categoryGrammar,
			axes: {
				...categoryGrammar.axes,
				definitions: { method: { ...categoryGrammar.axes.definitions['method'], unknown: 'No category.' } },
				categories: { method: { ...categoryGrammar.axes.categories!['method'] } }
			}
		};
		const groups = getMethodTokensByCategory(withExtra);
		const last = groups[groups.length - 1];
		expect(last.category).toBe('');
		expect(last.tokens.map((t) => t.token)).toContain('unknown');
	});

	it('populates category field on TokenMeta', () => {
		const tokens = getAxisTokens(categoryGrammar, 'method');
		const abduce = tokens.find((t) => t.token === 'abduce')!;
		expect(abduce.category).toBe('Reasoning');
	});
});

// ADR-0144 Phase 2: getStarterPacks
describe('getStarterPacks', () => {
	const grammarWithPacks: Grammar = {
		...minimalGrammar,
		starter_packs: [
			{ name: 'debug', framing: 'Diagnosing a bug or system failure', command: 'bar build probe diagnose adversarial unknowns' },
			{ name: 'design', framing: 'Architectural or interface design decision', command: 'bar build show branch trade balance' },
		]
	};

	it('returns starter packs from grammar', () => {
		const packs = getStarterPacks(grammarWithPacks);
		expect(packs).toHaveLength(2);
		expect(packs[0].name).toBe('debug');
		expect(packs[0].framing).toBe('Diagnosing a bug or system failure');
		expect(packs[0].command).toBe('bar build probe diagnose adversarial unknowns');
	});

	it('returns empty array when starter_packs absent', () => {
		expect(getStarterPacks(minimalGrammar)).toEqual([]);
	});

	it('each pack has name, framing, command strings', () => {
		const packs = getStarterPacks(grammarWithPacks);
		for (const pack of packs) {
			expect(typeof pack.name).toBe('string');
			expect(typeof pack.framing).toBe('string');
			expect(typeof pack.command).toBe('string');
		}
	});
});

// Minimal grammar with cross_axis_composition for form/channel conflict testing
const grammarWithComposition: Grammar = {
	...minimalGrammar,
	axes: {
		...minimalGrammar.axes,
		cross_axis_composition: {
			form: {
				faq: {
					channel: {
						natural: ['plain', 'slack'],
						cautionary: {
							shellscript: 'Q&A prose cannot be rendered as shell code',
							code: 'Q&A prose cannot be rendered as code-only output'
						}
					}
				}
			},
			channel: {
				gherkin: {
					form: {
						natural: [],
						cautionary: {
							recipe: 'Recipe prose conflicts with Gherkin format'
						}
					}
				}
			}
		}
	}
};

describe('getReverseChipState — form/channel cross-axis traffic lights', () => {
	it('returns cautionary for a form chip when a conflicting channel is active', () => {
		// faq (form) chip should show cautionary when shellscript (channel) is selected
		const state = getReverseChipState(grammarWithComposition, { channel: ['shellscript'] }, 'form', 'faq');
		expect(state).toBe('cautionary');
	});

	it('returns natural for a form chip when a compatible channel is active', () => {
		// faq (form) chip should show natural when plain (channel) is selected
		const state = getReverseChipState(grammarWithComposition, { channel: ['plain'] }, 'form', 'faq');
		expect(state).toBe('natural');
	});

	it('returns cautionary for a channel chip when a conflicting form is active', () => {
		// shellscript (channel) chip should show cautionary when faq (form) is selected
		const state = getReverseChipState(grammarWithComposition, { form: ['faq'] }, 'channel', 'shellscript');
		expect(state).toBe('cautionary');
	});

	it('returns cautionary for a channel chip with composition data when a conflicting form is active', () => {
		// gherkin (channel) chip has its own form.cautionary entry; recipe form should trigger it
		const state = getReverseChipState(grammarWithComposition, { form: ['recipe'] }, 'channel', 'gherkin');
		expect(state).toBe('cautionary');
	});

	it('returns null for a form chip with no active conflicting tokens', () => {
		const state = getReverseChipState(grammarWithComposition, { channel: ['diagram'] }, 'form', 'faq');
		expect(state).toBeNull();
	});
});

describe('findConflicts — cross_axis_composition cautionary pairs', () => {
	it('detects form+channel conflict via cross_axis_composition', () => {
		const conflicts = findConflicts(grammarWithComposition, {
			form: ['faq'],
			channel: ['shellscript']
		});
		expect(conflicts.length).toBeGreaterThan(0);
		const conflict = conflicts[0];
		expect([conflict.tokenA, conflict.tokenB].sort()).toEqual(['faq', 'shellscript']);
	});

	it('returns no conflict when form and channel are compatible', () => {
		const conflicts = findConflicts(grammarWithComposition, {
			form: ['faq'],
			channel: ['plain']
		});
		expect(conflicts).toHaveLength(0);
	});

	it('returns no conflict when only one token is selected', () => {
		const conflicts = findConflicts(grammarWithComposition, {
			form: ['faq']
		});
		expect(conflicts).toHaveLength(0);
	});
});
