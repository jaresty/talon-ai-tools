<script module>
	// Module-level flag: persists across all TokenSelector instances (tab changes mount fresh
	// instances with isUsingTouch=false, breaking per-instance guards). This tracks whether
	// the last pointer interaction was touch anywhere on the page, so onfocus and onmouseenter
	// guards work correctly even after a new instance mounts.
	// Note: :focus-visible is NOT a reliable guard on iOS Safari — it returns true for all
	// focused elements regardless of input method, so we use this flag instead.
	let globalIsUsingTouch = false;
	if (typeof window !== 'undefined') {
		window.addEventListener('pointerdown', (e: PointerEvent) => {
			globalIsUsingTouch = e.pointerType === 'touch' || e.pointerType === 'pen';
		}, { capture: true, passive: true });
	}
</script>

<script lang="ts">
	import { METHOD_CATEGORY_ORDER } from './grammar.js';
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
	// Captured at pointerdown (before onfocus fires) to detect confirming clicks
	let activeAtPointerDown = $state<string | null>(null);
	// On mobile, focus fires AFTER click — this flag prevents onfocus re-opening the panel
	let wasJustClicked = $state(false);
	// Touch browsers fire compat mouseenter events — suppress them after any touch interaction
	let isUsingTouch = $state(false);
	// Set when a touchmove/scroll closes the panel mid-gesture; suppresses the stray synthetic
	// click that iOS fires at touchend even after a swipe (which would re-open a random chip's panel)
	let touchBecameSwipe = $state(false);

	// True when any token has a non-empty category — enables grouped rendering
	let hasCategoryGroups = $derived(tokens.some((t) => t.category));

	// Groups for grouped rendering (no filter active). Follows canonical METHOD_CATEGORY_ORDER,
	// with uncategorized tokens in a trailing group.
	let categoryGroups = $derived((): { category: string; tokens: TokenMeta[] }[] => {
		if (!hasCategoryGroups) return [];
		const byCategory = new Map<string, TokenMeta[]>();
		const uncategorized: TokenMeta[] = [];
		for (const t of tokens) {
			if (!t.category) { uncategorized.push(t); continue; }
			if (!byCategory.has(t.category)) byCategory.set(t.category, []);
			byCategory.get(t.category)!.push(t);
		}
		const result: { category: string; tokens: TokenMeta[] }[] = [];
		for (const cat of METHOD_CATEGORY_ORDER) {
			const catTokens = byCategory.get(cat);
			if (catTokens && catTokens.length > 0) result.push({ category: cat, tokens: catTokens });
		}
		if (uncategorized.length > 0) result.push({ category: '', tokens: uncategorized });
		return result;
	});

	// Flat token list in display order — used for keyboard navigation.
	// In grouped mode (no filter), tokens appear in category order; in flat/filter mode, unchanged.
	let filtered = $derived(
		filter.trim()
			? tokens.filter(
					(t) =>
						t.token.includes(filter.toLowerCase()) ||
						t.label.toLowerCase().includes(filter.toLowerCase()) ||
						(t.routing_concept?.toLowerCase().includes(filter.toLowerCase()) ?? false)
				)
			: hasCategoryGroups
				? categoryGroups().flatMap((g) => g.tokens)
				: tokens
	);

	let activeMeta = $derived(tokens.find((t) => t.token === activeToken) ?? null);

	let panelStyle = $state('');

	// Compute panel position before render, anchored to the active chip (not the full grid).
	// Shows on whichever side of the chip has more viewport space — so chips near the top
	// show below, chips near the bottom flip above.
	$effect.pre(() => {
		if (!activeMeta || !gridRef || window.innerWidth <= 767) { panelStyle = ''; return; }
		const chipEl = gridRef.querySelector<HTMLElement>(`[data-token="${activeMeta.token}"]`);
		const rect = (chipEl ?? gridRef).getBoundingClientRect();
		const spaceBelow = window.innerHeight - rect.bottom;
		const spaceAbove = rect.top;
		const left = Math.round(rect.left);
		const w = `min(600px, calc(100vw - ${left}px - 1rem))`;
		if (spaceBelow >= spaceAbove) {
			panelStyle = `top:${Math.round(rect.bottom + 4)}px; left:${left}px; width:${w}`;
		} else {
			panelStyle = `bottom:${Math.round(window.innerHeight - rect.top + 4)}px; left:${left}px; width:${w}`;
		}
	});

	// Always-active touchmove guard: any touch movement marks the gesture as a swipe so
	// handleChipClick can suppress the stray synthetic click iOS fires at touchend.
	// pointerdown resets the flag, so a real tap after a scroll always works correctly.
	$effect(() => {
		const markSwipe = (e: Event) => { if (e instanceof TouchEvent) touchBecameSwipe = true; };
		window.addEventListener('touchmove', markSwipe, { passive: true });
		return () => window.removeEventListener('touchmove', markSwipe);
	});

	// Close panel on page scroll or touch scroll, but not when scrolling inside the panel itself.
	// Set touchBecameSwipe BEFORE the meta-panel early-return so swipes that start inside the
	// panel still suppress the ghost click.
	$effect(() => {
		if (!activeToken) return;

		const handleScroll = (e: Event) => {
			if (e instanceof TouchEvent) touchBecameSwipe = true;
			if (e instanceof TouchEvent && (e.target as Element)?.closest?.('.meta-panel')) return;
			activeToken = null;
		};
		window.addEventListener('scroll', handleScroll, { passive: true });
		window.addEventListener('touchmove', handleScroll, { passive: true });

		return () => {
			window.removeEventListener('scroll', handleScroll);
			window.removeEventListener('touchmove', handleScroll);
		};
	});

	// On touch: blur the chip when the panel closes so swipe-back can't re-trigger it via focus restore
	$effect(() => {
		if (activeToken !== null) return;
		if (!isUsingTouch) return;
		const focused = document.activeElement as HTMLElement | null;
		if (focused?.closest('.token-grid')) focused.blur();
	});

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
		// Suppress stray synthetic click fired by iOS at touchend after a swipe gesture
		if (isUsingTouch && touchBecameSwipe) { touchBecameSwipe = false; return; }
		const isSelected = selected.includes(meta.token);
		if (isSelected) {
			onToggle(meta.token);
			activeToken = null;
		} else if (activeAtPointerDown === meta.token) {
			// Panel was already open when the pointer went down — confirming click selects
			if (!atCap) { onToggle(meta.token); activeToken = null; }
		} else {
			// First click: open panel to inspect
			activeToken = meta.token;
		}
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

<div class="axis-panel" onmouseleave={() => { if (!isUsingTouch) activeToken = null; }}>
	<div class="axis-header">
		<span class="axis-name">{axis}</span>
		<span class="axis-cap">0–{maxSelect}</span>
	</div>

	{#if tokens.length > 5}
		<input
			class="filter-input"
			type="text"
			placeholder="filter…"
			bind:value={filter}
			bind:this={filterInputRef}
			onfocus={(e) => (e.target as HTMLInputElement).select()}
			onkeydown={(e) => {
				if (e.key === 'ArrowDown' && filtered.length > 0) {
					e.preventDefault();
					focusedIndex = 0;
					focusChip(0);
				} else if (e.key === 'Tab' && !e.shiftKey && filtered.length > 0) {
					e.preventDefault();
					focusedIndex = 0;
					focusChip(0);
				} else if (e.key === 'Enter' && filtered.length > 0) {
					e.preventDefault();
					onToggle(filtered[0].token);
					// Keep focus on filter — allows fast multi-toggle by typing + Enter repeatedly
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
		{#if hasCategoryGroups && !filter.trim()}
			{#each categoryGroups() as group}
				{#if group.category}
					<div class="category-header" role="presentation">{group.category}</div>
				{/if}
				{#each group.tokens as meta (meta.token)}
					{@const i = filtered.indexOf(meta)}
					{@const isSelected = selected.includes(meta.token)}
					{@const atCap = !isSelected && selected.length >= maxSelect && maxSelect > 1}
					{@const isActive = activeToken === meta.token}
					<!-- svelte-ignore a11y_click_events_have_key_events -->
					<div
						class="token-chip"
						class:selected={isSelected}
						class:disabled={atCap}
						class:active-meta={isActive}
						role="option"
						aria-selected={isSelected}
						data-token={meta.token}
						tabindex={focusedIndex === -1 ? (i === 0 ? 0 : -1) : (focusedIndex === i ? 0 : -1)}
						onmouseenter={() => { if (!globalIsUsingTouch) activeToken = meta.token; }}
						onpointerdown={(e) => {
							isUsingTouch = e.pointerType === 'touch' || e.pointerType === 'pen';
							activeAtPointerDown = activeToken;
							wasJustClicked = true;
							touchBecameSwipe = false;
						}}
						onclick={() => handleChipClick(meta, atCap)}
						onkeydown={(e) => {
							if (e.key === 'Enter' || e.key === ' ') {
								e.preventDefault();
								if (!atCap) { onToggle(meta.token); activeToken = null; }
							}
						}}
						onfocus={(e) => {
							focusedIndex = i;
							if (!wasJustClicked && !globalIsUsingTouch) activeToken = meta.token;
							wasJustClicked = false;
						}}
					>
						{#if meta.kanji}
							<span class="token-kanji">{meta.kanji}</span>
						{/if}
						<code>{meta.token}</code>
						{#if meta.label}
							<span class="token-label">{meta.label}</span>
						{/if}
						{#if meta.use_when}
							<span class="use-when-dot">●</span>
						{/if}
						{#if meta.routing_concept}
							<span class="routing-concept">{meta.routing_concept}</span>
						{/if}
					</div>
				{/each}
			{/each}
		{:else}
			{#each filtered as meta, i (meta.token)}
				{@const isSelected = selected.includes(meta.token)}
				{@const atCap = !isSelected && selected.length >= maxSelect && maxSelect > 1}
				{@const isActive = activeToken === meta.token}
				<!-- svelte-ignore a11y_click_events_have_key_events -->
				<div
					class="token-chip"
					class:selected={isSelected}
					class:disabled={atCap}
					class:active-meta={isActive}
					role="option"
					aria-selected={isSelected}
					data-token={meta.token}
					tabindex={focusedIndex === -1 ? (i === 0 ? 0 : -1) : (focusedIndex === i ? 0 : -1)}
					onmouseenter={() => { if (!globalIsUsingTouch) activeToken = meta.token; }}
					onpointerdown={(e) => {
						isUsingTouch = e.pointerType === 'touch' || e.pointerType === 'pen';
						activeAtPointerDown = activeToken;
						wasJustClicked = true;
					}}
					onclick={() => handleChipClick(meta, atCap)}
					onkeydown={(e) => {
						if (e.key === 'Enter' || e.key === ' ') {
							e.preventDefault();
							if (!atCap) { onToggle(meta.token); activeToken = null; }
						}
					}}
					onfocus={(e) => {
						focusedIndex = i;
						if (!wasJustClicked && !globalIsUsingTouch) activeToken = meta.token;
						wasJustClicked = false;
					}}
				>
					{#if meta.kanji}
						<span class="token-kanji">{meta.kanji}</span>
					{/if}
					<code>{meta.token}</code>
					{#if meta.label}
						<span class="token-label">{meta.label}</span>
					{/if}
					{#if meta.use_when}
						<span class="use-when-dot">●</span>
					{/if}
					{#if meta.routing_concept}
						<span class="routing-concept">{meta.routing_concept}</span>
					{/if}
				</div>
			{/each}
		{/if}
	</div>

	{#if activeMeta}
		{@const isActiveSel = selected.includes(activeMeta.token)}
		{@const atCap = !isActiveSel && selected.length >= maxSelect && maxSelect > 1}
		<div class="meta-panel" style={panelStyle}>
			<div class="meta-header">
				<code class="meta-token">{activeMeta.token}</code>
				{#if activeMeta.label}
					<span class="meta-label">{activeMeta.label}</span>
				{/if}
				<button class="meta-close" onclick={() => (activeToken = null)}>✕</button>
			</div>
			<div class="meta-body">
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
		align-items: flex-start;
	}

	.category-header {
		width: 100%;
		font-size: 0.68rem;
		font-weight: 600;
		text-transform: uppercase;
		letter-spacing: 0.06em;
		color: var(--color-text-muted);
		padding: 0.4rem 0 0.1rem 0;
		margin-top: 0.2rem;
		border-top: 1px solid var(--color-border);
	}

	.category-header:first-child {
		border-top: none;
		padding-top: 0;
		margin-top: 0;
	}

	.token-chip {
		display: flex;
		align-items: center;
		flex-wrap: wrap;
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
		outline-offset: -1px;
	}

	.token-chip:focus-visible {
		outline: 2px solid var(--color-accent);
		outline-offset: -1px;
	}

	.token-chip.disabled {
		opacity: 0.4;
		cursor: not-allowed;
	}

	code {
		font-family: var(--font-mono);
		font-size: 0.8rem;
	}

	.token-kanji {
		font-size: 0.9rem;
		margin-right: 0.2rem;
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

	/* ADR-0146: routing concept subtitle — same visual weight as chip label, not artificially dimmed */
	.routing-concept {
		width: 100%;
		font-size: 0.65rem;
		color: var(--color-text);
		font-style: italic;
		line-height: 1.3;
		margin-top: 0.05rem;
	}

	.meta-panel {
		padding: 0.75rem;
		background: var(--color-surface);
		border: 1px solid var(--color-accent-muted);
		border-radius: var(--radius);
		font-size: 0.8rem;
		line-height: 1.5;
		display: flex;
		flex-direction: column;
		position: fixed;
		z-index: 100;
		pointer-events: none;
	}

	.meta-body {
		overflow-y: auto;
		flex: 1;
		min-height: 0;
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
			top: auto;
			left: 0;
			right: 0;
			margin: 0;
			border-radius: var(--radius) var(--radius) 0 0;
			border-left: none;
			border-right: none;
			border-bottom: none;
			border-top: 2px solid var(--color-accent);
			max-height: 60vh;
			overflow: hidden;
			z-index: 200;
			pointer-events: auto;
			font-size: 1rem;
			line-height: 1.6;
			padding-bottom: 0;
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
			padding-bottom: env(safe-area-inset-bottom);
		}
	}
</style>
