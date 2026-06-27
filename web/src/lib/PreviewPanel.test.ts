import { flushSync, mount } from 'svelte';
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest';
import type { SpaPreset } from './presets.js';
import type { HistoryEntry } from './history.js';

vi.mock('$lib/LLMPanel.svelte', () => ({
	default: vi.fn(() => ({ c: vi.fn(), m: vi.fn(), d: vi.fn(), l: vi.fn() }))
}));

describe('PreviewPanel', () => {
	let container: HTMLDivElement;

	const defaultProps = {
		command: 'bar build show full',
		promptText: 'This is the rendered prompt text.',
		showPreview: true,
		copied: false,
		copiedPrompt: false,
		shared: false,
		linkCopied: false,
		savedPresets: [] as SpaPreset[],
		presetNameInput: '',
		presetSaved: false,
		historyEntries: [] as HistoryEntry[],
		onTogglePreview: vi.fn(),
		onCopyCommand: vi.fn(),
		onCopyPrompt: vi.fn(),
		onSharePrompt: vi.fn(),
		onShareLink: vi.fn(),
		onCopyLink: vi.fn(),
		onClear: vi.fn(),
		onSavePreset: vi.fn(),
		onLoadPreset: vi.fn(),
		onDeletePreset: vi.fn(),
		onLoadHistory: vi.fn(),
		onDeleteHistory: vi.fn(),
		onClearHistory: vi.fn(),
		onNameInput: vi.fn()
	};

	beforeEach(() => {
		container = document.createElement('div');
		document.body.appendChild(container);
	});

	afterEach(() => {
		document.body.removeChild(container);
		vi.clearAllMocks();
	});

	async function mountPanel(props: Record<string, unknown> = {}) {
		const { default: PreviewPanel } = await import('./PreviewPanel.svelte');
		mount(PreviewPanel, { target: container, props: { ...defaultProps, ...props } });
		flushSync();
	}

	it('PreviewPanel renders command text', async () => {
		await mountPanel();
		expect(container.querySelector('.command')?.textContent).toBe('bar build show full');
	});

	it('renders rendered prompt text', async () => {
		await mountPanel();
		expect(container.querySelector('.prompt-preview')?.textContent).toBe('This is the rendered prompt text.');
	});

	it('shows Copy cmd button', async () => {
		await mountPanel();
		expect(container.querySelector('.copy-btn')).toBeTruthy();
		expect(container.querySelector('.copy-btn')?.textContent?.trim()).toBe('Copy cmd');
	});

	it('shows copied label when copied is true', async () => {
		await mountPanel({ copied: true });
		const copyBtn = container.querySelector('.copy-btn');
		expect(copyBtn?.textContent?.trim()).toBe('✓ Copied');
	});

	it('clicking copy cmd button calls onCopyCommand', async () => {
		const onCopyCommand = vi.fn();
		await mountPanel({ onCopyCommand });
		(container.querySelector('.copy-btn') as HTMLButtonElement).click();
		flushSync();
		expect(onCopyCommand).toHaveBeenCalledOnce();
	});

	it('preview-panel section is visible when showPreview is true', async () => {
		await mountPanel({ showPreview: true });
		expect(container.querySelector('.preview-panel.visible')).toBeTruthy();
	});

	it('preview-panel section is not visible when showPreview is false', async () => {
		await mountPanel({ showPreview: false });
		expect(container.querySelector('.preview-panel.visible')).toBeFalsy();
	});

	it('clicking preview toggle button calls onTogglePreview', async () => {
		const onTogglePreview = vi.fn();
		await mountPanel({ onTogglePreview });
		(container.querySelector('.preview-toggle') as HTMLButtonElement).click();
		flushSync();
		expect(onTogglePreview).toHaveBeenCalledOnce();
	});
});
