<script lang="ts">
	import type { TokenMeta } from './grammar.js';

	interface Props {
		axis: string;
		tokens: TokenMeta[];
		selected: string[];
		maxSelect: number;
		onToggle: (token: string) => void;
	}

	let { axis, tokens, selected, maxSelect, onToggle }: Props = $props();

	let filter = $state('');

	let filtered = $derived(
		filter.trim()
			? tokens.filter(
					(t) =>
						t.token.includes(filter.toLowerCase()) ||
						t.label.toLowerCase().includes(filter.toLowerCase())
				)
			: tokens
	);
</script>

<div class="axis-panel">
	<div class="axis-header">
		<span class="axis-name">{axis}</span>
		<span class="axis-cap">0–{maxSelect}</span>
	</div>

	{#if tokens.length > 8}
		<input
			class="filter-input"
			type="text"
			placeholder="filter…"
			bind:value={filter}
		/>
	{/if}

	<div class="token-grid">
		{#each filtered as meta (meta.token)}
			{@const isSelected = selected.includes(meta.token)}
			{@const atCap = !isSelected && selected.length >= maxSelect}
			<!-- svelte-ignore a11y_click_events_have_key_events -->
			<!-- svelte-ignore a11y_no_static_element_interactions -->
			<div
				class="token-chip"
				class:selected={isSelected}
				class:disabled={atCap}
				onclick={() => !atCap && onToggle(meta.token)}
				title={[meta.description, meta.use_when ? `When to use: ${meta.use_when}` : '', meta.guidance ? `Note: ${meta.guidance}` : ''].filter(Boolean).join('\n\n')}
			>
				<code>{meta.token}</code>
				{#if meta.label}
					<span class="token-label">{meta.label}</span>
				{/if}
				{#if meta.use_when}
					<span class="use-when-dot" title="Has 'when to use' guidance">●</span>
				{/if}
			</div>
		{/each}
	</div>
</div>

<style>
	.axis-panel {
		margin-bottom: 1.5rem;
	}

	.axis-header {
		display: flex;
		align-items: baseline;
		gap: 0.5rem;
		margin-bottom: 0.5rem;
	}

	.axis-name {
		font-size: 0.85rem;
		font-weight: 600;
		text-transform: uppercase;
		letter-spacing: 0.05em;
		color: var(--color-accent);
	}

	.axis-cap {
		font-size: 0.75rem;
		color: var(--color-text-muted);
	}

	.filter-input {
		width: 100%;
		padding: 0.3rem 0.5rem;
		background: var(--color-bg);
		border: 1px solid var(--color-border);
		border-radius: var(--radius);
		color: var(--color-text);
		font-size: 0.8rem;
		margin-bottom: 0.5rem;
	}

	.token-grid {
		display: flex;
		flex-wrap: wrap;
		gap: 0.4rem;
	}

	.token-chip {
		display: flex;
		align-items: center;
		gap: 0.3rem;
		padding: 0.25rem 0.5rem;
		background: var(--color-surface);
		border: 1px solid var(--color-border);
		border-radius: var(--radius);
		cursor: pointer;
		transition: border-color 0.1s, background 0.1s;
		user-select: none;
	}

	.token-chip:hover:not(.disabled) {
		border-color: var(--color-accent-muted);
	}

	.token-chip.selected {
		background: var(--color-accent-muted);
		border-color: var(--color-accent);
	}

	.token-chip.disabled {
		opacity: 0.4;
		cursor: not-allowed;
	}

	code {
		font-family: var(--font-mono);
		font-size: 0.8rem;
	}

	.token-label {
		font-size: 0.7rem;
		color: var(--color-text-muted);
		max-width: 12rem;
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}

	.use-when-dot {
		font-size: 0.5rem;
		color: var(--color-accent);
		line-height: 1;
	}
</style>
