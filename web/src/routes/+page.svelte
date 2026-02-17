<script lang="ts">
	import { onMount } from 'svelte';
	import { loadGrammar, getAxisTokens, getTaskTokens, AXES, type Grammar } from '$lib/grammar.js';
	import { findConflicts } from '$lib/incompatibilities.js';
	import TokenSelector from '$lib/TokenSelector.svelte';
	import LLMPanel from '$lib/LLMPanel.svelte';
	import PatternsLibrary from '$lib/PatternsLibrary.svelte';

	const STORAGE_KEY = 'bar-prompt-state';

	let grammar: Grammar | null = $state(null);
	let error: string | null = $state(null);

	let selected = $state<Record<string, string[]>>({
		task: [],
		completeness: [],
		scope: [],
		method: [],
		form: [],
		channel: [],
		directional: []
	});

	let subject = $state('');
	let addendum = $state('');
	let copied = $state(false);
	let shared = $state(false);

	// Serialize/deserialize prompt state
	function serialize(): string {
		return btoa(JSON.stringify({ selected, subject, addendum }));
	}

	function deserialize(raw: string): void {
		try {
			const parsed = JSON.parse(atob(raw));
			if (parsed && typeof parsed === 'object') {
				if (parsed.selected) selected = { ...selected, ...parsed.selected };
				if (typeof parsed.subject === 'string') subject = parsed.subject;
				if (typeof parsed.addendum === 'string') addendum = parsed.addendum;
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
		} catch (e) {
			error = String(e);
		}
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
			}
		}
	}

	let conflicts = $derived(grammar ? findConflicts(grammar, selected) : []);

	let command = $derived.by(() => {
		if (!grammar) return '';
		const order = ['task', 'completeness', 'scope', 'method', 'form', 'channel', 'directional'];
		const tokens = order.flatMap((axis) => selected[axis] ?? []);
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

	function sharePrompt() {
		const encoded = serialize();
		const url = `${window.location.origin}${window.location.pathname}#${encoded}`;
		window.history.replaceState(null, '', `#${encoded}`);
		navigator.clipboard.writeText(url);
		shared = true;
		setTimeout(() => (shared = false), 1500);
	}

	function clearState() {
		selected = { task: [], completeness: [], scope: [], method: [], form: [], channel: [], directional: [] };
		subject = '';
		addendum = '';
		window.history.replaceState(null, '', window.location.pathname);
		localStorage.removeItem(STORAGE_KEY);
	}

	function loadPattern(pattern: { tokens: Record<string, string[]>; subject?: string; addendum?: string }) {
		selected = { task: [], completeness: [], scope: [], method: [], form: [], channel: [], directional: [], ...pattern.tokens };
		if (pattern.subject !== undefined) subject = pattern.subject;
		if (pattern.addendum !== undefined) addendum = pattern.addendum;
	}
</script>

<div class="layout">
	<header>
		<h1>Bar Prompt Builder</h1>
		<p class="subtitle">Token composition for structured prompts</p>
	</header>

	{#if error}
		<div class="error">Failed to load grammar: {error}</div>
	{:else if !grammar}
		<div class="loading">Loading grammar…</div>
	{:else}
		<div class="main">
			<section class="selector-panel">
				<PatternsLibrary onLoad={loadPattern} />
				<TokenSelector
					axis="task"
					tokens={getTaskTokens(grammar)}
					selected={selected.task}
					maxSelect={1}
					onToggle={(t) => toggle('task', t)}
				/>
				{#each AXES as axis (axis)}
					<TokenSelector
						{axis}
						tokens={getAxisTokens(grammar, axis)}
						selected={selected[axis] ?? []}
						maxSelect={softCap(axis)}
						onToggle={(t) => toggle(axis, t)}
					/>
				{/each}
			</section>

			<section class="preview-panel">
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
					<div class="action-row">
						<button class="copy-btn" onclick={copyCommand}>
							{copied ? '✓ Copied' : 'Copy'}
						</button>
						<button class="share-btn" onclick={sharePrompt}>
							{shared ? '✓ Link copied' : 'Share'}
						</button>
						<button class="clear-btn" onclick={clearState}>Clear</button>
					</div>
				</div>

				<!-- Subject / addendum inputs -->
				<div class="inputs">
					<label class="input-group">
						<span class="input-label">--subject <span class="input-hint">source material</span></span>
						<textarea
							class="input-area"
							rows="3"
							placeholder="Paste code, document, or topic…"
							bind:value={subject}
						></textarea>
					</label>

					<label class="input-group">
						<span class="input-label">--addendum <span class="input-hint">task directive</span></span>
						<textarea
							class="input-area"
							rows="2"
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
								<span class="selected-chip" onclick={() => toggle(axis, token)}>
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
</div>

<style>
	.layout {
		max-width: 1200px;
		margin: 0 auto;
		padding: 1.5rem;
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
	}

	.preview-panel {
		position: sticky;
		top: 1rem;
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

	.copy-btn, .share-btn, .clear-btn {
		padding: 0.3rem 0.75rem;
		background: var(--color-accent-muted);
		border: 1px solid var(--color-accent);
		border-radius: var(--radius);
		color: var(--color-text);
		cursor: pointer;
		font-size: 0.8rem;
	}

	.copy-btn:hover, .share-btn:hover { background: var(--color-accent); }

	.clear-btn {
		background: transparent;
		border-color: var(--color-border);
		color: var(--color-text-muted);
	}

	.clear-btn:hover { border-color: #f7768e; color: #f7768e; }

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
</style>
