<script lang="ts">
	import { onMount } from 'svelte';
	import { loadGrammar, getAxisTokens, getTaskTokens, getPersonaPresets, getPersonaAxisTokens, toPersonaSlug, AXES, type Grammar, type GrammarPattern, getUsagePatterns } from '$lib/grammar.js';
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

	let selected = $state<Record<string, string[]>>({
		task: [],
		completeness: [],
		scope: [],
		method: [],
		form: [],
		channel: [],
		directional: []
	});

	let persona = $state<PersonaState>({ preset: '', voice: '', audience: '', tone: '' });

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
			if (grammar) patterns = getUsagePatterns(grammar);
		} catch (e) {
			error = String(e);
		}

		function handleGlobalKey(e: KeyboardEvent) {
			if (e.key === 'k' && (e.ctrlKey || e.metaKey)) {
				e.preventDefault();
				clearState();
				(document.activeElement as HTMLElement | null)?.blur();
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
			}
		}
	}

	let conflicts = $derived(grammar ? findConflicts(grammar, selected) : []);

	let command = $derived.by(() => {
		if (!grammar) return '';
		const personaTokens: string[] = [];
		if (persona.preset) {
			personaTokens.push(`persona=${persona.preset}`);
		} else {
			if (persona.voice) personaTokens.push(`voice=${toPersonaSlug(persona.voice)}`);
			if (persona.audience) personaTokens.push(`audience=${toPersonaSlug(persona.audience)}`);
			if (persona.tone) personaTokens.push(`tone=${persona.tone}`);
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
		persona = { preset: '', voice: '', audience: '', tone: '' };
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

	function loadCommand() {
		if (!grammar || !cmdInput.trim()) return;
		const result = parseCommand(cmdInput, grammar);
		selected = { task: [], completeness: [], scope: [], method: [], form: [], channel: [], directional: [], ...result.selected };
		if (result.subject) subject = result.subject;
		if (result.addendum) addendum = result.addendum;
		if (result.persona.preset || result.persona.voice || result.persona.audience || result.persona.tone) {
			persona = result.persona;
		}
		cmdInputWarnings = result.unrecognized;
		if (result.unrecognized.length === 0) {
			cmdInput = '';
			cmdInputOpen = false;
		}
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
				<!-- Load command input (collapsible) -->
				<div class="load-cmd-section">
					<!-- svelte-ignore a11y_click_events_have_key_events -->
					<!-- svelte-ignore a11y_no_static_element_interactions -->
					<div class="load-cmd-toggle" onclick={() => { cmdInputOpen = !cmdInputOpen; cmdInputWarnings = []; }}>
						<span class="load-cmd-toggle-label">Load command</span>
						<span class="load-cmd-caret">{cmdInputOpen ? '▲' : '▼'}</span>
					</div>
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

				<PatternsLibrary {patterns} onLoad={loadPattern} />

				<!-- Persona -->
				<div class="persona-section">
					<div class="persona-header">Persona</div>

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
											persona = { preset: '', voice: '', audience: '', tone: '' };
										} else {
											persona = { preset: preset.key, voice: '', audience: '', tone: '' };
										}
									}}
								>{preset.label}</button>
							{/each}
						</div>
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
									onchange={(e) => { persona = { preset: '', voice: (e.target as HTMLSelectElement).value, audience: persona.audience, tone: persona.tone }; }}
								>
									<option value="">—</option>
									{#each getPersonaAxisTokens(grammar, 'voice') as v (v)}
										<option value={v}>{v}</option>
									{/each}
								</select>
							</label>
							<label class="persona-select-label">
								<span>Audience</span>
								<select
									class="persona-select"
									value={persona.audience}
									onchange={(e) => { persona = { preset: '', voice: persona.voice, audience: (e.target as HTMLSelectElement).value, tone: persona.tone }; }}
								>
									<option value="">—</option>
									{#each getPersonaAxisTokens(grammar, 'audience') as a (a)}
										<option value={a}>{a}</option>
									{/each}
								</select>
							</label>
							<label class="persona-select-label">
								<span>Tone</span>
								<select
									class="persona-select"
									value={persona.tone}
									onchange={(e) => { persona = { preset: '', voice: persona.voice, audience: persona.audience, tone: (e.target as HTMLSelectElement).value }; }}
								>
									<option value="">—</option>
									{#each getPersonaAxisTokens(grammar, 'tone') as t (t)}
										<option value={t}>{t}</option>
									{/each}
								</select>
							</label>
						</div>
					</div>
				</div>

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
							{copied ? '✓ Copied' : 'Copy cmd'}
						</button>
						<button class="copy-prompt-btn" onclick={copyPrompt}>
							{copiedPrompt ? '✓ Copied' : 'Copy prompt'}
						</button>
						<button class="share-btn" onclick={sharePrompt}>
							{shared ? '✓ Link copied' : 'Share'}
						</button>
						<button class="clear-btn" onclick={clearState} title="Clear all (⌘K / Ctrl+K)">Clear</button>
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

	.copy-btn, .copy-prompt-btn, .share-btn, .clear-btn {
		padding: 0.3rem 0.75rem;
		background: var(--color-accent-muted);
		border: 1px solid var(--color-accent);
		border-radius: var(--radius);
		color: var(--color-text);
		cursor: pointer;
		font-size: 0.8rem;
	}

	.copy-btn:hover, .copy-prompt-btn:hover, .share-btn:hover { background: var(--color-accent); }

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
</style>
