import { flushSync, mount } from 'svelte';
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest';

describe('ReviewPanel', () => {
	let container: HTMLDivElement;

	const mockSelected = { method: ['diagnose', 'induce'], scope: ['full'] };
	const mockPersona = { preset: '', voice: 'direct', audience: '', tone: '', intent: '' };
	const mockConflicts = [{ tokenA: 'induce', tokenB: 'diagnose', reason: 'conflict' }];

	beforeEach(() => {
		container = document.createElement('div');
		document.body.appendChild(container);
	});

	afterEach(() => {
		document.body.removeChild(container);
		vi.clearAllMocks();
	});

	async function mountPanel(props: Record<string, unknown> = {}) {
		const { default: ReviewPanel } = await import('./ReviewPanel.svelte');
		mount(ReviewPanel, {
			target: container,
			props: {
				selected: {},
				persona: { preset: '', voice: '', audience: '', tone: '', intent: '' },
				conflicts: [],
				hasSelectedTokens: false,
				onToggle: vi.fn(),
				onClearPersonaField: vi.fn(),
				...props
			}
		});
		flushSync();
	}

	it('ReviewPanel renders empty state', async () => {
		await mountPanel();
		expect(container.textContent).toContain('Select tokens from the axes above');
	});

	it('renders selected axis tokens as chips', async () => {
		await mountPanel({ selected: mockSelected, hasSelectedTokens: true });
		expect(container.textContent).toContain('method=diagnose');
		expect(container.textContent).toContain('scope=full');
	});

	it('renders persona voice chip when voice is set', async () => {
		await mountPanel({ persona: mockPersona, hasSelectedTokens: true });
		expect(container.textContent).toContain('voice=direct');
	});

	it('renders persona preset chip when preset is set', async () => {
		const persona = { preset: 'senior-dev', voice: '', audience: '', tone: '', intent: '' };
		await mountPanel({ persona, hasSelectedTokens: true });
		expect(container.textContent).toContain('persona=senior-dev');
	});

	it('marks conflicted tokens with conflict class', async () => {
		await mountPanel({ selected: mockSelected, conflicts: mockConflicts, hasSelectedTokens: true });
		const chips = container.querySelectorAll('.review-panel-chip');
		const conflictChips = Array.from(chips).filter(c => c.classList.contains('conflict'));
		expect(conflictChips.length).toBeGreaterThan(0);
	});

	it('clicking a token chip calls onToggle with axis and token', async () => {
		const onToggle = vi.fn();
		await mountPanel({ selected: mockSelected, hasSelectedTokens: true, onToggle });
		const chips = Array.from(container.querySelectorAll('.review-panel-chip'));
		const methodChip = chips.find(c => c.textContent?.includes('method=diagnose'));
		(methodChip as HTMLButtonElement).click();
		flushSync();
		expect(onToggle).toHaveBeenCalledWith('method', 'diagnose');
	});

	it('clicking voice chip calls onClearPersonaField with voice field', async () => {
		const onClearPersonaField = vi.fn();
		await mountPanel({ persona: mockPersona, hasSelectedTokens: true, onClearPersonaField });
		const chips = Array.from(container.querySelectorAll('.review-panel-chip'));
		const voiceChip = chips.find(c => c.textContent?.includes('voice=direct'));
		(voiceChip as HTMLButtonElement).click();
		flushSync();
		expect(onClearPersonaField).toHaveBeenCalledWith('voice');
	});

	it('shows conflict warning indicator on conflicted chips', async () => {
		await mountPanel({ selected: mockSelected, conflicts: mockConflicts, hasSelectedTokens: true });
		expect(container.textContent).toContain('⚠');
	});
});
