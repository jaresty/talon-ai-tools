import { flushSync, mount } from 'svelte';
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest';
import type { HistoryEntry } from './history.js';

describe('HistoryPanel', () => {
	let container: HTMLDivElement;

	const mockEntries: HistoryEntry[] = [
		{ ts: '2026-01-01T00:00:00.000Z-0', hash: 'abc', trigger: 'copy', command_preview: 'bar build show', subject_preview: 'my subject' },
		{ ts: '2026-01-01T00:00:01.000Z-1', hash: 'def', trigger: 'share', command_preview: 'bar build fix', subject_preview: '' }
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
		const { default: HistoryPanel } = await import('./HistoryPanel.svelte');
		mount(HistoryPanel, {
			target: container,
			props: {
				historyEntries: [],
				onLoad: vi.fn(),
				onDelete: vi.fn(),
				onClearAll: vi.fn(),
				...props
			}
		});
		flushSync();
	}

	it('HistoryPanel renders empty state', async () => {
		await mountPanel();
		expect(container.querySelector('.history-empty')).toBeTruthy();
		expect(container.textContent).toContain('No history yet');
	});

	it('renders history entries when provided', async () => {
		await mountPanel({ historyEntries: mockEntries });
		expect(container.querySelector('.history-list')).toBeTruthy();
		expect(container.textContent).toContain('bar build show');
		expect(container.textContent).toContain('bar build fix');
	});

	it('shows subject preview when present', async () => {
		await mountPanel({ historyEntries: mockEntries });
		expect(container.textContent).toContain('my subject');
	});

	it('shows clear all button when entries exist', async () => {
		await mountPanel({ historyEntries: mockEntries });
		expect(container.querySelector('.history-clear-btn')).toBeTruthy();
	});

	it('does not show clear all button when empty', async () => {
		await mountPanel();
		expect(container.querySelector('.history-clear-btn')).toBeFalsy();
	});

	it('clicking clear all calls onClearAll', async () => {
		const onClearAll = vi.fn();
		await mountPanel({ historyEntries: mockEntries, onClearAll });
		(container.querySelector('.history-clear-btn') as HTMLButtonElement).click();
		flushSync();
		expect(onClearAll).toHaveBeenCalledOnce();
	});

	it('clicking an entry calls onLoad with its hash', async () => {
		const onLoad = vi.fn();
		await mountPanel({ historyEntries: mockEntries, onLoad });
		(container.querySelector('.history-entry-load') as HTMLButtonElement).click();
		flushSync();
		expect(onLoad).toHaveBeenCalledWith('abc');
	});

	it('clicking delete calls onDelete with entry ts', async () => {
		const onDelete = vi.fn();
		await mountPanel({ historyEntries: mockEntries, onDelete });
		(container.querySelector('.history-delete-btn') as HTMLButtonElement).click();
		flushSync();
		expect(onDelete).toHaveBeenCalledWith('2026-01-01T00:00:00.000Z-0');
	});
});
