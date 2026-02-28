<script lang="ts">
	import { onMount } from 'svelte';
	import { loadGrammar, getAxisTokens, getTaskTokens, getPersonaPresets, getPersonaAxisTokens, getPersonaIntentTokens, toPersonaSlug, AXES, type Grammar, type GrammarPattern, type StarterPack, getUsagePatterns, getStarterPacks } from '$lib/grammar.js';
	import { findConflicts } from '$lib/incompatibilities.js';
	import TokenSelector from '$lib/TokenSelector.svelte';
	import LLMPanel from '$lib/LLMPanel.svelte';
	import PatternsLibrary from '$lib/PatternsLibrary.svelte';
	import { renderPrompt, type PersonaState } from '$lib/renderPrompt.js';
	import { parseCommand } from '$lib/parseCommand.js';

	const STORAGE_KEY = 'bar-prompt-state';

	let grammar: Grammar | null = $state(null);
	let error: string | null = $state(null);
	let patterns = $state<GrammarPattern[]>([]);
	let starterPacks = $state<StarterPack[]>([]);

	let selected = $state<Record<string, string[]>>({
		task: [],
		completeness: [],
		scope: [],
		method: [],
		form: [],
		channel: [],
		directional: []
	});

	let persona = $state<PersonaState>({ preset: '', voice: '', audience: '', tone: '', intent: '' });

	let subject = $state('');
	let addendum = $state('');
	let copied = $state(false);
	let shared = $state(false);
	let copiedPrompt = $state(false);

	// Serialize/deserialize prompt state
	function serialize(): string {
		return btoa(JSON.stringify({ selected, subject, addendum, persona }));
	}

	function deserialize(raw: string): void {
		try {
			const parsed = JSON.parse(atob(raw));
			if (parsed && typeof parsed === 'object') {
				if (parsed.selected) selected = { ...selected, ...parsed.selected };
				if (typeof parsed.subject === 'string') subject = parsed.subject;
				if (typeof parsed.addendum === 'string') addendum = parsed.addendum;
				if (parsed.persona && typeof parsed.persona === 'object') {
					persona = { preset: '', voice: '', audience: '', tone: '', ...parsed.persona };
				}
			}
		} catch {
			// ignore malformed state
		}
	}

	onMount(async () => {
		// Restore from URL hash first; fall back to localStorage
		const hash = window.location.hash.slice(1);
		if (hash && hash !== '/') {
			deserialize(hash);
		} else {
			const saved = localStorage.getItem(STORAGE_KEY);
			if (saved) deserialize(saved);
		}

		try {
			grammar = await loadGrammar();
			if (grammar) {
			patterns = getUsagePatterns(grammar);
			starterPacks = getStarterPacks(grammar);
		}
		} catch (e) {
			error = String(e);
		}

		// On desktop, focus the active tab so keyboard navigation works immediately
		if (!window.matchMedia('(hover: none)').matches) {
			setTimeout(focusActiveTab, 0);
		}

		function handleGlobalKey(e: KeyboardEvent) {
			if (e.key === 'k' && (e.ctrlKey || e.metaKey)) {
				e.preventDefault();
				clearState();
				(document.activeElement as HTMLElement | null)?.blur();
			} else if (e.key === 'c' && e.shiftKey && (e.ctrlKey || e.metaKey)) {
				e.preventDefault();
				copyCommand();
			} else if (e.key === 'p' && e.shiftKey && (e.ctrlKey || e.metaKey)) {
				e.preventDefault();
				copyPrompt();
			} else if (e.key === 'u' && e.shiftKey && (e.ctrlKey || e.metaKey)) {
				e.preventDefault();
				shareLink();
			} else if (e.code === 'Period' && e.altKey) {
				if ((e.target as HTMLElement).tagName === 'TEXTAREA') return;
				e.preventDefault();
				goToNextTab(false);
				setTimeout(focusFilterOrFirst, 0);
			} else if (e.code === 'Comma' && e.altKey) {
				if ((e.target as HTMLElement).tagName === 'TEXTAREA') return;
				e.preventDefault();
				goToPrevTab(false);
				setTimeout(focusFilterOrFirst, 0);
			}
		}
		document.addEventListener('keydown', handleGlobalKey);
		return () => document.removeEventListener('keydown', handleGlobalKey);
	});

	// Auto-save to localStorage on every state change
	$effect(() => {
		// Touch reactive dependencies
		const snap = serialize();
		localStorage.setItem(STORAGE_KEY, snap);
	});

	function softCap(axis: string): number {
		if (!grammar) return 1;
		return grammar.hierarchy.axis_soft_caps[axis] ?? 1;
	}

	function toggle(axis: string, token: string) {
		const cur = selected[axis] ?? [];
		if (cur.includes(token)) {
			selected[axis] = cur.filter((t) => t !== token);
		} else {
			const cap = softCap(axis);
			if (cur.length < cap) {
				selected[axis] = [...cur, token];
			} else if (cap === 1) {
				selected[axis] = [token];
			}
		}
	}

	let conflicts = $derived(grammar ? findConflicts(grammar, selected) : []);
	let promptText = $derived(grammar ? renderPrompt(grammar, selected, subject, addendum, persona) : '');

	let command = $derived.by(() => {
		if (!grammar) return '';
		const personaTokens: string[] = [];
		if (persona.preset) {
			personaTokens.push(`persona=${persona.preset}`);
		} else {
			if (persona.voice) personaTokens.push(toPersonaSlug(persona.voice));
			if (persona.audience) personaTokens.push(toPersonaSlug(persona.audience));
			if (persona.tone) personaTokens.push(persona.tone);
			if (persona.intent) personaTokens.push(persona.intent);
		}
		const order = ['task', 'completeness', 'scope', 'method', 'form', 'channel', 'directional'];
		const tokens = [...personaTokens, ...order.flatMap((axis) => selected[axis] ?? [])];
		let cmd = tokens.length === 0 ? 'bar build' : `bar build ${tokens.join(' ')}`;
		if (subject.trim()) cmd += ` --subject "${subject.trim().replace(/"/g, '\\"')}"`;
		if (addendum.trim()) cmd += ` --addendum "${addendum.trim().replace(/"/g, '\\"')}"`;
		return cmd;
	});

	function copyCommand() {
		navigator.clipboard.writeText(command);
		copied = true;
		setTimeout(() => (copied = false), 1500);
	}

	function copyPrompt() {
		if (!grammar) return;
		const text = renderPrompt(grammar, selected, subject, addendum, persona);
		navigator.clipboard.writeText(text);
		copiedPrompt = true;
		setTimeout(() => (copiedPrompt = false), 1500);
	}

	async function shareLink() {
		const encoded = serialize();
		const url = `${window.location.origin}${window.location.pathname}#${encoded}`;
		window.history.replaceState(null, '', `#${encoded}`);
		if (navigator.share) {
			await navigator.share({ url });
		} else {
			navigator.clipboard.writeText(url);
			shared = true;
			setTimeout(() => (shared = false), 1500);
		}
	}

	async function sharePromptNative() {
		if (!grammar) return;
		const text = renderPrompt(grammar, selected, subject, addendum, persona);
		if (navigator.share) {
			await navigator.share({ text });
		} else {
			navigator.clipboard.writeText(text);
			copiedPrompt = true;
			setTimeout(() => (copiedPrompt = false), 1500);
		}
	}

	let touchStartX = 0;
	let touchStartY = 0;
	let swipeOffset = $state(0);
	let swipeAnimating = $state(false);
	let panelSlideDir = $state<'next' | 'prev' | null>(null);

	// Per-instance capture listener on .layout absorbs ghost clicks after a swipe.
	// Using bind:this keeps the listener isolated to this component instance.
	let layoutEl = $state<HTMLElement | null>(null);
	let swipeCompletedAt = 0;
	$effect(() => {
		if (!layoutEl) return;
		const absorb = (e: MouseEvent) => {
			if (Date.now() - swipeCompletedAt < 600) {
				e.stopImmediatePropagation();
				swipeCompletedAt = 0;
			}
		};
		layoutEl.addEventListener('click', absorb, { capture: true });
		return () => {
			layoutEl?.removeEventListener('click', absorb);
		};
	});

	function handleTouchStart(e: TouchEvent) {
		touchStartX = e.touches[0].clientX;
		touchStartY = e.touches[0].clientY;
		swipeOffset = 0;
		swipeAnimating = false;
	}

	function handleTouchMove(e: TouchEvent) {
		const dx = e.touches[0].clientX - touchStartX;
		const dy = e.touches[0].clientY - touchStartY;
		if (Math.abs(dx) > Math.abs(dy)) {
			swipeOffset = dx;
		}
	}

	function handleTouchEnd(e: TouchEvent) {
		const dx = e.changedTouches[0].clientX - touchStartX;
		const dy = e.changedTouches[0].clientY - touchStartY;
		const target = e.target as Element;

		if (target.closest('input, textarea, select')) {
			swipeAnimating = true;
			swipeOffset = 0;
			return;
		}

		if (Math.abs(dx) < 50 || Math.abs(dy) >= Math.abs(dx)) {
			swipeAnimating = true;
			swipeOffset = 0;
			return;
		}

		e.preventDefault(); // belt-and-suspenders: suppresses ghost click in mobile browsers
		swipeCompletedAt = Date.now(); // layout capture listener absorbs the ghost click
		const dir = dx < 0 ? -1 : 1;
		const slideWidth = Math.max(window.innerWidth, 400);
		swipeAnimating = true;
		swipeOffset = dir * slideWidth; // slide out in the direction of the swipe

		setTimeout(() => {
			swipeAnimating = false;
			swipeOffset = 0;
			if (dx < 0) goToNextTab(false, false);
			else goToPrevTab(false, false);
		}, 250);
	}


	function clearState() {
		selected = { task: [], completeness: [], scope: [], method: [], form: [], channel: [], directional: [] };
		persona = { preset: '', voice: '', audience: '', tone: '', intent: '' };
		subject = '';
		addendum = '';
		window.history.replaceState(null, '', window.location.pathname);
		localStorage.removeItem(STORAGE_KEY);
	}

	function loadPattern(pattern: GrammarPattern) {
		selected = { task: [], completeness: [], scope: [], method: [], form: [], channel: [], directional: [], ...pattern.tokens };
	}

	let cmdInput = $state('');
	let cmdInputOpen = $state(false);
	let cmdInputWarnings = $state<string[]>([]);

	let activeTab = $state('task');
	let showPreview = $state(false); // Hidden by default; toggle reveals on mobile
	let fabOpen = $state(false); // FAB menu state
	let activePresetUseWhen = $state('');
	let activePresetGuidance = $state('');

	const AXES_WITH_PERSONA = ['persona', 'task', 'completeness', 'scope', 'method', 'form', 'channel', 'directional'];

	function focusActiveTab() {
		document.querySelector<HTMLElement>('[role="tab"][aria-selected="true"]')?.focus();
	}

	function focusFirstChip() {
		const chip = document.querySelector<HTMLElement>('[role="option"]');
		if (chip) { chip.focus(); return; }
		// Fallback for panels with no [role="option"] (e.g. persona)
		document.querySelector<HTMLElement>('.selector-panel button, .selector-panel select, .selector-panel input')?.focus();
	}

	function focusLastChip() {
		const chips = document.querySelectorAll<HTMLElement>('[role="option"]');
		const last = chips[chips.length - 1];
		last?.focus();
	}

	function goToNextTab(moveFocus = true, animate = true) {
		if (animate) panelSlideDir = 'next';
		const n = AXES_WITH_PERSONA.length;
		const cur = AXES_WITH_PERSONA.indexOf(activeTab);
		activeTab = AXES_WITH_PERSONA[(cur + 1) % n];
		if (moveFocus) setTimeout(focusFirstChip, 0);
	}

	function goToPrevTab(moveFocus = true, animate = true) {
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

	function focusFilterOrFirst() {
		const filterEl = document.querySelector<HTMLElement>('.selector-panel .filter-input');
		if (filterEl) { filterEl.focus(); return; }
		focusFirstChip();
	}

	function handleTabBarKey(e: KeyboardEvent) {
		const n = AXES_WITH_PERSONA.length;
		const cur = AXES_WITH_PERSONA.indexOf(activeTab);
		if (e.key === 'ArrowRight' || e.key === 'ArrowDown') {
			e.preventDefault();
			panelSlideDir = 'next';
			activeTab = AXES_WITH_PERSONA[(cur + 1) % n];
			setTimeout(focusActiveTab, 0);
		} else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') {
			e.preventDefault();
			panelSlideDir = 'prev';
			activeTab = AXES_WITH_PERSONA[(cur - 1 + n) % n];
			setTimeout(focusActiveTab, 0);
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

	function togglePreview() {
		showPreview = !showPreview;
	}

	function loadCommand() {
		if (!grammar || !cmdInput.trim()) return;
		const result = parseCommand(cmdInput, grammar);
		selected = { task: [], completeness: [], scope: [], method: [], form: [], channel: [], directional: [], ...result.selected };
		if (result.subject) subject = result.subject;
		if (result.addendum) addendum = result.addendum;
		if (result.persona.preset || result.persona.voice || result.persona.audience || result.persona.tone || result.persona.intent) {
			persona = result.persona;
		}
		cmdInputWarnings = result.unrecognized;
		if (result.unrecognized.length === 0) {
			cmdInput = '';
			cmdInputOpen = false;
		}
	}
</script>

<div class="layout" bind:this={layoutEl}>
	<header>
		<h1>Bar Prompt Builder</h1>
		<p class="subtitle">Token composition for structured prompts</p>
	</header>

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

	{#if error}
		<div class="error">Failed to load grammar: {error}</div>
	{:else if !grammar}
		<div class="loading">Loading grammar…</div>
	{:else}
		<div class="main">
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
									class:active={persona.preset === preset.key}
									onclick={() => {
										if (persona.preset === preset.key) {
											persona = { preset: '', voice: '', audience: '', tone: '', intent: persona.intent };
											activePresetUseWhen = '';
											activePresetGuidance = '';
										} else {
											persona = { preset: preset.key, voice: '', audience: '', tone: '', intent: persona.intent };
											activePresetUseWhen = grammar!.persona.use_when?.presets?.[preset.key] ?? '';
											activePresetGuidance = grammar!.persona.guidance?.presets?.[preset.key] ?? '';
										}
									}}
								>{preset.label}</button>
							{/each}
						</div>
						{#if persona.preset && activePresetUseWhen}
							<div class="persona-use-when">
								<span class="persona-use-when-label">When to use</span>
								<p class="persona-use-when-text">{activePresetUseWhen}</p>
							</div>
						{/if}
						{#if persona.preset && activePresetGuidance}
							<div class="persona-use-when persona-guidance">
								<span class="persona-use-when-label">Notes</span>
								<p class="persona-use-when-text">{activePresetGuidance}</p>
							</div>
						{/if}
					</div>

					<!-- Custom axes -->
					<div class="persona-group">
						<div class="persona-group-label">Custom</div>
						<div class="persona-selects">
							<label class="persona-select-label">
								<span>Voice</span>
								<select
									class="persona-select"
									value={persona.voice}
									onchange={(e) => { persona = { preset: '', voice: (e.target as HTMLSelectElement).value, audience: persona.audience, tone: persona.tone, intent: persona.intent }; }}
								>
									<option value="">—</option>
									{#each getPersonaAxisTokens(grammar, 'voice') as v (v)}
										<option value={v}>{v}</option>
									{/each}
								</select>
								{#if persona.voice && grammar.persona.use_when?.voice?.[persona.voice]}
									<span class="persona-hint">{grammar.persona.use_when.voice[persona.voice]}</span>
								{/if}
								{#if persona.voice && grammar.persona.guidance?.voice?.[persona.voice]}
									<span class="persona-hint persona-hint-note">{grammar.persona.guidance.voice[persona.voice]}</span>
								{/if}
							</label>
							<label class="persona-select-label">
								<span>Audience</span>
								<select
									class="persona-select"
									value={persona.audience}
									onchange={(e) => { persona = { preset: '', voice: persona.voice, audience: (e.target as HTMLSelectElement).value, tone: persona.tone, intent: persona.intent }; }}
								>
									<option value="">—</option>
									{#each getPersonaAxisTokens(grammar, 'audience') as a (a)}
										<option value={a}>{a}</option>
									{/each}
								</select>
								{#if persona.audience && grammar.persona.use_when?.audience?.[persona.audience]}
									<span class="persona-hint">{grammar.persona.use_when.audience[persona.audience]}</span>
								{/if}
								{#if persona.audience && grammar.persona.guidance?.audience?.[persona.audience]}
									<span class="persona-hint persona-hint-note">{grammar.persona.guidance.audience[persona.audience]}</span>
								{/if}
							</label>
							<label class="persona-select-label">
								<span>Tone</span>
								<select
									class="persona-select"
									value={persona.tone}
									onchange={(e) => { persona = { preset: '', voice: persona.voice, audience: persona.audience, tone: (e.target as HTMLSelectElement).value, intent: persona.intent }; }}
								>
									<option value="">—</option>
									{#each getPersonaAxisTokens(grammar, 'tone') as t (t)}
										<option value={t}>{t}</option>
									{/each}
								</select>
								{#if persona.tone && grammar.persona.use_when?.tone?.[persona.tone]}
									<span class="persona-hint">{grammar.persona.use_when.tone[persona.tone]}</span>
								{/if}
								{#if persona.tone && grammar.persona.guidance?.tone?.[persona.tone]}
									<span class="persona-hint persona-hint-note">{grammar.persona.guidance.tone[persona.tone]}</span>
								{/if}
							</label>
							<label class="persona-select-label">
								<span>Intent</span>
								<select
									class="persona-select"
									value={persona.intent}
									onchange={(e) => { persona = { preset: persona.preset, voice: persona.voice, audience: persona.audience, tone: persona.tone, intent: (e.target as HTMLSelectElement).value }; }}
								>
									<option value="">—</option>
									{#each getPersonaIntentTokens(grammar) as it (it)}
										<option value={it}>{it}</option>
									{/each}
								</select>
								{#if persona.intent && grammar.persona.use_when?.intent?.[persona.intent]}
									<span class="persona-hint">{grammar.persona.use_when.intent[persona.intent]}</span>
								{/if}
								{#if persona.intent && grammar.persona.guidance?.intent?.[persona.intent]}
									<span class="persona-hint persona-hint-note">{grammar.persona.guidance.intent[persona.intent]}</span>
								{/if}
							</label>
						</div>
					</div>
				</div>
				{/if}

				{#if activeTab === 'task'}
				<TokenSelector
					axis="task"
					tokens={getTaskTokens(grammar)}
					selected={selected.task}
					maxSelect={1}
					onToggle={(t) => toggle('task', t)}
					onTabNext={goToNextTab}
					onTabPrev={focusActiveTab}
					{grammar}
					activeTokensByAxis={selected}
					axisDescription={grammar?.axes?.axis_descriptions?.['task']}
				/>
				{/if}
				{#each AXES as axis (axis)}
					{#if activeTab === axis}
					<TokenSelector
						{axis}
						tokens={getAxisTokens(grammar, axis)}
						selected={selected[axis] ?? []}
						maxSelect={softCap(axis)}
						onToggle={(t) => toggle(axis, t)}
						onTabNext={goToNextTab}
						onTabPrev={goToPrevTab}
						{grammar}
						activeTokensByAxis={selected}
						axisDescription={grammar?.axes?.axis_descriptions?.[axis]}
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
						<tr><td><kbd>Alt+.</kbd></td><td>Next axis (focus filter)</td></tr>
						<tr><td><kbd>Alt+,</kbd></td><td>Previous axis (focus filter)</td></tr>
						</tbody>
					</table>
				</details>
			</section>

			<button class="preview-toggle" onclick={togglePreview}>
				{showPreview ? 'Hide Output' : 'Show Output'}
			</button>

			<section class="preview-panel" class:visible={showPreview}>
				<!-- Conflict warnings -->
				{#if conflicts.length > 0}
					<div class="conflicts">
						<div class="conflicts-header">⚠ Incompatible tokens</div>
						{#each conflicts as c}
							<div class="conflict-row">
								<code>{c.tokenA}</code> conflicts with <code>{c.tokenB}</code>
							</div>
						{/each}
					</div>
				{/if}

				<!-- Command preview -->
				<div class="command-box" class:has-conflicts={conflicts.length > 0}>
					<div class="command-label">Command</div>
					<code class="command">{command}</code>
					<!-- Desktop action row (always visible on desktop) -->
					<div class="action-row">
						<button class="copy-btn" onclick={copyCommand}>
							{copied ? '✓ Copied' : 'Copy cmd'}
						</button>
						<button class="copy-prompt-btn" onclick={copyPrompt}>
							{copiedPrompt ? '✓ Copied' : 'Copy prompt'}
						</button>
						<button class="share-prompt-btn" onclick={sharePromptNative}>
							Share prompt
						</button>
						<button class="share-link-btn" onclick={shareLink}>
							{shared ? '✓ Link copied' : 'Share link'}
						</button>
						<button class="clear-btn" onclick={clearState} title="Clear all (⌘K) | Copy cmd (⌘⇧C) | Copy prompt (⌘⇧P) | Share (⌘⇧U)">Clear</button>
					</div>
				</div>

				<!-- Rendered prompt -->
				<details class="prompt-preview-section">
					<summary class="prompt-preview-label">Rendered Prompt</summary>
					<pre class="prompt-preview">{promptText}</pre>
				</details>

				<!-- Subject / addendum inputs -->
				<div class="inputs">
					<label class="input-group">
						<span class="input-label">--subject <span class="input-hint">source material</span></span>
						<textarea
							class="input-area"
							rows="6"
							placeholder="Paste code, document, or topic…"
							bind:value={subject}
						></textarea>
					</label>

					<label class="input-group">
						<span class="input-label">--addendum <span class="input-hint">task directive</span></span>
						<textarea
							class="input-area"
							rows="4"
							placeholder="e.g. Focus on error handling, include examples…"
							bind:value={addendum}
						></textarea>
					</label>
				</div>

				<!-- Selected token chips -->
				{#if Object.values(selected).some((toks) => toks.length > 0)}
					<div class="selected-chips">
						{#each Object.entries(selected) as [axis, tokens]}
							{#each tokens as token (token)}
								<span
									class="selected-chip"
									role="button"
									tabindex="0"
									onclick={() => toggle(axis, token)}
									onkeydown={(e) => {
										if (e.key === 'Enter' || e.key === ' ') {
											e.preventDefault();
											toggle(axis, token);
										}
									}}
								>
									{token} ×
								</span>
							{/each}
						{/each}
					</div>
				{/if}

				<LLMPanel {command} {subject} {addendum} />
			</section>
		</div>
	{/if}

	<!-- FAB and mobile action overlay — always accessible, outside preview panel -->
	<button class="fab-btn" onclick={() => { if (Date.now() - swipeCompletedAt >= 600) fabOpen = !fabOpen; }} aria-label="Actions">
		{fabOpen ? '✕' : '⋯'}
	</button>
	{#if fabOpen}
		<!-- svelte-ignore a11y_click_events_have_key_events -->
		<!-- svelte-ignore a11y_no_static_element_interactions -->
		<div class="fab-backdrop" onclick={() => fabOpen = false}></div>
	{/if}
	<div class="action-row action-overlay" class:mobile-visible={fabOpen}>
		<button class="copy-btn" onclick={copyCommand}>
			{copied ? '✓ Copied' : 'Copy cmd'}
		</button>
		<button class="copy-prompt-btn" onclick={copyPrompt}>
			{copiedPrompt ? '✓ Copied' : 'Copy prompt'}
		</button>
		<button class="share-prompt-btn" onclick={sharePromptNative}>
			Share prompt
		</button>
		<button class="share-link-btn" onclick={shareLink}>
			{shared ? '✓ Link copied' : 'Share link'}
		</button>
		<button class="clear-btn" onclick={clearState} title="Clear all (⌘K) | Copy cmd (⌘⇧C) | Copy prompt (⌘⇧P) | Share (⌘⇧U)">Clear</button>
	</div>
</div>

<style>
	.layout {
		max-width: 1200px;
		margin: 0 auto;
		padding: 1.5rem;
		padding-top: calc(1.5rem + env(safe-area-inset-top));
	}

	header {
		margin-bottom: 1.5rem;
		border-bottom: 1px solid var(--color-border);
		padding-bottom: 1rem;
	}

	h1 { font-size: 1.4rem; color: var(--color-accent); }
	.subtitle { font-size: 0.85rem; color: var(--color-text-muted); margin-top: 0.25rem; }

	.loading, .error { color: var(--color-text-muted); padding: 2rem; text-align: center; }
	.error { color: #f7768e; }

	.main {
		display: grid;
		grid-template-columns: 1fr 340px;
		gap: 1.5rem;
		align-items: start;
		overflow-x: hidden; /* prevent horizontal scroll during swipe slide-out */
	}

	.preview-panel {
		position: sticky;
		top: 1rem;
	}

	.preview-toggle {
		display: none;
		width: 100%;
		padding: 0.75rem;
		background: var(--color-accent-muted);
		border: 1px solid var(--color-accent);
		border-radius: var(--radius);
		color: var(--color-text);
		cursor: pointer;
		font-size: 1rem;
		margin-bottom: 1rem;
	}

	.preview-panel.hidden {
		display: none;
	}

	/* Conflicts */
	.conflicts {
		background: #2a1f10;
		border: 1px solid var(--color-warning);
		border-radius: var(--radius);
		padding: 0.75rem;
		margin-bottom: 0.75rem;
		font-size: 0.82rem;
	}

	.conflicts-header {
		color: var(--color-warning);
		font-weight: 600;
		margin-bottom: 0.4rem;
	}

	.conflict-row { color: var(--color-text-muted); margin-top: 0.25rem; }
	.conflict-row code { color: var(--color-warning); font-family: var(--font-mono); }

	/* Command box */
	.command-box {
		background: var(--color-surface);
		border: 1px solid var(--color-border);
		border-radius: var(--radius);
		padding: 1rem;
		margin-bottom: 0.75rem;
	}

	.command-box.has-conflicts { border-color: var(--color-warning); }

	.command-label {
		font-size: 0.75rem;
		text-transform: uppercase;
		letter-spacing: 0.05em;
		color: var(--color-text-muted);
		margin-bottom: 0.5rem;
	}

	.command {
		display: block;
		font-family: var(--font-mono);
		font-size: 0.8rem;
		word-break: break-all;
		margin-bottom: 0.75rem;
		color: var(--color-success);
		line-height: 1.5;
	}

	.action-row {
		display: flex;
		gap: 0.5rem;
		flex-wrap: wrap;
	}

	.copy-btn, .copy-prompt-btn, .share-prompt-btn, .share-link-btn, .clear-btn {
		padding: 0.3rem 0.75rem;
		background: var(--color-accent-muted);
		border: 1px solid var(--color-accent);
		border-radius: var(--radius);
		color: var(--color-text);
		cursor: pointer;
		font-size: 0.8rem;
	}

	.copy-btn:hover, .copy-prompt-btn:hover, .share-prompt-btn:hover, .share-link-btn:hover { background: var(--color-accent); }

	.copy-prompt-btn {
		border-color: var(--color-success);
		color: var(--color-success);
	}

	.copy-prompt-btn:hover { background: var(--color-success); color: var(--color-bg); }

	.clear-btn {
		background: transparent;
		border-color: var(--color-border);
		color: var(--color-text-muted);
	}

	.clear-btn:hover { border-color: #f7768e; color: #f7768e; }

	.fab-btn {
		display: none;
	}

	.fab-backdrop {
		display: none;
	}

	/* Rendered prompt preview */
	.prompt-preview-section {
		margin-bottom: 0.75rem;
		border: 1px solid var(--color-border);
		border-radius: var(--radius);
		overflow: hidden;
	}

	.prompt-preview-label {
		padding: 0.4rem 0.75rem;
		font-size: 0.75rem;
		text-transform: uppercase;
		letter-spacing: 0.05em;
		color: var(--color-text-muted);
		cursor: pointer;
		user-select: none;
	}

	.prompt-preview-label:hover { color: var(--color-text); }

	.prompt-preview {
		font-family: var(--font-mono);
		font-size: 0.75rem;
		line-height: 1.5;
		color: var(--color-text);
		padding: 0.5rem 0.75rem;
		margin: 0;
		white-space: pre-wrap;
		word-break: break-word;
		background: var(--color-bg);
		border-top: 1px solid var(--color-border);
		max-height: 300px;
		overflow-y: auto;
	}

	/* Inputs */
	.inputs { margin-bottom: 0.75rem; }

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

	/* Selected chips */
	.selected-chips { display: flex; flex-wrap: wrap; gap: 0.4rem; }

	.selected-chip {
		padding: 0.2rem 0.5rem;
		background: var(--color-accent-muted);
		border: 1px solid var(--color-accent);
		border-radius: var(--radius);
		font-family: var(--font-mono);
		font-size: 0.8rem;
		cursor: pointer;
		user-select: none;
	}

	.selected-chip:hover { background: #6b3040; border-color: #f7768e; }

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
		padding: 0.5rem 0.6rem;
		background: var(--color-surface);
		border: 1px solid var(--color-accent-muted);
		border-radius: var(--radius);
		font-size: 0.78rem;
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

	.persona-hint {
		font-size: 0.68rem;
		color: var(--color-text-muted);
		line-height: 1.4;
		font-style: italic;
	}

	.persona-hint-note {
		color: var(--color-accent);
		font-style: normal;
	}

	.persona-guidance {
		border-color: color-mix(in srgb, var(--color-accent-muted) 60%, transparent);
		background: color-mix(in srgb, var(--color-surface) 80%, var(--color-accent-muted));
	}

	.persona-guidance .persona-use-when-label {
		color: var(--color-text-muted);
	}

	.persona-selects { display: flex; gap: 0.5rem; flex-wrap: wrap; }

	.persona-select-label {
		display: flex;
		flex-direction: column;
		gap: 0.2rem;
		font-size: 0.72rem;
		color: var(--color-text-muted);
		flex: 1;
		min-width: 90px;
	}

	.persona-select {
		background: var(--color-bg);
		border: 1px solid var(--color-border);
		border-radius: var(--radius);
		color: var(--color-text);
		font-size: 0.78rem;
		padding: 0.2rem 0.35rem;
	}

	.persona-select:focus { outline: none; border-color: var(--color-accent-muted); }

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

	.selector-panel {
		position: relative;
		padding-left: 3px; /* prevent focus outline from being clipped by parent overflow-x:hidden */
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

	@media (max-width: 767px) {
		.preview-toggle {
			display: block;
		}

		.preview-panel {
			position: static;
			display: none;
		}

		.preview-panel.visible {
			display: block;
		}

		/* Desktop action-row inside command-box — hide on mobile (replaced by overlay) */
		.command-box .action-row {
			display: none;
		}

		.main {
			grid-template-columns: 1fr;
		}

		.persona-selects {
			flex-direction: column;
		}

		.persona-select-label {
			min-width: 100%;
		}

		/* FAB — always visible at layout root, fixed bottom-right */
		.fab-btn {
			display: flex;
			align-items: center;
			justify-content: center;
			width: 44px;
			height: 44px;
			background: var(--color-accent);
			border: none;
			border-radius: 50%;
			color: var(--color-bg);
			font-size: 1.25rem;
			cursor: pointer;
			position: fixed;
			bottom: 1.5rem;
			right: 1.5rem;
			z-index: 150;
			box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
		}

		/* Backdrop to dismiss action overlay */
		.fab-backdrop {
			display: block;
			position: fixed;
			inset: 0;
			z-index: 140;
		}

		/* Mobile action overlay — fixed above FAB, always reachable */
		.action-overlay {
			display: none;
		}

		.action-overlay.mobile-visible {
			display: flex;
			flex-direction: column;
			gap: 0.5rem;
			position: fixed;
			bottom: 5rem;
			right: 1rem;
			z-index: 150;
			background: var(--color-surface);
			border: 1px solid var(--color-border);
			border-radius: var(--radius);
			padding: 0.5rem;
			box-shadow: 0 4px 16px rgba(0, 0, 0, 0.4);
			min-width: 180px;
		}

		.action-overlay button {
			width: 100%;
			min-height: 44px;
			justify-content: center;
		}

		.copy-btn, .copy-prompt-btn, .share-prompt-btn, .share-link-btn, .clear-btn {
			min-height: 44px;
		}

		/* Touch targets: tabs, persona chips, selected chips, load-cmd-toggle */
		.tab {
			min-height: 44px;
		}

		.persona-chip {
			min-height: 44px;
			padding: 0.5rem 0.75rem;
		}

		.selected-chip {
			min-height: 44px;
			padding: 0.5rem 0.75rem;
			display: inline-flex;
			align-items: center;
		}

		.load-cmd-toggle {
			min-height: 44px;
		}

		/* iOS auto-zoom prevention: font-size must be ≥16px on inputs */
		.input-area {
			font-size: 1rem;
		}

		.load-cmd-input {
			font-size: 1rem;
		}
	}
</style>
