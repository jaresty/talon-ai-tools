import { flushSync } from 'svelte';
import { mount } from 'svelte';
import { vi, describe, it, expect, beforeEach } from 'vitest';

const mockLocalStorage = {
	getItem: vi.fn(() => null),
	setItem: vi.fn(),
	removeItem: vi.fn(),
	clear: vi.fn()
};

Object.defineProperty(globalThis, 'localStorage', {
	value: mockLocalStorage,
	writable: true
});

vi.mock('$lib/grammar.js', () => ({
	loadGrammar: vi.fn().mockResolvedValue({
		hierarchy: { axis_soft_caps: {} },
		tokens: {},
		persona_presets: [],
		reference_key: { task: '', addendum: '', constraints: '', constraints_axes: {}, persona: '', subject: '' },
		execution_reminder: '',
		planning_directive: '',
		meta_interpretation_guidance: '',
		subject_framing: ''
	}),
	getAxisTokens: vi.fn().mockReturnValue([]),
	getTaskTokens: vi.fn().mockReturnValue([{ token: 'show', label: 'Explain' }]),
	getPersonaPresets: vi.fn().mockReturnValue([]),
	getPersonaAxisTokens: vi.fn().mockReturnValue([]),
	getPersonaAxisTokensMeta: vi.fn().mockReturnValue([]),
	AXES: ['completeness', 'scope', 'method', 'form', 'channel', 'directional'],
	toPersonaSlug: vi.fn().mockReturnValue(''),
	getUsagePatterns: vi.fn().mockReturnValue([]),
	getStarterPacks: vi.fn().mockReturnValue([]),
	getCompositionData: vi.fn().mockReturnValue(null),
	getChipState: vi.fn().mockReturnValue(null),
	getReverseChipState: vi.fn().mockReturnValue(null),
	getChipStateWithReason: vi.fn().mockReturnValue({ state: null, naturalWith: [], cautionWith: [] })
}));

vi.mock('$lib/incompatibilities.js', () => ({
	findConflicts: vi.fn().mockReturnValue([])
}));

vi.mock('$lib/renderPrompt.js', () => ({
	renderPrompt: vi.fn().mockReturnValue('MOCK RENDERED PROMPT TEXT')
}));

describe('Page — subject/addendum placement', () => {
	let container: HTMLDivElement;

	beforeEach(() => {
		vi.clearAllMocks();
		container = document.createElement('div');
		document.body.appendChild(container);
	});

	it('addendum textarea is inside the task tab section', async () => {
		const { default: Page } = await import('../routes/+page.svelte');
		mount(Page, { target: container });
		await new Promise(r => setTimeout(r, 100));

		const taskTab = container.querySelector('.task-tab-section');
		expect(taskTab).toBeTruthy();
		const addendumInTask = taskTab!.querySelector('textarea[data-field="addendum"]');
		expect(addendumInTask).toBeTruthy();
	});

	it('subject textarea appears before the rendered prompt', async () => {
		const { default: Page } = await import('../routes/+page.svelte');
		mount(Page, { target: container });
		await new Promise(r => setTimeout(r, 100));

		const subjectTextarea = container.querySelector('textarea[data-field="subject"]');
		const renderedPrompt = container.querySelector('.prompt-preview-section');
		expect(subjectTextarea).toBeTruthy();
		expect(renderedPrompt).toBeTruthy();

		const position = subjectTextarea!.compareDocumentPosition(renderedPrompt!);
		// DOCUMENT_POSITION_FOLLOWING = 4: renderedPrompt comes after subjectTextarea
		expect(position & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
	});
});
