<script lang="ts">
	import type { HistoryEntry } from '$lib/history.js';

	let {
		historyEntries,
		onLoad,
		onDelete,
		onClearAll
	}: {
		historyEntries: HistoryEntry[];
		onLoad: (hash: string) => void;
		onDelete: (ts: string) => void;
		onClearAll: () => void;
	} = $props();
</script>

<details class="history-panel">
	<summary class="history-summary">History</summary>
	{#if historyEntries.length === 0}
		<p class="history-empty">No history yet. History is saved when you copy or share a prompt.</p>
	{:else}
		<div class="history-header-row">
			<button class="history-clear-btn" onclick={onClearAll}>Clear all</button>
		</div>
		<ul class="history-list">
			{#each historyEntries as entry (entry.ts)}
				<li class="history-entry">
					<button class="history-entry-load" onclick={() => onLoad(entry.hash)}>
						<code class="history-entry-command">{entry.command_preview || '(no command)'}</code>
						{#if entry.subject_preview}
							<span class="history-entry-subject">{entry.subject_preview}</span>
						{/if}
					</button>
					<button class="history-delete-btn" onclick={() => onDelete(entry.ts)}>✕</button>
				</li>
			{/each}
		</ul>
	{/if}
</details>

<style>
	.history-panel {
		margin-bottom: 0.75rem;
		border: 1px solid var(--color-border);
		border-radius: var(--radius);
		overflow: hidden;
	}
	.history-summary {
		padding: 0.4rem 0.75rem;
		font-size: 0.75rem;
		text-transform: uppercase;
		letter-spacing: 0.05em;
		cursor: pointer;
		user-select: none;
		background: var(--color-surface);
		color: var(--color-text-muted);
	}
	.history-empty {
		font-size: 0.8rem;
		color: var(--color-text-muted);
		padding: 0.5rem 0.75rem 0.75rem;
		margin: 0;
	}
	.history-header-row {
		display: flex;
		justify-content: flex-end;
		padding: 0.4rem 0.75rem 0.1rem;
	}
	.history-clear-btn {
		font-size: 0.75rem;
		color: var(--color-text-muted);
		background: none;
		border: none;
		cursor: pointer;
		padding: 0.1rem 0.25rem;
	}
	.history-clear-btn:hover { color: #f7768e; }
	.history-list { list-style: none; margin: 0; padding: 0.25rem 0 0.5rem; }
	.history-entry {
		display: flex;
		align-items: center;
		gap: 0.25rem;
		padding: 0 0.5rem;
		border-bottom: 1px solid var(--color-border);
	}
	.history-entry:last-child { border-bottom: none; }
	.history-entry-load {
		flex: 1;
		text-align: left;
		background: none;
		border: none;
		cursor: pointer;
		padding: 0.35rem 0.25rem;
		min-width: 0;
	}
	.history-entry-command {
		display: block;
		font-size: 0.75rem;
		color: var(--color-accent);
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
	}
	.history-entry-subject {
		display: block;
		font-size: 0.72rem;
		color: var(--color-text-muted);
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
	}
	.history-delete-btn {
		background: none;
		border: none;
		cursor: pointer;
		color: var(--color-text-muted);
		font-size: 0.8rem;
		padding: 0.2rem 0.35rem;
		flex-shrink: 0;
	}
	.history-delete-btn:hover { color: #f7768e; }
</style>
