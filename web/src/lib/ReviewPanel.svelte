<script lang="ts">
	let {
		selected,
		persona,
		conflicts,
		hasSelectedTokens,
		panelHeight = $bindable(0),
		onToggle,
		onClearPersonaField
	}: {
		selected: Record<string, string[]>;
		persona: { preset: string; voice: string; audience: string; tone: string; intent: string };
		conflicts: { tokenA: string; tokenB: string; reason: string }[];
		hasSelectedTokens: boolean;
		panelHeight?: number;
		onToggle: (axis: string, token: string) => void;
		onClearPersonaField: (field: string) => void;
	} = $props();
</script>

<div class="review-panel" class:review-panel-empty={!hasSelectedTokens} bind:clientHeight={panelHeight}>
	{#if hasSelectedTokens}
		{#if persona.preset}
			<button class="review-panel-chip" tabindex="0" onclick={() => onClearPersonaField('preset')}>persona={persona.preset}</button>
		{/if}
		{#if persona.voice}
			<button class="review-panel-chip" tabindex="0" onclick={() => onClearPersonaField('voice')}>voice={persona.voice}</button>
		{/if}
		{#if persona.audience}
			<button class="review-panel-chip" tabindex="0" onclick={() => onClearPersonaField('audience')}>audience={persona.audience}</button>
		{/if}
		{#if persona.tone}
			<button class="review-panel-chip" tabindex="0" onclick={() => onClearPersonaField('tone')}>tone={persona.tone}</button>
		{/if}
		{#if persona.intent}
			<button class="review-panel-chip" tabindex="0" onclick={() => onClearPersonaField('intent')}>intent={persona.intent}</button>
		{/if}
		{#each Object.entries(selected) as [axis, tokens]}
			{#each tokens as token (token)}
				{@const isConflict = conflicts.some(c => c.tokenA === token || c.tokenB === token)}
				<button
					class="review-panel-chip"
					class:conflict={isConflict}
					tabindex="0"
					onclick={() => onToggle(axis, token)}
				>{axis}={token}{#if isConflict} ⚠{/if}</button>
			{/each}
		{/each}
	{:else}
		Select tokens from the axes above
	{/if}
</div>

<style>
	/* ADR-0157: Review Panel */
	.review-panel {
		position: fixed;
		bottom: 0;
		left: 0;
		right: 0;
		background: var(--color-bg);
		border-top: 1px solid var(--color-border);
		padding: 0.5rem 1rem;
		display: flex;
		flex-wrap: wrap;
		gap: 0.5rem;
		z-index: 100;
		max-height: 30vh;
		overflow-y: auto;
	}

	.review-panel-empty {
		color: var(--color-text-muted);
		font-size: 0.85rem;
		justify-content: center;
	}

	.review-panel-chip {
		background: var(--color-accent);
		border: 1px solid var(--color-accent);
		border-radius: var(--radius);
		padding: 0.25rem 0.5rem;
		font-size: 0.8rem;
		font-family: var(--font-mono);
		color: var(--color-text);
		cursor: pointer;
	}

	@media (hover: hover) {
		.review-panel-chip:hover {
			background: #6b3040;
			border-color: #f7768e;
		}
	}

	.review-panel-chip.conflict {
		opacity: 0.6;
		text-decoration: line-through;
	}

	@media (max-width: 767px) {
		/* FAB clearance: prevent chips from hiding under the fixed bottom-right FAB */
		.review-panel {
			padding-right: 4rem;
		}
	}
</style>
