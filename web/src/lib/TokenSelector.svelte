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
	let activeToken = $state<string | null>(null);

	let filtered = $derived(
		filter.trim()
			? tokens.filter(
					(t) =>
						t.token.includes(filter.toLowerCase()) ||
						t.label.toLowerCase().includes(filter.toLowerCase())
				)
			: tokens
	);

	let activeMeta = $derived(tokens.find((t) => t.token === activeToken) ?? null);

	function handleChipClick(meta: TokenMeta, atCap: boolean) {
		if (!atCap) onToggle(meta.token);
		activeToken = activeToken === meta.token ? null : meta.token;
	}
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
			{@const isActive = activeToken === meta.token}
			<!-- svelte-ignore a11y_click_events_have_key_events -->
			<!-- svelte-ignore a11y_no_static_element_interactions -->
			<div
				class="token-chip"
				class:selected={isSelected}
				class:disabled={atCap}
				class:active-meta={isActive}
				onclick={() => handleChipClick(meta, atCap)}
			>
				<code>{meta.token}</code>
				{#if meta.label}
					<span class="token-label">{meta.label}</span>
				{/if}
				{#if meta.use_when}
					<span class="use-when-dot">●</span>
				{/if}
			</div>
		{/each}
	</div>

	{#if activeMeta}
		<div class="meta-panel">
			<div class="meta-header">
				<code class="meta-token">{activeMeta.token}</code>
				{#if activeMeta.label}
					<span class="meta-label">{activeMeta.label}</span>
				{/if}
				<!-- svelte-ignore a11y_click_events_have_key_events -->
				<!-- svelte-ignore a11y_no_static_element_interactions -->
				<span class="meta-close" onclick={() => (activeToken = null)}>✕</span>
			</div>
			{#if activeMeta.description}
				<p class="meta-description">{activeMeta.description}</p>
			{/if}
			{#if activeMeta.use_when}
				<div class="meta-section">
					<span class="meta-section-label">When to use</span>
					<p>{activeMeta.use_when}</p>
				</div>
			{/if}
			{#if activeMeta.guidance}
				<div class="meta-section meta-note">
					<span class="meta-section-label">Notes</span>
					<p>{activeMeta.guidance}</p>
				</div>
			{/if}
		</div>
	{/if}
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

	.token-chip.active-meta {
		outline: 2px solid var(--color-accent);
		outline-offset: 1px;
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

	.meta-panel {
		margin-top: 0.6rem;
		padding: 0.75rem;
		background: var(--color-surface);
		border: 1px solid var(--color-accent-muted);
		border-radius: var(--radius);
		font-size: 0.8rem;
		line-height: 1.5;
	}

	.meta-header {
		display: flex;
		align-items: baseline;
		gap: 0.5rem;
		margin-bottom: 0.4rem;
	}

	.meta-token {
		font-family: var(--font-mono);
		font-size: 0.85rem;
		color: var(--color-accent);
	}

	.meta-label {
		font-size: 0.75rem;
		color: var(--color-text-muted);
		flex: 1;
	}

	.meta-close {
		cursor: pointer;
		color: var(--color-text-muted);
		font-size: 0.75rem;
		padding: 0 0.2rem;
	}

	.meta-close:hover {
		color: var(--color-text);
	}

	.meta-description {
		margin: 0 0 0.5rem 0;
		color: var(--color-text);
	}

	.meta-section {
		margin-top: 0.5rem;
		padding-top: 0.5rem;
		border-top: 1px solid var(--color-border);
	}

	.meta-section p {
		margin: 0.2rem 0 0 0;
		color: var(--color-text);
	}

	.meta-section-label {
		font-size: 0.7rem;
		font-weight: 600;
		text-transform: uppercase;
		letter-spacing: 0.04em;
		color: var(--color-accent);
	}

	.meta-note {
		background: color-mix(in srgb, var(--color-surface) 80%, var(--color-accent-muted));
		border-radius: calc(var(--radius) - 2px);
		padding: 0.4rem 0.5rem;
		border-top: none;
		margin-top: 0.4rem;
	}
</style>
