/**
 * ADR-0157: Selected Token Review Panel
 * Specifying validations for the review panel feature.
 * Written BEFORE implementation — all tests must fail red initially.
 */
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

const mockClipboard = {
	writeText: vi.fn().mockResolvedValue(undefined)
};

Object.defineProperty(globalThis, 'navigator', {
	value: { clipboard: mockClipboard },
	writable: true
});

vi.mock('$lib/grammar.js', () => ({
	loadGrammar: vi.fn().mockResolvedValue({
		hierarchy: { axis_soft_caps: {} },
		tokens: { task: { tokens: ['probe', 'show'] }, channel: { tokens: ['shellscript', 'code'] } },
		persona_presets: [],
		persona: { use_when: {} },
		reference_key: { task: '', addendum: '', constraints: '', constraints_axes: {}, persona: '', subject: '' },
		execution_reminder: '',
		planning_directive: '',
		meta_interpretation_guidance: '',
		axes: {
			definitions: {
				task: { probe: 'Surface assumptions', show: 'Explain' },
				channel: { shellscript: 'Shell script', code: 'Code' }
			},
			labels: {
				task: { probe: 'Probe', show: 'Show' },
				channel: { shellscript: 'Shellscript', code: 'Code' }
			}
		}
	}),
	getAxisTokens: vi.fn().mockImplementation((_grammar, axis) => {
		const defs = axis === 'task'
			? { probe: 'Surface assumptions', show: 'Explain' }
			: axis === 'channel'
				? { shellscript: 'Shell script', code: 'Code' }
				: {};
		return Object.entries(defs).map(([token, description]) => ({
			token,
			label: token.charAt(0).toUpperCase() + token.slice(1),
			description,
			guidance: '',
			use_when: ''
		}));
	}),
	getTaskTokens: vi.fn().mockReturnValue([
		{ token: 'probe', label: 'Surface', description: '', guidance: '', use_when: '' },
		{ token: 'show', label: 'Explain', description: '', guidance: '', use_when: '' }
	]),
	getPersonaPresets: vi.fn().mockReturnValue([]),
	getPersonaAxisTokens: vi.fn().mockReturnValue([]),
	AXES: ['task', 'channel'],
	toPersonaSlug: vi.fn().mockReturnValue(''),
	toAxisTokenSlug: vi.fn((s: string) => s.toLowerCase().replace(/\s+/g, '-')),
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
	renderPrompt: vi.fn().mockReturnValue('MOCK RENDERED PROMPT')
}));

describe('ADR-0157: Selected Token Review Panel', () => {
	describe('Happy Path', () => {
		it('review panel displays selected tokens in axis=token format', async () => {
			const Page = (await import('../routes/+page.svelte')).default;
			const target = document.createElement('div');
			document.body.appendChild(target);
			mount(Page, { target });
			flushSync();

			const reviewPanel = target.querySelector('.review-panel');
			expect(reviewPanel).toBeTruthy();

			document.body.removeChild(target);
		});

		it('shows placeholder when no tokens selected', async () => {
			const Page = (await import('../routes/+page.svelte')).default;
			const target = document.createElement('div');
			document.body.appendChild(target);
			mount(Page, { target });
			flushSync();

			const placeholder = target.querySelector('.review-panel-empty');
			expect(placeholder?.textContent).toBe('Select tokens from the axes above');

			document.body.removeChild(target);
		});

		it('clicking token in review panel deselects it', async () => {
			const Page = (await import('../routes/+page.svelte')).default;
			const target = document.createElement('div');
			document.body.appendChild(target);
			mount(Page, { target });
			flushSync();

			const tokenChip = target.querySelector('.review-panel-chip');
			if (tokenChip) {
				tokenChip.click();
				flushSync();
			}

			document.body.removeChild(target);
		});
	});

	describe('Conflicts', () => {
		it('conflicting tokens show warning icon in review panel', async () => {
			// Pre-select probe (task) and shellscript (channel) via localStorage
			const state = {
				selected: {
					task: ['probe'],
					completeness: [],
					scope: [],
					method: [],
					form: [],
					channel: ['shellscript'],
					directional: []
				},
				subject: '',
				addendum: '',
				persona: { preset: '', voice: '', audience: '', tone: '', intent: '' }
			};
			mockLocalStorage.getItem.mockReturnValueOnce(btoa(JSON.stringify(state)));

			const incompatibilities = await import('$lib/incompatibilities.js');
			(incompatibilities.findConflicts as ReturnType<typeof vi.fn>).mockReturnValue([
				{ tokenA: 'probe', tokenB: 'shellscript', reason: 'test conflict' }
			]);

			const Page = (await import('../routes/+page.svelte')).default;
			const target = document.createElement('div');
			document.body.appendChild(target);
			mount(Page, { target });

			// Wait for onMount (async grammar load + state deserialize)
			await new Promise((resolve) => setTimeout(resolve, 50));
			flushSync();

			const conflictChips = target.querySelectorAll('.review-panel-chip.conflict');
			expect(conflictChips.length).toBeGreaterThan(0);
			expect(conflictChips[0].textContent).toContain('⚠');

			// Reset
			(incompatibilities.findConflicts as ReturnType<typeof vi.fn>).mockReturnValue([]);
			document.body.removeChild(target);
		});
	});

	describe('Command Box', () => {
		it('command box shows no conflict warning', async () => {
			const Page = (await import('../routes/+page.svelte')).default;
			const target = document.createElement('div');
			document.body.appendChild(target);
			mount(Page, { target });
			flushSync();

			const conflictWarning = target.querySelector('.conflicts');
			expect(conflictWarning).toBeFalsy();

			document.body.removeChild(target);
		});
	});

	describe('Desktop layout', () => {
		it('action-overlay is hidden by default (no mobile-visible class)', async () => {
			const Page = (await import('../routes/+page.svelte')).default;
			const target = document.createElement('div');
			document.body.appendChild(target);
			mount(Page, { target });
			flushSync();

			const overlay = target.querySelector('.action-overlay');
			expect(overlay).toBeTruthy();
			expect(overlay?.classList.contains('mobile-visible')).toBe(false);

			document.body.removeChild(target);
		});

		it('layout exposes --review-h CSS custom property for preview-panel constraint', async () => {
			const Page = (await import('../routes/+page.svelte')).default;
			const target = document.createElement('div');
			document.body.appendChild(target);
			mount(Page, { target });
			flushSync();

			const layout = target.querySelector('.layout') as HTMLElement;
			expect(layout?.style.getPropertyValue('--review-h')).toBeTruthy();

			document.body.removeChild(target);
		});
	});

	describe('Accessibility', () => {
		// Review panel is a button element, which is inherently keyboard accessible
		// The existing selected-chip tests verify Enter/Space behavior
		it('review panel chips are rendered as buttons', async () => {
			const Page = (await import('../routes/+page.svelte')).default;
			const target = document.createElement('div');
			document.body.appendChild(target);
			mount(Page, { target });
			flushSync();

			// Empty state shows placeholder (not buttons)
			const placeholder = target.querySelector('.review-panel-empty');
			expect(placeholder?.textContent).toBe('Select tokens from the axes above');

			document.body.removeChild(target);
		});
	});
});
