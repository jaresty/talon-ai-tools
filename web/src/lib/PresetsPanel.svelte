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
		margin-bottom: 0.75rem;
		border: 1px solid var(--color-border);
		border-radius: var(--radius);
		overflow: hidden;
	}

	.presets-summary {
		padding: 0.4rem 0.75rem;
		font-size: 0.75rem;
		text-transform: uppercase;
		letter-spacing: 0.05em;
		cursor: pointer;
		user-select: none;
		background: var(--color-surface);
		color: var(--color-text-muted);
	}

	.presets-save-row {
		display: flex;
		gap: 0.5rem;
		padding: 0.5rem 0.75rem 0.25rem;
	}

	.presets-name-input {
		flex: 1;
		padding: 0.3rem 0.5rem;
		font-size: 0.8rem;
		background: var(--color-bg);
		border: 1px solid var(--color-border);
		border-radius: var(--radius);
		color: var(--color-text);
	}

	.presets-save-btn {
		padding: 0.3rem 0.75rem;
		font-size: 0.8rem;
		background: var(--color-accent);
		color: #1a1b26;
		border: none;
		border-radius: var(--radius);
		cursor: pointer;
		white-space: nowrap;
	}

	.presets-save-btn:disabled { opacity: 0.4; cursor: default; }

	.presets-empty {
		font-size: 0.8rem;
		color: var(--color-text-muted);
		padding: 0.5rem 0.75rem 0.75rem;
		margin: 0;
	}

	.presets-list { list-style: none; margin: 0; padding: 0.25rem 0 0.5rem; }

	.preset-item {
		padding: 0.35rem 0.75rem;
		border-bottom: 1px solid var(--color-border);
	}
	.preset-item:last-child { border-bottom: none; }

	.preset-item-top {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 0.5rem;
	}

	.preset-item-name { font-size: 0.85rem; font-weight: 500; color: var(--color-text); }

	.preset-item-actions { display: flex; gap: 0.3rem; flex-shrink: 0; }

	.preset-load-btn {
		padding: 0.15rem 0.5rem;
		font-size: 0.75rem;
		background: var(--color-surface);
		border: 1px solid var(--color-border);
		border-radius: var(--radius);
		color: var(--color-text);
		cursor: pointer;
	}
	.preset-load-btn:hover { border-color: var(--color-accent); color: var(--color-accent); }

	.preset-delete-btn {
		padding: 0.15rem 0.4rem;
		font-size: 0.75rem;
		background: transparent;
		border: 1px solid transparent;
		border-radius: var(--radius);
		color: var(--color-text-muted);
		cursor: pointer;
	}
	.preset-delete-btn:hover { border-color: #f7768e; color: #f7768e; }

	.preset-item-tokens {
		display: block;
		margin-top: 0.15rem;
		font-size: 0.75rem;
		color: var(--color-text-muted);
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}
</style>
