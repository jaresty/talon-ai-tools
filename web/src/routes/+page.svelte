<script lang="ts">
	import { onMount } from 'svelte';
	import { loadGrammar, getAxisTokens, getTaskTokens, toPersonaSlug, toAxisTokenSlug, buildCommandTokens, AXES, type GrammarPattern, type StarterPack, getUsagePatterns, getStarterPacks } from '$lib/grammar.js';
	import { findConflicts } from '$lib/incompatibilities.js';
	import PreviewPanel from '$lib/PreviewPanel.svelte';
	import { renderPrompt, type PersonaState } from '$lib/renderPrompt.js';
	import SequencesPanel from '$lib/SequencesPanel.svelte';
	import SelectorPanel from '$lib/SelectorPanel.svelte';

	import ReviewPanel from '$lib/ReviewPanel.svelte';
	import { parseCommand } from '$lib/parseCommand.js';
	import { savePreset, listPresets, deletePreset, type SpaPreset } from '$lib/presets.js';
	import { addHistoryEntry, loadHistory, deleteHistoryEntry, clearHistory, type HistoryEntry } from '$lib/history.js';
	import { encodeState, decodeState } from '$lib/stateCodec.js';
	import { bm25Score } from '$lib/bm25.js';
	import { createEmbedder } from '$lib/embedder.js';
	import { selected, persona, subject, addendum, grammar as grammarStore, conflicts as conflictsStore } from '$lib/stores.js';

	const embedder = createEmbedder();

	const STORAGE_KEY = 'bar-prompt-state';
	const RELEASE_NOTE_KEY = 'bar-release-note-gate-falsify-split-dismissed';

	let releaseNoteDismissed = $state(false);

	function dismissReleaseNote() {
		releaseNoteDismissed = true;
		localStorage.setItem(RELEASE_NOTE_KEY, '1');
	}

	let error: string | null = $state(null);
	let patterns = $state<GrammarPattern[]>([]);
	let starterPacks = $state<StarterPack[]>([]);

	// Initialize selected store with axis keys
	$selected = { task: [], completeness: [], scope: [], method: [], form: [], channel: [], directional: [] };
	let copied = $state(false);
	let shared = $state(false);
	let copiedPrompt = $state(false);
	let linkCopied = $state(false);
	let savedPresets = $state<SpaPreset[]>([]);
	let presetNameInput = $state('');
	let presetSaved = $state(false);
	let historyEntries = $state<HistoryEntry[]>([]);

	// Serialize/deserialize prompt state
	function serialize(): string {
		return encodeState({ selected: $selected, subject: $subject, addendum: $addendum, persona: $persona });
	}

	function deserialize(raw: string): void {
		const parsed = decodeState(raw);
		if (parsed && typeof parsed === 'object') {
			const p = parsed as Record<string, unknown>;
			if (p.selected) $selected = { ...$selected, ...(p.selected as Record<string, string[]>) };
			if (typeof p.subject === 'string') $subject = p.subject;
			if (typeof p.addendum === 'string') $addendum = p.addendum;
			if (p.persona && typeof p.persona === 'object') {
				$persona = { preset: '', voice: '', audience: '', tone: '', ...(p.persona as PersonaState) };
			}
		}
	}

	onMount(async () => {
		// Restore from URL hash first; fall back to localStorage
		const hash = window.location.hash.slice(1);
		if (hash && hash !== '/') {
			deserialize(hash);
			addHistoryEntry(localStorage, { hash, trigger: 'open-link', subject_preview: '', command_preview: '' });
		} else {
			const saved = localStorage.getItem(STORAGE_KEY);
			if (saved) deserialize(saved);
		releaseNoteDismissed = !!localStorage.getItem(RELEASE_NOTE_KEY);
		}
		refreshPresets();
		refreshHistory();

		try {
			$grammarStore = await loadGrammar();
			if ($grammarStore) {
				patterns = getUsagePatterns($grammarStore);
				starterPacks = getStarterPacks($grammarStore);
			}
		} catch (e) {
			error = String(e);
		}

		// On desktop, focus the active tab so keyboard navigation works immediately
		if (!window.matchMedia('(hover: none)').matches) {
			setTimeout(() => selectorPanelEl?.focusActiveTab(), 0);
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
			} else if (e.key === 'l' && e.shiftKey && (e.ctrlKey || e.metaKey)) {
				e.preventDefault();
				copyLink();
			} else if (e.code === 'Period' && e.altKey) {
				if ((e.target as HTMLElement).tagName === 'TEXTAREA') return;
				e.preventDefault();
				selectorPanelEl?.goToNextTab();
				setTimeout(() => selectorPanelEl?.focusFilterOrFirst(), 0);
			} else if (e.code === 'Comma' && e.altKey) {
				if ((e.target as HTMLElement).tagName === 'TEXTAREA') return;
				e.preventDefault();
				selectorPanelEl?.goToPrevTab();
				setTimeout(() => selectorPanelEl?.focusFilterOrFirst(), 0);
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

	// Keep conflicts store in sync
	$effect(() => { $conflictsStore = $grammarStore ? findConflicts($grammarStore, $selected) : []; });

	let promptText = $derived($grammarStore ? renderPrompt($grammarStore, $selected, $subject, $addendum, $persona) : '');

	// ADR-0233: BM25 suggestion scores — derived from subject + addendum to dim irrelevant chips
	let suggestionScores = $derived.by(() => {
		const query = ($subject + ' ' + $addendum).trim();
		if (!$grammarStore || query.length < 10) return new Map<string, number>();
		const allTokens = [
			...getTaskTokens($grammarStore),
			...AXES.flatMap(ax => getAxisTokens($grammarStore!, ax))
		];
		return bm25Score(allTokens, query);
	});

	let tokens = $derived.by(() => {
		const personaTokens: string[] = [];
		if ($persona.preset) {
			personaTokens.push(`persona=${$persona.preset}`);
		} else {
			if ($persona.voice) personaTokens.push(toPersonaSlug($persona.voice));
			if ($persona.audience) personaTokens.push(toPersonaSlug($persona.audience));
			if ($persona.tone) personaTokens.push($persona.tone);
			if ($persona.intent) personaTokens.push($persona.intent);
		}
		return [...personaTokens, ...buildCommandTokens($selected, toAxisTokenSlug)];
	});

	let command = $derived.by(() => {
		let cmd = tokens.length === 0 ? 'bar build' : `bar build ${tokens.join(' ')}`;
		if ($subject.trim()) cmd += ` --subject "${$subject.trim().replace(/"/g, '\\"')}"`;
		if ($addendum.trim()) cmd += ` --addendum "${$addendum.trim().replace(/"/g, '\\"')}"`;
		return cmd;
	});

	function refreshPresets() {
		savedPresets = listPresets(localStorage);
	}

	function refreshHistory() {
		historyEntries = loadHistory(localStorage);
	}

	function handleSavePreset() {
		const name = presetNameInput.trim();
		if (!name) return;
		const axes: Record<string, string[]> = {};
		for (const [axis, toks] of Object.entries($selected)) axes[axis] = [...toks];
		savePreset(localStorage, name, tokens, axes, {
			preset: $persona.preset || undefined,
			voice: $persona.voice || undefined,
			audience: $persona.audience || undefined,
			tone: $persona.tone || undefined,
			intent: $persona.intent || undefined
		});
		presetNameInput = '';
		refreshPresets();
		presetSaved = true;
		setTimeout(() => (presetSaved = false), 1500);
	}

	function handleLoadPreset(preset: SpaPreset) {
		$selected = { task: [], completeness: [], scope: [], method: [], form: [], channel: [], directional: [], ...preset.result.axes };
		$persona = {
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
		addHistoryEntry(localStorage, { hash: serialize(), trigger: 'copy-command', subject_preview: $subject.slice(0, 80), command_preview: command });
		refreshHistory();
		copied = true;
		setTimeout(() => (copied = false), 1500);
	}

	function copyPrompt() {
		if (!$grammarStore) return;
		const text = renderPrompt($grammarStore, $selected, $subject, $addendum, $persona);
		navigator.clipboard.writeText(text);
		addHistoryEntry(localStorage, { hash: serialize(), trigger: 'copy-prompt', subject_preview: $subject.slice(0, 80), command_preview: command });
		refreshHistory();
		copiedPrompt = true;
		setTimeout(() => (copiedPrompt = false), 1500);
	}

	async function shareLink() {
		const encoded = serialize();
		const url = `${window.location.origin}${window.location.pathname}#${encoded}`;
		window.history.replaceState(null, '', `#${encoded}`);
		addHistoryEntry(localStorage, { hash: encoded, trigger: 'share-link', subject_preview: $subject.slice(0, 80), command_preview: command });
		refreshHistory();
		if (navigator.share) {
			await navigator.share({ url });
		} else {
			navigator.clipboard.writeText(url);
			shared = true;
			setTimeout(() => (shared = false), 1500);
		}
	}

	async function copyLink() {
		const encoded = serialize();
		const url = `${window.location.origin}${window.location.pathname}#${encoded}`;
		window.history.replaceState(null, '', `#${encoded}`);
		await navigator.clipboard.writeText(url);
		addHistoryEntry(localStorage, { hash: encoded, trigger: 'copy-link', subject_preview: $subject.slice(0, 80), command_preview: command });
		refreshHistory();
		linkCopied = true;
		setTimeout(() => (linkCopied = false), 1500);
	}

	async function sharePromptNative() {
		if (!$grammarStore) return;
		const text = renderPrompt($grammarStore, $selected, $subject, $addendum, $persona);
		addHistoryEntry(localStorage, { hash: serialize(), trigger: 'share-prompt', subject_preview: $subject.slice(0, 80), command_preview: command });
		refreshHistory();
		if (navigator.share) {
			await navigator.share({ text });
		} else {
			navigator.clipboard.writeText(text);
			copiedPrompt = true;
			setTimeout(() => (copiedPrompt = false), 1500);
		}
	}

	let layoutEl = $state<HTMLElement | null>(null);
	let selectorPanelEl = $state<{ focusFilterOrFirst: () => void; goToNextTab: () => void; goToPrevTab: () => void; focusActiveTab: () => void; getSwipeCompletedAt: () => number } | null>(null);

	$effect(() => {
		if (!layoutEl) return;
		const absorb = (e: MouseEvent) => {
			const completedAt = selectorPanelEl?.getSwipeCompletedAt() ?? 0;
			if (Date.now() - completedAt < 600) {
				e.stopImmediatePropagation();
			}
		};
		layoutEl.addEventListener('click', absorb, { capture: true });
		return () => layoutEl?.removeEventListener('click', absorb);
	});

	function clearState() {
		$selected = { task: [], completeness: [], scope: [], method: [], form: [], channel: [], directional: [] };
		$persona = { preset: '', voice: '', audience: '', tone: '', intent: '' };
		$subject = '';
		$addendum = '';
		window.history.replaceState(null, '', window.location.pathname);
		localStorage.removeItem(STORAGE_KEY);
	}

	let activeMode = $state<'build' | 'sequences'>('build');
	let showPreview = $state(false);
	let fabOpen = $state(false);
	let reviewPanelHeight = $state(0);
	let hasPersonaTokens = $derived(Object.values($persona).some((v) => v.length > 0));
	let hasSelectedTokens = $derived(Object.values($selected).some((toks) => toks.length > 0) || hasPersonaTokens);
	let previewPanelEl = $state<HTMLElement | null>(null);

	$effect(() => {
		if (!previewPanelEl) return;
		const update = () => {
			if (window.innerWidth <= 767) { previewPanelEl!.style.maxHeight = ''; return; }
			const rect = previewPanelEl!.getBoundingClientRect();
			const available = window.innerHeight - Math.max(rect.top, 16) - (reviewPanelHeight + 16);
			previewPanelEl!.style.maxHeight = available + 'px';
		};
		window.addEventListener('scroll', update, { passive: true });
		window.addEventListener('resize', update, { passive: true });
		update();
		return () => { window.removeEventListener('scroll', update); window.removeEventListener('resize', update); };
	});

	function togglePreview() {
		showPreview = !showPreview;
	}


</script>

<div class="layout" bind:this={layoutEl} style:padding-bottom="{reviewPanelHeight + 16}px" style:--review-h="{reviewPanelHeight + 16}px">
	<header>
		<h1>Bar Prompt Builder</h1>
		<p class="subtitle">Token composition for structured prompts</p>
	</header>

	{#if !releaseNoteDismissed}
		<div class="release-note-banner">
			<div class="release-note-content">
				<strong>Token change:</strong> The <code>gate</code> token has been split.
				<code>gate</code> is now a general hard-blocking checkpoint;
				<code>falsify</code> is the new token for TDD artifact quality (artifact must fire against the minimal wrong state before implementation).
				The <strong>craft</strong> preset and TDD enforcement now use <code>ground gate falsify atomic</code> — update any saved commands that used <code>ground gate chain atomic</code> or <code>ground gate atomic</code>.
			</div>
			<button class="release-note-dismiss" onclick={dismissReleaseNote} aria-label="Dismiss">✕</button>
		</div>
	{/if}

	<!-- Mode switcher — always visible in both build and sequences modes -->
	<div class="mode-switcher">
		<button class="mode-btn" class:mode-btn--active={activeMode === 'build'} onclick={() => activeMode = 'build'}>Build Prompt</button>
		<button class="mode-btn" class:mode-btn--active={activeMode === 'sequences'} onclick={() => activeMode = 'sequences'}>Sequences</button>
	</div>

	{#if error}
		<div class="error">Failed to load grammar: {error}</div>
	{:else if activeMode === 'sequences'}
		{#if $grammarStore}<SequencesPanel grammar={$grammarStore} />{/if}
	{:else if !$grammarStore}
		<div class="loading">Loading grammar…</div>
	{:else}
		<div class="main">
			<SelectorPanel
				bind:this={selectorPanelEl}
				{patterns}
				{starterPacks}
				{suggestionScores}
				{embedder}
				{activeMode}
				onClear={clearState}
				onModeChange={(m) => activeMode = m}
			/>

		<PreviewPanel
				{command}
				subject={$subject}
				addendum={$addendum}
				{promptText}
				{showPreview}
				{copied}
				{copiedPrompt}
				{shared}
				{linkCopied}
				{savedPresets}
				{presetNameInput}
				{presetSaved}
				{historyEntries}
				onTogglePreview={togglePreview}
				onCopyCommand={copyCommand}
				onCopyPrompt={copyPrompt}
				onSharePrompt={sharePromptNative}
				onShareLink={shareLink}
				onCopyLink={copyLink}
				onClear={clearState}
				onSavePreset={handleSavePreset}
				onLoadPreset={handleLoadPreset}
				onDeletePreset={handleDeletePreset}
				onLoadHistory={(hash) => deserialize(hash)}
				onDeleteHistory={(ts) => { deleteHistoryEntry(localStorage, ts); refreshHistory(); }}
				onClearHistory={() => { clearHistory(localStorage); refreshHistory(); }}
				onNameInput={(v) => presetNameInput = v}
			/>
		</div>
	{/if}

	{#if activeMode === 'build'}
	<!-- ADR-0157: Selected Token Review Panel - fixed bottom bar -->
	<ReviewPanel
		selected={$selected}
		persona={$persona}
		conflicts={$conflictsStore}
		{hasSelectedTokens}
		bind:panelHeight={reviewPanelHeight}
		onToggle={(axis, token) => toggle(axis, token)}
		onClearPersonaField={(field) => {
			if (field === 'preset') $persona = { preset: '', voice: '', audience: '', tone: '', intent: $persona.intent };
			else if (field === 'voice') $persona = { ...$persona, preset: '', voice: '' };
			else if (field === 'audience') $persona = { ...$persona, preset: '', audience: '' };
			else if (field === 'tone') $persona = { ...$persona, preset: '', tone: '' };
			else if (field === 'intent') $persona = { ...$persona, intent: '' };
		}}
	/>
	{/if}

	<!-- FAB and mobile action overlay — always accessible, outside preview panel -->
	<button class="fab-btn" onclick={() => { if (Date.now() - (selectorPanelEl?.getSwipeCompletedAt() ?? 0) >= 600) fabOpen = !fabOpen; }} aria-label="Actions">
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
		<button class="copy-link-btn" onclick={copyLink}>
			{linkCopied ? '✓ Link copied' : 'Copy link'}
		</button>
		<button class="clear-btn" onclick={clearState} title="Clear all (⌘K)">Clear</button>
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

	.release-note-banner {
		display: flex;
		align-items: flex-start;
		gap: 0.75rem;
		background: color-mix(in srgb, var(--color-accent) 12%, var(--color-bg));
		border: 1px solid color-mix(in srgb, var(--color-accent) 40%, transparent);
		border-radius: 6px;
		padding: 0.65rem 0.85rem;
		margin-bottom: 1.25rem;
		font-size: 0.82rem;
		line-height: 1.5;
	}
	.release-note-content { flex: 1; color: var(--color-text); }
	.release-note-content code {
		font-family: monospace;
		background: color-mix(in srgb, var(--color-accent) 18%, var(--color-bg));
		padding: 0.1em 0.3em;
		border-radius: 3px;
		font-size: 0.95em;
	}
	.release-note-dismiss {
		background: none;
		border: none;
		cursor: pointer;
		color: var(--color-text-muted);
		font-size: 0.85rem;
		padding: 0;
		line-height: 1;
		flex-shrink: 0;
	}
	.release-note-dismiss:hover { color: var(--color-text); }

	.main {
		display: grid;
		grid-template-columns: 1fr 340px;
		gap: 1.5rem;
		align-items: start;
		overflow-x: hidden; /* prevent horizontal scroll during swipe slide-out */
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

	.copy-btn, .copy-prompt-btn, .share-prompt-btn, .share-link-btn, .copy-link-btn, .clear-btn {
		padding: 0.3rem 0.75rem;
		background: var(--color-accent-muted);
		border: 1px solid var(--color-accent);
		border-radius: var(--radius);
		color: var(--color-text);
		cursor: pointer;
		font-size: 0.8rem;
	}

	.copy-btn:hover, .copy-prompt-btn:hover, .share-prompt-btn:hover, .share-link-btn:hover, .copy-link-btn:hover { background: var(--color-accent); }

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

	@media (max-width: 767px) {
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

		.copy-btn, .copy-prompt-btn, .share-prompt-btn, .share-link-btn, .copy-link-btn, .clear-btn {
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
