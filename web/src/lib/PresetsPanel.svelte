<script lang="ts">
	import type { SpaPreset } from '$lib/presets.js';

	let {
		savedPresets,
		presetNameInput,
		presetSaved,
		onSave,
		onLoad,
		onDelete,
		onNameInput
	}: {
		savedPresets: SpaPreset[];
		presetNameInput: string;
		presetSaved: boolean;
		onSave: () => void;
		onLoad: (preset: SpaPreset) => void;
		onDelete: (name: string) => void;
		onNameInput: (value: string) => void;
	} = $props();
</script>

<details class="presets-panel">
	<summary class="presets-summary">Presets</summary>
	<div class="presets-save-row">
		<input
			class="presets-name-input"
			type="text"
			placeholder="Preset name…"
			value={presetNameInput}
			oninput={(e) => onNameInput((e.target as HTMLInputElement).value)}
			onkeydown={(e) => { if (e.key === 'Enter') onSave(); }}
		/>
		<button class="presets-save-btn" onclick={onSave} disabled={!presetNameInput.trim()}>
			{presetSaved ? '✓ Saved' : 'Save'}
		</button>
	</div>
	{#if savedPresets.length === 0}
		<p class="presets-empty">No presets saved.</p>
	{:else}
		<ul class="presets-list">
			{#each savedPresets as preset (preset.name)}
				<li class="preset-item">
					<div class="preset-item-top">
						<span class="preset-item-name">{preset.name}</span>
						<div class="preset-item-actions">
							<button class="preset-load-btn" onclick={() => onLoad(preset)}>Load</button>
							<button class="preset-delete-btn" onclick={() => onDelete(preset.name)}>✕</button>
						</div>
					</div>
					<code class="preset-item-tokens">{preset.tokens.join(' ')}</code>
				</li>
			{/each}
		</ul>
	{/if}
</details>

<style>
	.presets-panel {
		margin-top: 0.5rem;
	}

	.presets-summary {
		cursor: pointer;
		font-size: 0.85rem;
		color: var(--color-muted, #aaa);
		user-select: none;
	}

	.presets-save-row {
		display: flex;
		gap: 0.5rem;
		margin: 0.5rem 0;
	}

	.presets-name-input {
		flex: 1;
		background: var(--color-surface, #1a1a1a);
		border: 1px solid var(--color-border, #444);
		border-radius: 4px;
		color: inherit;
		padding: 0.3rem 0.5rem;
		font-size: 0.85rem;
	}

	.presets-save-btn {
		padding: 0.3rem 0.75rem;
		background: var(--color-accent, #4a9eff);
		color: #fff;
		border: none;
		border-radius: 4px;
		cursor: pointer;
		font-size: 0.85rem;
	}

	.presets-save-btn:disabled {
		opacity: 0.4;
		cursor: default;
	}

	.presets-empty {
		font-size: 0.82rem;
		color: var(--color-muted, #888);
		margin: 0.25rem 0;
	}

	.presets-list {
		list-style: none;
		padding: 0;
		margin: 0;
		display: flex;
		flex-direction: column;
		gap: 0.4rem;
	}

	.preset-item {
		background: var(--color-surface, #1a1a1a);
		border: 1px solid var(--color-border, #333);
		border-radius: 4px;
		padding: 0.4rem 0.6rem;
	}

	.preset-item-top {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 0.5rem;
	}

	.preset-item-name {
		font-size: 0.85rem;
		font-weight: 500;
	}

	.preset-item-actions {
		display: flex;
		gap: 0.3rem;
	}

	.preset-load-btn {
		font-size: 0.78rem;
		padding: 0.15rem 0.5rem;
		background: var(--color-accent, #4a9eff);
		color: #fff;
		border: none;
		border-radius: 3px;
		cursor: pointer;
	}

	.preset-delete-btn {
		font-size: 0.78rem;
		padding: 0.15rem 0.4rem;
		background: transparent;
		color: var(--color-muted, #888);
		border: 1px solid var(--color-border, #444);
		border-radius: 3px;
		cursor: pointer;
	}

	.preset-item-tokens {
		display: block;
		margin-top: 0.2rem;
		font-size: 0.75rem;
		color: var(--color-muted, #999);
	}
</style>
