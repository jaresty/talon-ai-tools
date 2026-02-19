import { describe, it, expect } from 'vitest';
import {
	getAxisTokens,
	getTaskTokens,
	getUsagePatterns,
	getPersonaAxisTokensMeta,
	toPersonaSlug,
	type Grammar
} from './grammar.js';

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
		}
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
		use_when: { audience: { 'to managers': 'Use when addressing outcome-focused leadership.' } }
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
});
