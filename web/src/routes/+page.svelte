<script lang="ts">
	import { onMount } from 'svelte';
	import { loadGrammar, getAxisTokens, getTaskTokens, AXES, type Grammar } from '$lib/grammar.js';
	import TokenSelector from '$lib/TokenSelector.svelte';

	let grammar: Grammar | null = $state(null);
	let error: string | null = $state(null);

	// Selected tokens per axis
	let selected = $state<Record<string, string[]>>({
		task: [],
		completeness: [],
		scope: [],
		method: [],
		form: [],
		channel: [],
		directional: []
	});

	onMount(async () => {
		try {
			grammar = await loadGrammar();
		} catch (e) {
			error = String(e);
		}
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

	// Build bar command from selections
	let command = $derived.by(() => {
		if (!grammar) return '';
		const order = ['task', 'completeness', 'scope', 'method', 'form', 'channel', 'directional'];
		const tokens = order.flatMap((axis) => selected[axis] ?? []);
		if (tokens.length === 0) return 'bar build';
		return `bar build ${tokens.join(' ')}`;
	});
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
				<!-- Task axis -->
				<TokenSelector
					axis="task"
					tokens={getTaskTokens(grammar)}
					selected={selected.task}
					maxSelect={1}
					onToggle={(t) => toggle('task', t)}
				/>

				<!-- Contract axes -->
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
				<div class="command-box">
					<div class="command-label">Command</div>
					<code class="command">{command}</code>
					<button
						class="copy-btn"
						onclick={() => navigator.clipboard.writeText(command)}
					>
						Copy
					</button>
				</div>

				<div class="selected-chips">
					{#each Object.entries(selected) as [axis, tokens]}
						{#each tokens as token (token)}
							<span class="selected-chip" onclick={() => toggle(axis, token)}>
								{token} ×
							</span>
						{/each}
					{/each}
				</div>
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

	h1 {
		font-size: 1.4rem;
		color: var(--color-accent);
	}

	.subtitle {
		font-size: 0.85rem;
		color: var(--color-text-muted);
		margin-top: 0.25rem;
	}

	.loading, .error {
		color: var(--color-text-muted);
		padding: 2rem;
		text-align: center;
	}

	.error { color: #f7768e; }

	.main {
		display: grid;
		grid-template-columns: 1fr 320px;
		gap: 1.5rem;
	}

	.selector-panel {
		overflow-y: auto;
	}

	.preview-panel {
		position: sticky;
		top: 1rem;
		align-self: start;
	}

	.command-box {
		background: var(--color-surface);
		border: 1px solid var(--color-border);
		border-radius: var(--radius);
		padding: 1rem;
		margin-bottom: 1rem;
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
		font-size: 0.85rem;
		word-break: break-all;
		margin-bottom: 0.75rem;
		color: var(--color-success);
	}

	.copy-btn {
		padding: 0.3rem 0.75rem;
		background: var(--color-accent-muted);
		border: 1px solid var(--color-accent);
		border-radius: var(--radius);
		color: var(--color-text);
		cursor: pointer;
		font-size: 0.8rem;
	}

	.copy-btn:hover { background: var(--color-accent); }

	.selected-chips {
		display: flex;
		flex-wrap: wrap;
		gap: 0.4rem;
	}

	.selected-chip {
		padding: 0.2rem 0.5rem;
		background: var(--color-accent-muted);
		border: 1px solid var(--color-accent);
		border-radius: var(--radius);
		font-family: var(--font-mono);
		font-size: 0.8rem;
		cursor: pointer;
	}

	.selected-chip:hover { background: #6b3040; border-color: #f7768e; }
</style>
