<script lang="ts">
	import { getAxisTokens, getTaskTokens, getPersonaPresets, getPersonaAxisTokensMeta, getPresetHint, AXES, type GrammarPattern, type StarterPack } from '$lib/grammar.js';
	import TokenSelector from '$lib/TokenSelector.svelte';
	import PatternsLibrary from '$lib/PatternsLibrary.svelte';
	import { parseCommand } from '$lib/parseCommand.js';
	import { selected, persona, subject, addendum, grammar as grammarStore } from '$lib/stores.js';
	let {
		patterns,
		starterPacks,
		onClear,
		suggestionScores,
		embedder,
		activeMode,
		onModeChange
	}: {
		patterns: GrammarPattern[];
		starterPacks: StarterPack[];
		onClear: () => void;
		suggestionScores: Map<string, number>;
		embedder: (q: string) => Promise<Float32Array | null>;
		activeMode: 'build' | 'sequences';
		onModeChange: (mode: 'build' | 'sequences') => void;
	} = $props();

	let activeTab = $state('task');
	let panelSlideDir = $state<'next' | 'prev' | null>(null);
	let swipeOffset = $state(0);
	let swipeAnimating = $state(false);
	let hoveredDistinctionPreset = $state<string | null>(null);
	let cmdInput = $state('');
	let cmdInputOpen = $state(false);
	let cmdInputWarnings = $state<string[]>([]);

	let touchStartX = 0;
	let touchStartY = 0;
	let touchStartedInModal = false;

	const AXES_WITH_PERSONA = ['persona', 'task', 'topology', 'completeness', 'scope', 'method', 'form', 'channel', 'directional'];

	let activePresetMeta = $derived($grammarStore && $persona.preset
		? getPersonaPresets($grammarStore).find(p => p.key === $persona.preset) ?? null
		: null);

	function softCap(axis: string): number {
		if (!$grammarStore) return 1;
		return $grammarStore.hierarchy.axis_soft_caps[axis] ?? 1;
	}

	function toggle(axis: string, token: string) {
		const cur = $selected[axis] ?? [];
		if (cur.includes(token)) {
			$selected = { ...$selected, [axis]: cur.filter((t) => t !== token) };
		} else {
			const cap = softCap(axis);
			if (cur.length < cap) {
				$selected = { ...$selected, [axis]: [...cur, token] };
			} else if (cap === 1) {
				$selected = { ...$selected, [axis]: [token] };
			}
		}
	}

	function loadPattern(pattern: GrammarPattern) {
		$selected = { task: [], completeness: [], scope: [], method: [], form: [], channel: [], directional: [], ...pattern.tokens };
	}

	function loadCommand() {
		if (!$grammarStore || !cmdInput.trim()) return;
		const result = parseCommand(cmdInput, $grammarStore);
		$selected = { task: [], completeness: [], scope: [], method: [], form: [], channel: [], directional: [], ...result.selected };
		if (result.subject) $subject = result.subject;
		if (result.addendum) $addendum = result.addendum;
		if (result.persona.preset || result.persona.voice || result.persona.audience || result.persona.tone || result.persona.intent) {
			$persona = result.persona;
		}
		cmdInputWarnings = result.unrecognized;
		if (result.unrecognized.length === 0) {
			cmdInput = '';
			cmdInputOpen = false;
		}
	}

	function focusActiveTabInner() {
		document.querySelector<HTMLElement>('[role="tab"][aria-selected="true"]')?.focus();
	}

	function focusFirstChip() {
		const chip = document.querySelector<HTMLElement>('[role="option"]');
		if (chip) { chip.focus(); return; }
		document.querySelector<HTMLElement>('.selector-panel button, .selector-panel select, .selector-panel input')?.focus();
	}

	function focusLastChip() {
		const chips = document.querySelectorAll<HTMLElement>('[role="option"]');
		const last = chips[chips.length - 1];
		last?.focus();
	}

	function focusFilterOrFirstInner() {
		const filterEl = document.querySelector<HTMLElement>('.selector-panel .filter-input');
		if (filterEl) { filterEl.focus(); return; }
		focusFirstChip();
	}

	function goToNextTabInner(moveFocus = true, animate = true) {
		if (animate) panelSlideDir = 'next';
		const n = AXES_WITH_PERSONA.length;
		const cur = AXES_WITH_PERSONA.indexOf(activeTab);
		activeTab = AXES_WITH_PERSONA[(cur + 1) % n];
		if (moveFocus) setTimeout(focusFirstChip, 0);
	}

	function goToPrevTabInner(moveFocus = true, animate = true) {
		if (animate) panelSlideDir = 'prev';
		const n = AXES_WITH_PERSONA.length;
		const cur = AXES_WITH_PERSONA.indexOf(activeTab);
		activeTab = AXES_WITH_PERSONA[(cur - 1 + n) % n];
		if (moveFocus) setTimeout(focusLastChip, 0);
	}

	function switchTab(tab: string) {
		const cur = AXES_WITH_PERSONA.indexOf(activeTab);
		const next = AXES_WITH_PERSONA.indexOf(tab);
		panelSlideDir = next > cur ? 'next' : next < cur ? 'prev' : null;
		activeTab = tab;
	}

	function handleTabBarKey(e: KeyboardEvent) {
		const n = AXES_WITH_PERSONA.length;
		const cur = AXES_WITH_PERSONA.indexOf(activeTab);
		if (e.key === 'ArrowRight' || e.key === 'ArrowDown') {
			e.preventDefault();
			panelSlideDir = 'next';
			activeTab = AXES_WITH_PERSONA[(cur + 1) % n];
			setTimeout(focusActiveTabInner, 0);
		} else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') {
			e.preventDefault();
			panelSlideDir = 'prev';
			activeTab = AXES_WITH_PERSONA[(cur - 1 + n) % n];
			setTimeout(focusActiveTabInner, 0);
		} else if (e.key === 'Home') {
			e.preventDefault();
			panelSlideDir = cur > 0 ? 'prev' : null;
			activeTab = AXES_WITH_PERSONA[0];
		} else if (e.key === 'End') {
			e.preventDefault();
			panelSlideDir = cur < n - 1 ? 'next' : null;
			activeTab = AXES_WITH_PERSONA[n - 1];
		}
	}

	function handleTouchStart(e: TouchEvent) {
		touchStartX = e.touches[0].clientX;
		touchStartY = e.touches[0].clientY;
		touchStartedInModal = !!(e.target as Element)?.closest?.('.meta-panel');
		swipeOffset = 0;
		swipeAnimating = false;
	}

	function handleTouchMove(e: TouchEvent) {
		if (touchStartedInModal) return;
		const dx = e.touches[0].clientX - touchStartX;
		const dy = e.touches[0].clientY - touchStartY;
		if (Math.abs(dx) > Math.abs(dy)) {
			swipeOffset = dx;
		}
	}

	let swipeCompletedAt = 0;

	function handleTouchEnd(e: TouchEvent) {
		const dx = e.changedTouches[0].clientX - touchStartX;
		const dy = e.changedTouches[0].clientY - touchStartY;
		const target = e.target as Element;

		if (touchStartedInModal) { swipeAnimating = true; swipeOffset = 0; return; }
		if (target.closest('input, textarea, select')) { swipeAnimating = true; swipeOffset = 0; return; }
		if (Math.abs(dx) < 50 || Math.abs(dy) >= Math.abs(dx)) { swipeAnimating = true; swipeOffset = 0; return; }

		e.preventDefault();
		swipeCompletedAt = Date.now();
		const dir = dx < 0 ? -1 : 1;
		const slideWidth = Math.max(window.innerWidth, 400);
		swipeAnimating = true;
		swipeOffset = dir * slideWidth;

		setTimeout(() => {
			swipeAnimating = false;
			swipeOffset = 0;
			if (dx < 0) goToNextTabInner(false, false);
			else goToPrevTabInner(false, false);
		}, 250);
	}

	export function getSwipeCompletedAt() { return swipeCompletedAt; }
	export function focusFilterOrFirst() { focusFilterOrFirstInner(); }
	export function goToNextTab(moveFocus = false) { goToNextTabInner(moveFocus); }
	export function goToPrevTab(moveFocus = false) { goToPrevTabInner(moveFocus); }
	export function focusActiveTab() { focusActiveTabInner(); }
</script>

<div class="selector-panel-root">
<!-- Subject input — above tabs, first-class input -->
<label class="input-group subject-top">
	<span class="input-label">--subject <span class="input-hint">source material</span></span>
	<textarea
		class="input-area"
		data-field="subject"
		rows="4"
		placeholder="Paste code, document, or topic…"
		bind:value={$subject}
	></textarea>
</label>

<!-- svelte-ignore a11y_no_noninteractive_element_to_interactive_role -->
<nav class="tab-bar" role="tablist" onkeydown={handleTabBarKey}>
	{#each AXES_WITH_PERSONA as tab (tab)}
		<button
			class="tab"
			class:active={activeTab === tab}
			role="tab"
			id="tab-{tab}"
			aria-selected={activeTab === tab}
			aria-controls="panel-{tab}"
			tabindex={activeTab === tab ? 0 : -1}
			onclick={() => switchTab(tab)}
		>
			{tab}
		</button>
	{/each}
</nav>

{#if !$grammarStore}
	<div class="loading">Loading grammar…</div>
{:else}
	{@const grammar = $grammarStore}
	<section
		class="selector-panel"
		class:slide-next={panelSlideDir === 'next'}
		class:slide-prev={panelSlideDir === 'prev'}
		role="region"
		aria-label="Token selector"
		style:transform={swipeOffset !== 0 ? `translateX(${swipeOffset}px)` : undefined}
		style:transition={swipeAnimating ? 'transform 0.25s ease-out' : 'none'}
		ontouchstart={handleTouchStart}
		ontouchmove={handleTouchMove}
		ontouchend={handleTouchEnd}
		onanimationend={() => panelSlideDir = null}
	>
		{#if activeTab === 'persona'}
		<!-- Persona -->
		<div class="persona-section">
			<div class="persona-header">Persona</div>
			{#if grammar?.axes?.axis_descriptions?.['persona']}
				<p class="axis-desc">{grammar.axes.axis_descriptions['persona']}</p>
			{/if}

			<!-- Presets -->
			<div class="persona-group">
				<div class="persona-group-label">Preset</div>
				<div class="persona-chips">
					{#each getPersonaPresets(grammar) as preset (preset.key)}
						<button
							class="persona-chip"
							class:active={$persona.preset === preset.key}
							class:chip--distinction-ref={hoveredDistinctionPreset === preset.key}
							onclick={() => {
								if ($persona.preset === preset.key) {
									$persona = { preset: '', voice: '', audience: '', tone: '', intent: $persona.intent };
								} else {
									$persona = { preset: preset.key, voice: '', audience: '', tone: '', intent: $persona.intent };
								}
							}}
						>{preset.label}{#if getPresetHint(grammar, preset.key)}<span class="persona-chip-hint">{getPresetHint(grammar, preset.key)}</span>{/if}</button>
					{/each}
				</div>
				{#if $persona.preset}
					{@const presetMeta = getPersonaPresets(grammar).find(p => p.key === $persona.preset)}
					<div class="persona-use-when preset-axis-summary">
						{#if presetMeta?.voice}<code class="preset-axis-tag">voice={presetMeta.voice}</code>{/if}
						{#if presetMeta?.audience}<code class="preset-axis-tag">audience={presetMeta.audience}</code>{/if}
						{#if presetMeta?.tone}<code class="preset-axis-tag">tone={presetMeta.tone}</code>{/if}
					</div>
				{/if}
			</div>

			<!-- Override axes: voice, audience, tone (mutually exclusive with preset) -->
			<div class="override-group">
				<div class="override-group-label">or customize</div>
				<TokenSelector
					axis="voice"
					tokens={getPersonaAxisTokensMeta(grammar, 'voice')}
					selected={$persona.voice ? [$persona.voice] : activePresetMeta?.voice ? [activePresetMeta.voice] : []}
					maxSelect={1}
					onToggle={(t) => {
						if ($persona.voice === t || activePresetMeta?.voice === t) $persona = { ...$persona, preset: '', voice: '' };
						else $persona = { preset: '', voice: t, audience: $persona.audience || activePresetMeta?.audience || '', tone: $persona.tone || activePresetMeta?.tone || '', intent: $persona.intent };
					}}
				/>
				<TokenSelector
					axis="audience"
					tokens={getPersonaAxisTokensMeta(grammar, 'audience')}
					selected={$persona.audience ? [$persona.audience] : activePresetMeta?.audience ? [activePresetMeta.audience] : []}
					maxSelect={1}
					onToggle={(t) => {
						if ($persona.audience === t || activePresetMeta?.audience === t) $persona = { ...$persona, preset: '', audience: '' };
						else $persona = { preset: '', voice: $persona.voice || activePresetMeta?.voice || '', audience: t, tone: $persona.tone || activePresetMeta?.tone || '', intent: $persona.intent };
					}}
				/>
				<TokenSelector
					axis="tone"
					tokens={getPersonaAxisTokensMeta(grammar, 'tone')}
					selected={$persona.tone ? [$persona.tone] : activePresetMeta?.tone ? [activePresetMeta.tone] : []}
					maxSelect={1}
					onToggle={(t) => {
						if ($persona.tone === t || activePresetMeta?.tone === t) $persona = { ...$persona, preset: '', tone: '' };
						else $persona = { preset: '', voice: $persona.voice || activePresetMeta?.voice || '', audience: $persona.audience || activePresetMeta?.audience || '', tone: t, intent: $persona.intent };
					}}
				/>
			</div>
			<!-- Intent: additive, does not clear preset -->
			<div class="intent-group">
				<TokenSelector
					axis="intent"
					tokens={getPersonaAxisTokensMeta(grammar, 'intent')}
					selected={$persona.intent ? [$persona.intent] : []}
					maxSelect={1}
					onToggle={(t) => {
						if ($persona.intent === t) $persona = { ...$persona, intent: '' };
						else $persona = { ...$persona, intent: t };
					}}
				/>
			</div>
		</div>
		{/if}

		{#if activeTab === 'task'}
		<div class="task-tab-section">
		<TokenSelector
			axis="task"
			tokens={getTaskTokens(grammar)}
			selected={$selected.task}
			maxSelect={1}
			onToggle={(t) => toggle('task', t)}
			onTabNext={goToNextTabInner}
			onTabPrev={focusActiveTabInner}
			{grammar}
			activeTokensByAxis={$selected}
			axisDescription={grammar?.axes?.axis_descriptions?.['task']}
			{suggestionScores}
			{embedder}
		/>
		<label class="input-group">
			<span class="input-label">--addendum <span class="input-hint">task directive</span></span>
			<textarea
				class="input-area"
				data-field="addendum"
				rows="4"
				placeholder="e.g. Focus on error handling, include examples…"
				bind:value={$addendum}
			></textarea>
		</label>
		</div>
		{/if}
		{#each AXES as axis (axis)}
			{#if activeTab === axis}
			<TokenSelector
				{axis}
				tokens={getAxisTokens(grammar, axis)}
				selected={$selected[axis] ?? []}
				maxSelect={softCap(axis)}
				onToggle={(t) => toggle(axis, t)}
				onTabNext={goToNextTabInner}
				onTabPrev={goToPrevTabInner}
				{grammar}
				activeTokensByAxis={$selected}
				axisDescription={grammar?.axes?.axis_descriptions?.[axis]}
				{suggestionScores}
				{embedder}
			/>
			{/if}
		{/each}

		<!-- Load command input (collapsible) — below axis panel for correct Tab order -->
		<div class="load-cmd-section">
			<button class="load-cmd-toggle" onclick={() => { cmdInputOpen = !cmdInputOpen; cmdInputWarnings = []; }}>
				<span class="load-cmd-toggle-label">Load command</span>
				<span class="load-cmd-caret">{cmdInputOpen ? '▲' : '▼'}</span>
			</button>
			{#if cmdInputOpen}
				<div class="load-cmd-body">
					<input
						class="load-cmd-input"
						type="text"
						placeholder="bar build show mean full plain --subject &quot;…&quot;"
						bind:value={cmdInput}
						onkeydown={(e) => e.key === 'Enter' && loadCommand()}
					/>
					<button class="load-cmd-btn" onclick={loadCommand}>Load</button>
					{#if cmdInputWarnings.length > 0}
						<div class="load-cmd-warnings">
							Unrecognized tokens: {cmdInputWarnings.map(t => `"${t}"`).join(', ')}
						</div>
					{/if}
				</div>
			{/if}
		</div>

		<PatternsLibrary {patterns} {starterPacks} {grammar} onLoad={loadPattern} />

		<!-- Shortcut legend — after axis panel so Tab flow is uninterrupted -->
		<details class="shortcut-legend">
			<summary class="shortcut-legend-summary">Keyboard shortcuts ▸</summary>
			<table class="shortcut-table">
				<thead>
					<tr><th>Keys</th><th>Action</th></tr>
				</thead>
				<tbody>
					<tr><td><kbd>←</kbd> <kbd>→</kbd> on tab-bar</td><td>Switch axis</td></tr>
					<tr><td><kbd>↑</kbd> <kbd>↓</kbd> <kbd>Home</kbd> <kbd>End</kbd> on tab-bar</td><td>Switch axis</td></tr>
					<tr><td>Arrow keys in panel</td><td>Navigate chips</td></tr>
					<tr><td><kbd>Enter</kbd> / <kbd>Space</kbd></td><td>Select focused chip</td></tr>
					<tr><td><kbd>Tab</kbd> from last chip</td><td>Advance to next axis</td></tr>
					<tr><td><kbd>Shift+Tab</kbd> from first chip</td><td>Retreat to previous axis</td></tr>
					<tr><td><kbd>⌘K</kbd> / <kbd>Ctrl+K</kbd></td><td>Clear all</td></tr>
					<tr><td><kbd>⌘⇧C</kbd> / <kbd>Ctrl+Shift+C</kbd></td><td>Copy command</td></tr>
					<tr><td><kbd>⌘⇧P</kbd> / <kbd>Ctrl+Shift+P</kbd></td><td>Copy rendered prompt</td></tr>
					<tr><td><kbd>⌘⇧U</kbd> / <kbd>Ctrl+Shift+U</kbd></td><td>Share URL</td></tr>
				<tr><td><kbd>⌘⇧L</kbd> / <kbd>Ctrl+Shift+L</kbd></td><td>Copy link</td></tr>
				<tr><td><kbd>Alt+.</kbd></td><td>Next axis (focus filter)</td></tr>
				<tr><td><kbd>Alt+,</kbd></td><td>Previous axis (focus filter)</td></tr>
				</tbody>
			</table>
		</details>

	</section>
{/if}
</div>

<style>
	/* Subject input */
	.input-group {
		display: flex;
		flex-direction: column;
		gap: 0.3rem;
		margin-bottom: 0.75rem;
	}

	.input-label {
		font-size: 0.75rem;
		font-family: var(--font-mono);
		color: var(--color-text-muted);
	}

	.input-hint { color: var(--color-text-muted); font-family: system-ui; font-style: italic; }

	.input-area {
		width: 100%;
		padding: 0.4rem 0.5rem;
		background: var(--color-bg);
		border: 1px solid var(--color-border);
		border-radius: var(--radius);
		color: var(--color-text);
		font-size: 0.82rem;
		resize: vertical;
		font-family: system-ui;
	}

	.input-area:focus {
		outline: none;
		border-color: var(--color-accent-muted);
	}

	/* Persona */
	.persona-section {
		border: 1px solid var(--color-border);
		border-radius: var(--radius);
		padding: 0.75rem;
		margin-bottom: 1rem;
	}

	.persona-header {
		font-size: 0.75rem;
		text-transform: uppercase;
		letter-spacing: 0.05em;
		color: var(--color-accent);
		font-weight: 600;
		margin-bottom: 0.6rem;
	}

	.axis-desc {
		font-size: 0.78rem;
		color: var(--color-text-muted);
		margin: 0 0 0.75rem 0;
		line-height: 1.4;
	}

	.persona-group { margin-bottom: 0.6rem; }
	.persona-group:last-child { margin-bottom: 0; }

	.persona-group-label {
		font-size: 0.7rem;
		color: var(--color-text-muted);
		margin-bottom: 0.35rem;
		text-transform: uppercase;
		letter-spacing: 0.04em;
	}

	.persona-chips { display: flex; flex-wrap: wrap; gap: 0.35rem; }

	.persona-chip-hint {
		display: block;
		font-size: 0.62rem;
		color: var(--color-text-muted);
		font-weight: 400;
		margin-top: 0.1rem;
		opacity: 0.75;
	}

	.persona-chip {
		padding: 0.2rem 0.55rem;
		background: transparent;
		border: 1px solid var(--color-border);
		border-radius: var(--radius);
		color: var(--color-text-muted);
		cursor: pointer;
		font-size: 0.78rem;
		font-family: system-ui;
	}

	.persona-chip:hover { border-color: var(--color-accent-muted); color: var(--color-text); }
	.persona-chip.active { background: var(--color-accent-muted); border-color: var(--color-accent); color: var(--color-text); }

	.persona-use-when {
		margin-top: 0.5rem;
		background: var(--color-surface);
		border: 1px solid var(--color-accent-muted);
		border-radius: var(--radius);
		font-size: 0.78rem;
		overflow: hidden;
	}

	.persona-use-when-label {
		display: block;
		font-size: 0.65rem;
		font-weight: 600;
		text-transform: uppercase;
		letter-spacing: 0.04em;
		color: var(--color-accent);
		margin-bottom: 0.2rem;
	}

	.persona-use-when-text {
		margin: 0;
		color: var(--color-text);
		line-height: 1.5;
	}

	.preset-detail-card { padding: 0; }

	.preset-detail-header {
		display: flex;
		flex-direction: column;
		gap: 0.3rem;
		padding: 0.5rem 0.6rem 0.45rem;
	}

	.preset-detail-name {
		font-size: 0.8rem;
		font-weight: 600;
		color: var(--color-accent);
	}

	.preset-detail-axes {
		display: flex;
		flex-wrap: wrap;
		gap: 0.25rem;
	}

	.preset-axis-tag {
		font-family: var(--font-mono);
		font-size: 0.65rem;
		padding: 0.1rem 0.35rem;
		background: color-mix(in srgb, var(--color-accent-muted) 50%, transparent);
		border: 1px solid color-mix(in srgb, var(--color-accent) 40%, transparent);
		border-radius: 3px;
		color: var(--color-text-muted);
	}

	.preset-detail-section {
		padding: 0.4rem 0.6rem;
		border-top: 1px solid var(--color-border);
	}

	.preset-detail-notes {
		background: color-mix(in srgb, var(--color-surface) 80%, var(--color-accent-muted));
	}

	.preset-detail-notes .persona-use-when-label {
		color: var(--color-text-muted);
	}

	.preset-heuristics {
		display: flex;
		flex-wrap: wrap;
		gap: 0.3rem;
		margin-top: 0.35rem;
	}

	.preset-heuristic-chip {
		font-size: 0.72rem;
		padding: 0.15rem 0.5rem;
		background: var(--color-accent-muted);
		border: 1px solid var(--color-accent);
		border-radius: 9999px;
		color: var(--color-text);
		font-family: monospace;
	}

	.preset-distinction-entry {
		margin: 0.25rem 0 0 0;
		color: var(--color-text);
		font-size: 0.78rem;
		line-height: 1.4;
	}

	.preset-distinction-entry:first-of-type { margin-top: 0.1rem; }

	.preset-distinction-entry code {
		font-size: 0.72rem;
		padding: 0.05rem 0.3rem;
		background: color-mix(in srgb, var(--color-accent-muted) 60%, transparent);
		border: 1px solid color-mix(in srgb, var(--color-accent) 40%, transparent);
		border-radius: 3px;
	}

	.preset-axis-summary {
		display: flex;
		flex-wrap: wrap;
		gap: 0.35rem;
		margin-top: 0.4rem;
	}

	.preset-axis-tag {
		font-size: 0.72rem;
		padding: 0.1rem 0.4rem;
		background: color-mix(in srgb, var(--color-accent-muted) 40%, transparent);
		border: 1px solid color-mix(in srgb, var(--color-accent) 30%, transparent);
		border-radius: 3px;
		color: var(--color-text-muted);
	}

	.override-group {
		border-left: 2px solid var(--color-border);
		padding-left: 0.75rem;
		margin-top: 0.75rem;
	}

	.override-group-label {
		font-size: 0.72rem;
		color: var(--color-text-muted);
		margin-bottom: 0.5rem;
		text-transform: uppercase;
		letter-spacing: 0.04em;
	}

	.intent-group {
		margin-top: 1rem;
	}

	/* Load command section */
	.load-cmd-section {
		border: 1px solid var(--color-border);
		border-radius: var(--radius);
		margin-bottom: 1rem;
		overflow: hidden;
	}

	.load-cmd-toggle {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 0.5rem 0.75rem;
		cursor: pointer;
		user-select: none;
		background: none;
		border: none;
		width: 100%;
		text-align: left;
		color: inherit;
		font-family: inherit;
	}

	.load-cmd-toggle:hover { background: var(--color-surface); }

	.load-cmd-toggle-label {
		font-size: 0.75rem;
		text-transform: uppercase;
		letter-spacing: 0.05em;
		color: var(--color-text-muted);
		font-weight: 600;
	}

	.load-cmd-caret {
		font-size: 0.6rem;
		color: var(--color-text-muted);
	}

	.load-cmd-body {
		padding: 0.5rem 0.75rem 0.75rem;
		border-top: 1px solid var(--color-border);
		display: flex;
		flex-direction: column;
		gap: 0.4rem;
	}

	.load-cmd-input {
		width: 100%;
		padding: 0.35rem 0.5rem;
		background: var(--color-bg);
		border: 1px solid var(--color-border);
		border-radius: var(--radius);
		color: var(--color-text);
		font-size: 0.8rem;
		font-family: var(--font-mono);
	}

	.load-cmd-input:focus {
		outline: none;
		border-color: var(--color-accent-muted);
	}

	.load-cmd-btn {
		align-self: flex-end;
		padding: 0.25rem 0.75rem;
		background: var(--color-accent-muted);
		border: 1px solid var(--color-accent);
		border-radius: var(--radius);
		color: var(--color-text);
		cursor: pointer;
		font-size: 0.8rem;
	}

	.load-cmd-btn:hover { background: var(--color-accent); }

	.load-cmd-warnings {
		font-size: 0.78rem;
		color: var(--color-warning);
		padding: 0.3rem 0.4rem;
		background: #2a1f10;
		border-radius: calc(var(--radius) - 2px);
	}

	.shortcut-legend {
		margin-bottom: 0.75rem;
		font-size: 0.78rem;
		color: var(--color-text-muted);
	}

	.shortcut-legend-summary {
		cursor: pointer;
		user-select: none;
		font-size: 0.75rem;
		color: var(--color-text-muted);
		letter-spacing: 0.02em;
	}

	.shortcut-legend-summary:hover { color: var(--color-text); }

	.shortcut-table {
		margin-top: 0.4rem;
		border-collapse: collapse;
		width: 100%;
	}

	.shortcut-table th {
		font-size: 0.7rem;
		text-transform: uppercase;
		letter-spacing: 0.04em;
		color: var(--color-text-muted);
		text-align: left;
		padding: 0.2rem 0.4rem;
		border-bottom: 1px solid var(--color-border);
	}

	.shortcut-table td {
		padding: 0.2rem 0.4rem;
		vertical-align: top;
	}

	.shortcut-table tr:not(:last-child) td {
		border-bottom: 1px solid color-mix(in srgb, var(--color-border) 40%, transparent);
	}

	.shortcut-table kbd {
		font-family: var(--font-mono);
		font-size: 0.72rem;
		background: var(--color-surface);
		border: 1px solid var(--color-border);
		border-radius: 3px;
		padding: 0.05rem 0.25rem;
	}

	@media (pointer: coarse) {
		.shortcut-legend { display: none; }
	}

	div.selector-panel-root {
		min-width: 0;
		width: 100%;
		max-width: 100%;
		box-sizing: border-box;
	}

	.selector-panel {
		position: relative;
		padding-left: 3px;
	}

	@keyframes slide-in-from-right {
		from { transform: translateX(30px); opacity: 0.8; }
		to   { transform: translateX(0);    opacity: 1;   }
	}
	@keyframes slide-in-from-left {
		from { transform: translateX(-30px); opacity: 0.8; }
		to   { transform: translateX(0);     opacity: 1;   }
	}

	.selector-panel.slide-next { animation: slide-in-from-right 0.18s ease-out; }
	.selector-panel.slide-prev { animation: slide-in-from-left  0.18s ease-out; }

	@media (prefers-reduced-motion: reduce) {
		.selector-panel.slide-next,
		.selector-panel.slide-prev { animation: none; }
	}

	.mode-switcher {
		display: flex;
		gap: 0.5rem;
		padding: 0.5rem 0;
	}

	.mode-btn {
		padding: 0.35rem 0.9rem;
		border: 1px solid var(--color-border, #444);
		border-radius: 6px;
		background: transparent;
		color: inherit;
		cursor: pointer;
		font-size: 0.85rem;
	}

	.mode-btn--active {
		background: var(--color-accent, #4a9eff);
		color: #fff;
		border-color: transparent;
	}

	.tab-bar {
		display: flex;
		gap: 0.25rem;
		overflow-x: auto;
		overflow-y: visible;
		margin-bottom: 1rem;
		padding-top: 4px;
		padding-left: 4px;
		padding-right: 4px;
		padding-bottom: 0.5rem;
		border-bottom: 1px solid var(--color-border);
		-webkit-overflow-scrolling: touch;
	}

	.tab {
		padding: 0.5rem 0.75rem;
		background: var(--color-surface);
		border: 1px solid var(--color-border);
		border-radius: var(--radius);
		color: var(--color-text-muted);
		cursor: pointer;
		font-size: 0.75rem;
		font-family: system-ui;
		white-space: nowrap;
	}

	.tab:hover {
		border-color: var(--color-accent-muted);
		color: var(--color-text);
	}

	.tab.active {
		background: var(--color-accent-muted);
		border-color: var(--color-accent);
		color: var(--color-text);
	}

	.loading { color: var(--color-text-muted); padding: 2rem; text-align: center; }

	@media (max-width: 767px) {
		.tab { min-height: 44px; }
		.persona-chip { min-height: 44px; padding: 0.5rem 0.75rem; }
		.load-cmd-toggle { min-height: 44px; }
		.input-area { font-size: 1rem; }
		.load-cmd-input { font-size: 1rem; }
	}
</style>
