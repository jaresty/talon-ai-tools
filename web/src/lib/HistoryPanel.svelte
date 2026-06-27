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
