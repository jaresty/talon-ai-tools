import { flushSync, mount } from 'svelte';
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest';
import type { SpaPreset } from './presets.js';

describe('PresetsPanel', () => {
	let container: HTMLDivElement;

	const mockPresets: SpaPreset[] = [
		{ name: 'my-preset', tokens: ['make', 'full'], selected: { task: ['make'] }, persona: {} },
		{ name: 'other-preset', tokens: ['show'], selected: { task: ['show'] }, persona: {} }
	];

	beforeEach(() => {
		container = document.createElement('div');
		document.body.appendChild(container);
	});

	afterEach(() => {
		document.body.removeChild(container);
		vi.clearAllMocks();
	});

	async function mountPanel(props: Record<string, unknown> = {}) {
		const { default: PresetsPanel } = await import('./PresetsPanel.svelte');
		mount(PresetsPanel, {
			target: container,
			props: {
				savedPresets: [],
				presetNameInput: '',
				presetSaved: false,
				onSave: vi.fn(),
				onLoad: vi.fn(),
				onDelete: vi.fn(),
				onNameInput: vi.fn(),
				...props
			}
		});
		flushSync();
	}

	it('PresetsPanel renders empty state', async () => {
		await mountPanel();
		expect(container.querySelector('.presets-empty')).toBeTruthy();
		expect(container.querySelector('.presets-empty')?.textContent?.trim()).toBe('No presets saved.');
	});

	it('renders preset list when presets provided', async () => {
		await mountPanel({ savedPresets: mockPresets });
		expect(container.querySelector('.presets-list')).toBeTruthy();
		expect(container.textContent).toContain('my-preset');
		expect(container.textContent).toContain('other-preset');
	});

	it('save button is disabled when presetNameInput is empty', async () => {
		await mountPanel({ presetNameInput: '' });
		const btn = container.querySelector('.presets-save-btn') as HTMLButtonElement;
		expect(btn.disabled).toBe(true);
	});

	it('save button is enabled when presetNameInput has text', async () => {
		await mountPanel({ presetNameInput: 'my name' });
		const btn = container.querySelector('.presets-save-btn') as HTMLButtonElement;
		expect(btn.disabled).toBe(false);
	});

	it('clicking save button calls onSave', async () => {
		const onSave = vi.fn();
		await mountPanel({ presetNameInput: 'test', onSave });
		(container.querySelector('.presets-save-btn') as HTMLButtonElement).click();
		flushSync();
		expect(onSave).toHaveBeenCalledOnce();
	});

	it('clicking load button calls onLoad with preset', async () => {
		const onLoad = vi.fn();
		await mountPanel({ savedPresets: mockPresets, onLoad });
		(container.querySelector('.preset-load-btn') as HTMLButtonElement).click();
		flushSync();
		expect(onLoad).toHaveBeenCalledWith(mockPresets[0]);
	});

	it('clicking delete button calls onDelete with preset name', async () => {
		const onDelete = vi.fn();
		await mountPanel({ savedPresets: mockPresets, onDelete });
		(container.querySelector('.preset-delete-btn') as HTMLButtonElement).click();
		flushSync();
		expect(onDelete).toHaveBeenCalledWith('my-preset');
	});

	it('shows token list for each preset', async () => {
		await mountPanel({ savedPresets: mockPresets });
		expect(container.textContent).toContain('make full');
	});

	it('shows saved confirmation when presetSaved is true', async () => {
		await mountPanel({ presetNameInput: 'x', presetSaved: true });
		const btn = container.querySelector('.presets-save-btn');
		expect(btn?.textContent?.trim()).toBe('✓ Saved');
	});
});
