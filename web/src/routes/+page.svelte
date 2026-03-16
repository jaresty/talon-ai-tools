<script lang="ts">
	import { onMount } from 'svelte';
	import { loadGrammar, getAxisTokens, getTaskTokens, getPersonaPresets, getPersonaAxisTokensMeta, getPresetHint, toPersonaSlug, AXES, type Grammar, type GrammarPattern, type StarterPack, getUsagePatterns, getStarterPacks } from '$lib/grammar.js';
	import { findConflicts } from '$lib/incompatibilities.js';
	import TokenSelector from '$lib/TokenSelector.svelte';
	import LLMPanel from '$lib/LLMPanel.svelte';
	import PatternsLibrary from '$lib/PatternsLibrary.svelte';
	import { renderPrompt, type PersonaState } from '$lib/renderPrompt.js';
	import { parseCommand } from '$lib/parseCommand.js';
	import { savePreset, listPresets, deletePreset, type SpaPreset } from '$lib/presets.js';

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
	let savedPresets = $state<SpaPreset[]>([]);
	let presetNameInput = $state('');
	let presetSaved = $state(false);

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
		refreshPresets();

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
			} else if (
				e.key.length === 1 &&
				e.key !== ' ' &&
				!e.ctrlKey && !e.metaKey && !e.altKey && !e.repeat
			) {
				const active = document.activeElement as HTMLElement | null;
				const tag = active?.tagName ?? '';
				if (tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT') return;
				if (active?.getAttribute('role') === 'option' || active?.closest?.('[role="listbox"]')) return;
				const filterEl = document.querySelector<HTMLInputElement>('.selector-panel .filter-input');
				if (!filterEl) return;
				e.preventDefault();
				filterEl.focus(); // onfocus handler clears filter (e.detail === 0)
				filterEl.value = e.key;
				filterEl.dispatchEvent(new InputEvent('input', { bubbles: true }));
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
	let activePresetMeta = $derived(grammar && persona.preset ? getPersonaPresets(grammar).find(p => p.key === persona.preset) ?? null : null);
	let promptText = $derived(grammar ? renderPrompt(grammar, selected, subject, addendum, persona) : '');

	let tokens = $derived.by(() => {
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
		return [...personaTokens, ...order.flatMap((axis) => selected[axis] ?? [])];
	});

	let command = $derived.by(() => {
		let cmd = tokens.length === 0 ? 'bar build' : `bar build ${tokens.join(' ')}`;
		if (subject.trim()) cmd += ` --subject "${subject.trim().replace(/"/g, '\\"')}"`;
		if (addendum.trim()) cmd += ` --addendum "${addendum.trim().replace(/"/g, '\\"')}"`;
		return cmd;
	});

	function refreshPresets() {
		savedPresets = listPresets(localStorage);
	}

	function handleSavePreset() {
		const name = presetNameInput.trim();
		if (!name) return;
		const axes: Record<string, string[]> = {};
		for (const [axis, toks] of Object.entries(selected)) axes[axis] = [...toks];
		savePreset(localStorage, name, tokens, axes, {
			preset: persona.preset || undefined,
			voice: persona.voice || undefined,
			audience: persona.audience || undefined,
			tone: persona.tone || undefined,
			intent: persona.intent || undefined
		});
		presetNameInput = '';
		refreshPresets();
		presetSaved = true;
		setTimeout(() => (presetSaved = false), 1500);
	}

	function handleLoadPreset(preset: SpaPreset) {
		selected = { task: [], completeness: [], scope: [], method: [], form: [], channel: [], directional: [], ...preset.result.axes };
		persona = {
			preset: preset.result.persona.preset ?? '',
			voice: preset.result.persona.voice ?? '',
			audience: preset.result.persona.audience ?? '',
			tone: preset.result.persona.tone ?? '',
			intent: preset.result.persona.intent ?? ''
		};
		// subject/addendum intentionally left unchanged
	}

	function handleDeletePreset(name: string) {
		deletePreset(localStorage, name);
		refreshPresets();
	}

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
	let touchStartedInModal = false;
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

	function handleTouchEnd(e: TouchEvent) {
		const dx = e.changedTouches[0].clientX - touchStartX;
		const dy = e.changedTouches[0].clientY - touchStartY;
		const target = e.target as Element;

		if (touchStartedInModal) {
			swipeAnimating = true;
			swipeOffset = 0;
			return;
		}

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
	let reviewPanelHeight = $state(0); // Tracks review panel height for dynamic layout padding
	let hasSelectedTokens = $derived(Object.values(selected).some((toks) => toks.length > 0));
	let previewPanelEl = $state<HTMLElement | null>(null);

	$effect(() => {
		if (!previewPanelEl) return;
		const update = () => {
			// On mobile the panel is position:static and flows naturally — no maxHeight constraint needed.
			if (window.innerWidth <= 767) {
				previewPanelEl!.style.maxHeight = '';
				return;
			}
			const rect = previewPanelEl!.getBoundingClientRect();
			const available = window.innerHeight - Math.max(rect.top, 16) - (reviewPanelHeight + 16);
			previewPanelEl!.style.maxHeight = available + 'px';
		};
		window.addEventListener('scroll', update, { passive: true });
		window.addEventListener('resize', update, { passive: true });
		update();
		return () => {
			window.removeEventListener('scroll', update);
			window.removeEventListener('resize', update);
		};
	});
	let hoveredDistinctionPreset = $state<string | null>(null);


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

<div class="layout" bind:this={layoutEl} style:padding-bottom="{reviewPanelHeight + 16}px" style:--review-h="{reviewPanelHeight + 16}px">
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
									class:chip--distinction-ref={hoveredDistinctionPreset === preset.key}
									onclick={() => {
										if (persona.preset === preset.key) {
											persona = { preset: '', voice: '', audience: '', tone: '', intent: persona.intent };
										} else {
											persona = { preset: preset.key, voice: '', audience: '', tone: '', intent: persona.intent };
										}
									}}
								>{preset.label}{#if getPresetHint(grammar, preset.key)}<span class="persona-chip-hint">{getPresetHint(grammar, preset.key)}</span>{/if}</button>
							{/each}
						</div>
						{#if persona.preset}
							{@const presetMeta = getPersonaPresets(grammar).find(p => p.key === persona.preset)}
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
							selected={persona.voice ? [persona.voice] : activePresetMeta?.voice ? [activePresetMeta.voice] : []}
							maxSelect={1}
							onToggle={(t) => {
								if (persona.voice === t) persona = { ...persona, preset: '', voice: '' };
								else persona = { preset: '', voice: t, audience: persona.audience, tone: persona.tone, intent: persona.intent };
							}}
						/>
						<TokenSelector
							axis="audience"
							tokens={getPersonaAxisTokensMeta(grammar, 'audience')}
							selected={persona.audience ? [persona.audience] : activePresetMeta?.audience ? [activePresetMeta.audience] : []}
							maxSelect={1}
							onToggle={(t) => {
								if (persona.audience === t) persona = { ...persona, preset: '', audience: '' };
								else persona = { preset: '', voice: persona.voice, audience: t, tone: persona.tone, intent: persona.intent };
							}}
						/>
						<TokenSelector
							axis="tone"
							tokens={getPersonaAxisTokensMeta(grammar, 'tone')}
							selected={persona.tone ? [persona.tone] : activePresetMeta?.tone ? [activePresetMeta.tone] : []}
							maxSelect={1}
							onToggle={(t) => {
								if (persona.tone === t) persona = { ...persona, preset: '', tone: '' };
								else persona = { preset: '', voice: persona.voice, audience: persona.audience, tone: t, intent: persona.intent };
							}}
						/>
					</div>
					<!-- Intent: additive, does not clear preset -->
					<div class="intent-group">
						<TokenSelector
							axis="intent"
							tokens={getPersonaAxisTokensMeta(grammar, 'intent')}
							selected={persona.intent ? [persona.intent] : []}
							maxSelect={1}
							onToggle={(t) => {
								if (persona.intent === t) persona = { ...persona, intent: '' };
								else persona = { ...persona, intent: t };
							}}
						/>
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

			<section class="preview-panel" class:visible={showPreview} bind:this={previewPanelEl}>
				<!-- Command preview -->
				<div class="command-box">
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

				<!-- Named preset panel (ADR-0165) -->
				<details class="presets-panel">
					<summary class="presets-summary">Presets</summary>
					<div class="presets-save-row">
						<input
							class="presets-name-input"
							type="text"
							placeholder="Preset name…"
							bind:value={presetNameInput}
							onkeydown={(e) => { if (e.key === 'Enter') handleSavePreset(); }}
						/>
						<button class="presets-save-btn" onclick={handleSavePreset} disabled={!presetNameInput.trim()}>
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
											<button class="preset-load-btn" onclick={() => handleLoadPreset(preset)}>Load</button>
											<button class="preset-delete-btn" onclick={() => handleDeletePreset(preset.name)}>✕</button>
										</div>
									</div>
									<code class="preset-item-tokens">{preset.tokens.join(' ')}</code>
								</li>
							{/each}
						</ul>
					{/if}
				</details>

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

				<LLMPanel {command} {subject} {addendum} />
			</section>
		</div>
	{/if}

	<!-- ADR-0157: Selected Token Review Panel - fixed bottom bar -->
	<div
		class="review-panel"
		class:review-panel-empty={!hasSelectedTokens}
		bind:clientHeight={reviewPanelHeight}
	>
		{#if hasSelectedTokens}
			{#each Object.entries(selected) as [axis, tokens]}
				{#each tokens as token (token)}
					{@const isConflict = conflicts.some(c => c.tokenA === token || c.tokenB === token)}
					<button
						class="review-panel-chip"
						class:conflict={isConflict}
						tabindex="0"
						onclick={() => toggle(axis, token)}
						onkeydown={(e) => {
							if (e.key === 'Enter' || e.key === ' ') {
								e.preventDefault();
								toggle(axis, token);
							}
						}}
					>
						{axis}={token}
						{#if isConflict} ⚠{/if}
					</button>
				{/each}
			{/each}
		{:else}
			Select tokens from the axes above
		{/if}
	</div>

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
		overflow-y: auto;
		scrollbar-width: thin;
		scrollbar-color: var(--color-border) transparent;
	}

	.preview-panel::-webkit-scrollbar {
		width: 4px;
	}

	.preview-panel::-webkit-scrollbar-track {
		background: transparent;
	}

	.preview-panel::-webkit-scrollbar-thumb {
		background: var(--color-border);
		border-radius: 2px;
	}

	.preview-panel::-webkit-scrollbar-thumb:hover {
		background: var(--color-accent-muted);
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

	/* Command box */
	.command-box {
		background: var(--color-surface);
		border: 1px solid var(--color-border);
		border-radius: var(--radius);
		padding: 1rem;
		margin-bottom: 0.75rem;
	}

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

	/* Mobile action overlay hidden on desktop; shown via .mobile-visible in media query */
	.action-row.action-overlay {
		display: none;
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

	.fab-btn {
		display: none;
	}

	.fab-backdrop {
		display: none;
	}

	/* Named preset panel (ADR-0165) */
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
	.preset-item-tokens {
		display: block;
		font-size: 0.7rem;
		color: var(--color-text-muted);
		margin-top: 0.15rem;
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}
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

	/* Preset detail card */
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
		/* FAB clearance: prevent chips from hiding under the fixed bottom-right FAB */
		.review-panel {
			padding-right: 4rem;
		}

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
