<script lang="ts">
	import type { TokenMeta } from './grammar.js';

	interface Props {
		axis: string;
		tokens: TokenMeta[];
		selected: string[];
		maxSelect: number;
		onToggle: (token: string) => void;
		onTabNext?: () => void;
		onTabPrev?: () => void;
	}

	let { axis, tokens, selected, maxSelect, onToggle, onTabNext, onTabPrev }: Props = $props();

	let filter = $state('');
	let activeToken = $state<string | null>(null);
	let focusedIndex = $state(-1);
	let gridRef = $state<HTMLDivElement | null>(null);
	let filterInputRef = $state<HTMLInputElement | null>(null);

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

	// Reset focus index when filtered list changes
	$effect(() => {
		void filtered.length;
		focusedIndex = -1;
	});

	function chipOptions(): HTMLElement[] {
		if (!gridRef) return [];
		return Array.from(gridRef.querySelectorAll<HTMLElement>('[role="option"]'));
	}

	function focusChip(index: number) {
		const options = chipOptions();
		options[index]?.focus();
	}

	function handleChipClick(meta: TokenMeta, atCap: boolean) {
		if (!atCap) onToggle(meta.token);
		activeToken = activeToken === meta.token ? null : meta.token;
	}

	function handleGridKey(e: KeyboardEvent) {
		const n = filtered.length;
		if (n === 0) return;
		if (e.key === 'ArrowRight' || e.key === 'ArrowDown') {
			e.preventDefault();
			focusedIndex = (focusedIndex + 1) % n;
			focusChip(focusedIndex);
		} else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') {
			e.preventDefault();
			focusedIndex = (focusedIndex <= 0 ? n : focusedIndex) - 1;
			focusChip(focusedIndex);
		} else if (e.key === 'Home') {
			e.preventDefault();
			focusedIndex = 0;
			focusChip(0);
		} else if (e.key === 'End') {
			e.preventDefault();
			focusedIndex = n - 1;
			focusChip(n - 1);
		} else if (e.key === 'Tab' && !e.shiftKey && focusedIndex < filtered.length - 1) {
			e.preventDefault();
			focusedIndex = filtered.length - 1;
			focusChip(filtered.length - 1);
		} else if (e.key === 'Tab' && !e.shiftKey && focusedIndex === filtered.length - 1 && onTabNext) {
			e.preventDefault();
			onTabNext();
		} else if (e.key === 'Tab' && e.shiftKey && focusedIndex === 0) {
			e.preventDefault();
			if (filterInputRef) {
				filterInputRef.focus();
			} else if (onTabPrev) {
				onTabPrev();
			}
		} else if (e.key === 'Escape') {
			activeToken = null;
			focusedIndex = -1;
			filterInputRef?.focus();
		}
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
			bind:this={filterInputRef}
			onkeydown={(e) => {
				if (e.key === 'ArrowDown' && filtered.length > 0) {
					e.preventDefault();
					focusedIndex = 0;
					focusChip(0);
				} else if (e.key === 'Tab' && !e.shiftKey && filtered.length > 0) {
					e.preventDefault();
					focusedIndex = 0;
					focusChip(0);
				}
				// Shift+Tab: let browser handle — natural DOM order returns focus to the active tab button
			}}
		/>
	{/if}

	{#if axis === 'directional'}
		<div class="axis-note">
			<span class="compass-label">fog</span> (abstract) ·
			<span class="compass-label">dig</span> (concrete) ·
			<span class="compass-label">rog</span> (reflect) ·
			<span class="compass-label">ong</span> (act) ·
			compounds span the spectrum between poles
		</div>
	{/if}

	<!-- svelte-ignore a11y_interactive_supports_focus -->
	<div
		class="token-grid"
		role="listbox"
		aria-label="{axis} tokens"
		aria-multiselectable={maxSelect > 1}
		onkeydown={handleGridKey}
		bind:this={gridRef}
	>
		{#each filtered as meta, i (meta.token)}
			{@const isSelected = selected.includes(meta.token)}
			{@const atCap = !isSelected && selected.length >= maxSelect}
			{@const isActive = activeToken === meta.token}
			<!-- svelte-ignore a11y_click_events_have_key_events -->
			<div
				class="token-chip"
				class:selected={isSelected}
				class:disabled={atCap}
				class:active-meta={isActive}
				role="option"
				aria-selected={isSelected}
				tabindex={focusedIndex === -1 ? (i === 0 ? 0 : -1) : (focusedIndex === i ? 0 : -1)}
	
				onclick={() => handleChipClick(meta, atCap)}
				onkeydown={(e) => {
					if (e.key === 'Enter' || e.key === ' ') {
						e.preventDefault();
						handleChipClick(meta, atCap);
					}
				}}
				onfocus={() => {
					focusedIndex = i;
					activeToken = meta.token;
				}}
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
		{@const isActiveSel = selected.includes(activeMeta.token)}
		{@const atCap = !isActiveSel && selected.length >= maxSelect}
		<div class="meta-panel">
			<div class="meta-header">
				<code class="meta-token">{activeMeta.token}</code>
				{#if activeMeta.label}
					<span class="meta-label">{activeMeta.label}</span>
				{/if}
				<button class="meta-close" onclick={() => (activeToken = null)}>✕</button>
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
			<div class="meta-footer">
				<button
					class="meta-select-btn"
					class:selected={isActiveSel}
					disabled={atCap}
					onclick={() => { onToggle(activeMeta!.token); activeToken = null; }}
				>
					{#if isActiveSel}✓ Deselect{:else if atCap}At limit{:else}Select ↵{/if}
				</button>
			</div>
		</div>
	{/if}
</div>

<style>
	.axis-note {
		font-size: 0.72rem;
		color: #888;
		margin-bottom: 0.5rem;
		line-height: 1.4;
	}

	.compass-label {
		font-family: monospace;
		font-weight: 600;
		color: #aaa;
	}

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

	.token-chip.active-meta:not(:focus-visible) {
		outline: 2px solid var(--color-accent);
		outline-offset: 1px;
	}

	.token-chip:focus-visible {
		outline: 2px solid var(--color-accent);
		outline-offset: 2px;
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
		background: none;
		border: none;
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

	.meta-footer {
		margin-top: 0.6rem;
		padding-top: 0.5rem;
		border-top: 1px solid var(--color-border);
		display: flex;
		justify-content: flex-end;
	}

	.meta-select-btn {
		padding: 0.3rem 0.9rem;
		background: var(--color-accent-muted);
		border: 1px solid var(--color-accent);
		border-radius: var(--radius);
		color: var(--color-text);
		cursor: pointer;
		font-size: 0.8rem;
		font-family: system-ui;
	}

	.meta-select-btn:hover:not(:disabled) { background: var(--color-accent); }

	.meta-select-btn.selected {
		background: transparent;
		border-color: var(--color-border);
		color: var(--color-text-muted);
	}

	.meta-select-btn.selected:hover { border-color: #f7768e; color: #f7768e; }

	.meta-select-btn:disabled {
		opacity: 0.4;
		cursor: not-allowed;
	}

	@media (max-width: 767px) {
		.token-chip {
			min-height: 44px;
			padding: 0.5rem 0.75rem;
		}

		/* Guidance drawer: slides up from bottom, always in viewport */
		.meta-panel {
			position: fixed;
			bottom: 0;
			left: 0;
			right: 0;
			margin: 0;
			border-radius: var(--radius) var(--radius) 0 0;
			border-left: none;
			border-right: none;
			border-bottom: none;
			border-top: 2px solid var(--color-accent);
			max-height: 60vh;
			overflow-y: auto;
			z-index: 200;
			font-size: 1rem;
			line-height: 1.6;
		}

		.meta-section-label {
			font-size: 0.85rem;
		}

		.meta-description,
		.meta-section p {
			font-size: 0.95rem;
		}

		.meta-close {
			min-width: 44px;
			min-height: 44px;
			display: flex;
			align-items: center;
			justify-content: center;
		}

		.filter-input {
			min-height: 44px;
			font-size: 1rem;
		}

		.meta-select-btn {
			min-height: 44px;
			padding: 0.5rem 1.5rem;
			font-size: 1rem;
			width: 100%;
		}

		.meta-footer {
			justify-content: stretch;
		}
	}
</style>
