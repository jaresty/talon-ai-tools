<script lang="ts">
	interface Pattern {
		name: string;
		description: string;
		tokens: Record<string, string[]>;
		subject?: string;
		addendum?: string;
	}

	// Pre-composed usage patterns drawn from real bar token vocabulary
	const usagePatterns: Pattern[] = [
		{
			name: 'Quick Code Review',
			description: 'Skim a diff or PR for obvious issues and style problems',
			tokens: { task: ['check'], completeness: ['skim'], scope: ['struct'], method: ['rigor'], channel: ['code'] }
		},
		{
			name: 'Deep Bug Diagnosis',
			description: 'Thorough root-cause analysis of a failing behaviour',
			tokens: { task: ['fix'], completeness: ['deep'], scope: ['fail'], method: ['diagnose'], channel: ['code'] }
		},
		{
			name: 'Architecture Plan',
			description: 'Full planning pass with structured ADR output',
			tokens: { task: ['plan'], completeness: ['full'], scope: ['struct'], method: ['spec'], channel: ['adr'] }
		},
		{
			name: 'Risk & Trade-off Exploration',
			description: 'Identify risks and alternatives before committing to a design',
			tokens: { task: ['probe'], completeness: ['gist'], scope: ['view'], method: ['risks'], channel: ['plain'] }
		},
		{
			name: 'Diff Summary',
			description: 'Summarise what changed and why in a diff or commit range',
			tokens: { task: ['diff'], completeness: ['gist'], scope: ['act'], method: ['analysis'], channel: ['plain'] }
		},
		{
			name: 'Pull Request Write-up',
			description: 'Draft a detailed PR description from a diff + context',
			tokens: { task: ['pull'], completeness: ['full'], scope: ['struct'], method: ['spec'], channel: ['plain'] }
		},
		{
			name: 'Feature Prioritisation',
			description: 'Score and rank a backlog of ideas or tasks',
			tokens: { task: ['sort'], completeness: ['minimal'], scope: ['thing'], method: ['prioritize'] }
		},
		{
			name: 'Show / Explain',
			description: 'Explain code or a concept concisely for a non-expert audience',
			tokens: { task: ['show'], completeness: ['gist'], scope: ['view'], method: ['analog'] }
		}
	];

	let { onLoad }: { onLoad: (pattern: Pattern) => void } = $props();

	let expanded = $state(false);
</script>

<div class="patterns">
	<button class="patterns-toggle" onclick={() => (expanded = !expanded)}>
		{expanded ? '▾' : '▸'} Usage Patterns
	</button>

	{#if expanded}
		<div class="patterns-grid">
			{#each usagePatterns as pattern (pattern.name)}
				<button class="pattern-card" onclick={() => onLoad(pattern)}>
					<div class="pattern-name">{pattern.name}</div>
					<div class="pattern-desc">{pattern.description}</div>
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
</style>
