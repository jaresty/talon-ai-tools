<script lang="ts">
	import type { Grammar, GrammarPattern, StarterPack } from '$lib/grammar.js';
	import { parseCommand } from '$lib/parseCommand.js';

	let {
		patterns,
		starterPacks = [],
		grammar = null,
		onLoad
	}: {
		patterns: GrammarPattern[];
		starterPacks?: StarterPack[];
		grammar?: Grammar | null;
		onLoad: (pattern: GrammarPattern) => void;
	} = $props();

	let expanded = $state(false);
	let startersExpanded = $state(false);

	function loadStarter(pack: StarterPack) {
		if (!grammar) return;
		const parsed = parseCommand(pack.command, grammar);
		onLoad({ title: pack.name, command: pack.command, example: pack.command, desc: pack.framing, tokens: parsed.selected });
	}
</script>

{#if starterPacks.length > 0}
<div class="patterns starters">
	<button class="patterns-toggle" onclick={() => (startersExpanded = !startersExpanded)}>
		{startersExpanded ? '▾' : '▸'} Starter Packs
	</button>

	{#if startersExpanded}
		<div class="patterns-grid">
			{#each starterPacks as pack (pack.name)}
				<button class="pattern-card" onclick={() => loadStarter(pack)}>
					<div class="pattern-name"><code>{pack.name}</code></div>
					<div class="pattern-desc">{pack.framing}</div>
					<div class="pattern-cmd"><code>{pack.command}</code></div>
				</button>
			{/each}
		</div>
	{/if}
</div>
{/if}

<div class="patterns">
	<button class="patterns-toggle" onclick={() => (expanded = !expanded)}>
		{expanded ? '▾' : '▸'} Usage Patterns
	</button>

	{#if expanded}
		<div class="patterns-grid">
			{#each patterns as pattern (pattern.title)}
				<button class="pattern-card" onclick={() => onLoad(pattern)}>
					<div class="pattern-name">{pattern.title}</div>
					<div class="pattern-desc">{pattern.desc}</div>
					<div class="pattern-tokens">
						{#each Object.values(pattern.tokens).flat() as token (token)}
							<span class="pattern-chip">{token}</span>
						{/each}
					</div>
				</button>
			{/each}
		</div>
	{/if}
</div>

<style>
	.patterns { margin-bottom: 1rem; }

	.patterns-toggle {
		width: 100%;
		text-align: left;
		padding: 0.5rem 0.75rem;
		background: var(--color-surface);
		border: 1px solid var(--color-border);
		border-radius: var(--radius);
		color: var(--color-text-muted);
		cursor: pointer;
		font-size: 0.8rem;
		display: flex;
		align-items: center;
		gap: 0.4rem;
	}

	.patterns-toggle:hover { border-color: var(--color-accent-muted); color: var(--color-text); }

	.patterns-grid {
		margin-top: 0.5rem;
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 0.5rem;
	}

	.pattern-card {
		text-align: left;
		padding: 0.6rem 0.75rem;
		background: var(--color-bg);
		border: 1px solid var(--color-border);
		border-radius: var(--radius);
		cursor: pointer;
		transition: border-color 0.1s;
	}

	.pattern-card:hover { border-color: var(--color-accent); }

	.pattern-name {
		font-size: 0.8rem;
		font-weight: 600;
		color: var(--color-text);
		margin-bottom: 0.2rem;
	}

	.pattern-desc {
		font-size: 0.72rem;
		color: var(--color-text-muted);
		line-height: 1.4;
		margin-bottom: 0.4rem;
	}

	.pattern-tokens { display: flex; flex-wrap: wrap; gap: 0.25rem; }

	.pattern-chip {
		padding: 0.1rem 0.35rem;
		background: var(--color-accent-muted);
		border: 1px solid var(--color-border);
		border-radius: 3px;
		font-family: var(--font-mono);
		font-size: 0.7rem;
		color: var(--color-text-muted);
	}

	.pattern-cmd {
		font-size: 0.68rem;
		color: var(--color-text-muted);
		margin-top: 0.2rem;
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}

	.starters .patterns-toggle {
		border-color: var(--color-accent-muted);
	}
</style>
