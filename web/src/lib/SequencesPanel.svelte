<script lang="ts">
	import { getSequences } from '$lib/grammar.js';
	import { buildCopyPrompt } from '$lib/sequenceRenderer.js';
	import type { Grammar } from '$lib/grammar.js';

	let { grammar }: { grammar: Grammar } = $props();

	let seqSubject = $state('');
	let seqCopied = $state(false);
	let seqModalText = $state('');
	let seqExpandedKey = $state<string | null>(null);
</script>

<div class="sequences-panel">
	{#if seqModalText}
		<div class="seq-modal-backdrop" onclick={() => seqModalText = ''}>
			<div class="seq-modal" onclick={(e) => e.stopPropagation()}>
				<p class="seq-modal-hint">Copy the text below:</p>
				<textarea class="seq-modal-textarea" readonly>{seqModalText}</textarea>
				<button onclick={() => seqModalText = ''}>Close</button>
			</div>
		</div>
	{/if}
	<label class="seq-subject-label">
		Subject
		<textarea class="seq-subject-input" rows="3" placeholder="What is this sequence operating on?" bind:value={seqSubject}></textarea>
	</label>
	{#each getSequences(grammar) as seq (seq.key)}
		<div class="seq-card">
			<button class="seq-card-header" onclick={() => seqExpandedKey = seqExpandedKey === seq.key ? null : seq.key}>
				<span class="seq-card-name">{seq.key}</span>
				<span class="seq-card-mode">{seq.mode}</span>
				<span class="seq-card-caret">{seqExpandedKey === seq.key ? '▲' : '▼'}</span>
			</button>
			<p class="seq-card-desc">{seq.description}</p>
			{#if seqExpandedKey === seq.key}
				<ol class="seq-steps">
					{#each seq.steps as step, i}
						<li class="seq-step" class:seq-step-action={step.type === 'action'}>
							{#if step.type === 'action'}
								<span class="seq-step-user-badge">👤 You</span>
							{:else if step.token}
								<code class="seq-step-token">{step.token}</code>
							{/if}
							<span class="seq-step-role">{step.role}</span>
							{#if step.prompt_hint}<p class="seq-step-hint">{step.prompt_hint}</p>{/if}
						</li>
						{#if step.requires_user_input && step.type !== 'action'}
							<li class="seq-pause-indicator" aria-label="Provide your input before continuing to next step">⏸ Provide your input before continuing to the next step</li>
						{/if}
					{/each}
				</ol>
				<button class="seq-copy-btn" onclick={async () => {
					const output = buildCopyPrompt(seq, seqSubject, grammar, seq.key);
					try {
						await navigator.clipboard.writeText(output);
						seqCopied = true;
						setTimeout(() => seqCopied = false, 1500);
					} catch {
						seqModalText = output;
					}
				}}>{seqCopied ? 'Copied!' : 'Copy as Prompt'}</button>
			{/if}
		</div>
	{:else}
		<p class="seq-empty">No sequences available.</p>
	{/each}
</div>

<style>
	.sequences-panel {
		display: flex;
		flex-direction: column;
		gap: 0.75rem;
		padding: 0.5rem 0;
	}

	.seq-subject-label {
		display: flex;
		flex-direction: column;
		gap: 0.25rem;
		font-size: 0.85rem;
		color: var(--color-muted, #aaa);
	}

	.seq-subject-input {
		width: 100%;
		background: var(--color-surface, #1a1a1a);
		border: 1px solid var(--color-border, #444);
		border-radius: 4px;
		color: inherit;
		padding: 0.4rem;
		font-size: 0.9rem;
		resize: vertical;
	}

	.seq-card {
		border: 1px solid var(--color-border, #333);
		border-radius: 6px;
		overflow: hidden;
	}

	.seq-card-header {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		width: 100%;
		padding: 0.5rem 0.75rem;
		background: var(--color-surface, #1e1e1e);
		border: none;
		color: inherit;
		cursor: pointer;
		text-align: left;
	}

	.seq-card-name {
		font-weight: 600;
		font-size: 0.9rem;
		flex: 1;
	}

	.seq-card-mode {
		font-size: 0.75rem;
		color: var(--color-muted, #888);
	}

	.seq-card-caret {
		font-size: 0.7rem;
		color: var(--color-muted, #888);
	}

	.seq-card-desc {
		margin: 0;
		padding: 0.4rem 0.75rem;
		font-size: 0.82rem;
		color: var(--color-muted, #aaa);
	}

	.seq-steps {
		margin: 0;
		padding: 0.5rem 0.75rem 0.5rem 1.5rem;
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}

	.seq-step {
		font-size: 0.82rem;
	}

	.seq-step-token {
		display: inline-block;
		margin-right: 0.4rem;
		padding: 0.1rem 0.3rem;
		background: var(--color-surface, #222);
		border-radius: 3px;
		font-size: 0.78rem;
	}

	.seq-step-role {
		font-weight: 500;
	}

	.seq-step-hint {
		margin: 0.15rem 0 0;
		color: var(--color-muted, #999);
		font-size: 0.78rem;
	}

	.seq-copy-btn {
		margin: 0.5rem 0.75rem 0.75rem;
		padding: 0.4rem 0.9rem;
		background: var(--color-accent, #4a9eff);
		color: #fff;
		border: none;
		border-radius: 5px;
		cursor: pointer;
		font-size: 0.85rem;
	}

	.seq-empty {
		color: var(--color-muted, #888);
		font-size: 0.85rem;
	}

	.seq-modal-backdrop {
		position: fixed;
		inset: 0;
		background: rgba(0,0,0,0.6);
		display: flex;
		align-items: center;
		justify-content: center;
		z-index: 100;
	}

	.seq-modal {
		background: var(--color-surface, #1e1e1e);
		border: 1px solid var(--color-border, #444);
		border-radius: 8px;
		padding: 1rem;
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
		width: min(90vw, 600px);
	}

	.seq-modal-hint {
		margin: 0;
		font-size: 0.85rem;
		color: var(--color-muted, #aaa);
	}

	.seq-modal-textarea {
		width: 100%;
		height: 200px;
		background: var(--color-surface, #111);
		border: 1px solid var(--color-border, #444);
		color: inherit;
		padding: 0.4rem;
	}
</style>
