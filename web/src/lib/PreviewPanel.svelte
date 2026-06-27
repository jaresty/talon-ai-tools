<script lang="ts">
	import type { SpaPreset } from '$lib/presets.js';
	import type { HistoryEntry } from '$lib/history.js';
	import PresetsPanel from '$lib/PresetsPanel.svelte';
	import HistoryPanel from '$lib/HistoryPanel.svelte';
	import LLMPanel from '$lib/LLMPanel.svelte';

	let {
		command,
		subject,
		addendum,
		promptText,
		showPreview,
		copied,
		copiedPrompt,
		shared,
		linkCopied,
		savedPresets,
		presetNameInput,
		presetSaved,
		historyEntries,
		onTogglePreview,
		onCopyCommand,
		onCopyPrompt,
		onSharePrompt,
		onShareLink,
		onCopyLink,
		onClear,
		onSavePreset,
		onLoadPreset,
		onDeletePreset,
		onLoadHistory,
		onDeleteHistory,
		onClearHistory,
		onNameInput
	}: {
		command: string;
		subject: string;
		addendum: string;
		promptText: string;
		showPreview: boolean;
		copied: boolean;
		copiedPrompt: boolean;
		shared: boolean;
		linkCopied: boolean;
		savedPresets: SpaPreset[];
		presetNameInput: string;
		presetSaved: boolean;
		historyEntries: HistoryEntry[];
		onTogglePreview: () => void;
		onCopyCommand: () => void;
		onCopyPrompt: () => void;
		onSharePrompt: () => void;
		onShareLink: () => void;
		onCopyLink: () => void;
		onClear: () => void;
		onSavePreset: () => void;
		onLoadPreset: (preset: SpaPreset) => void;
		onDeletePreset: (name: string) => void;
		onLoadHistory: (hash: string) => void;
		onDeleteHistory: (ts: string) => void;
		onClearHistory: () => void;
		onNameInput: (value: string) => void;
	} = $props();
</script>

<button class="preview-toggle" onclick={onTogglePreview}>
	{showPreview ? 'Hide Output' : 'Show Output'}
</button>

<section class="preview-panel" class:visible={showPreview}>
	<div class="command-box">
		<div class="command-label">Command</div>
		<code class="command">{command}</code>
		<div class="action-row">
			<button class="copy-btn" onclick={onCopyCommand}>{copied ? '✓ Copied' : 'Copy cmd'}</button>
			<button class="copy-prompt-btn" onclick={onCopyPrompt}>{copiedPrompt ? '✓ Copied' : 'Copy prompt'}</button>
			<button class="share-prompt-btn" onclick={onSharePrompt}>Share prompt</button>
			<button class="share-link-btn" onclick={onShareLink}>{shared ? '✓ Link copied' : 'Share link'}</button>
			<button class="copy-link-btn" onclick={onCopyLink} title="Copy link (⌘⇧L / Ctrl+Shift+L)">{linkCopied ? '✓ Link copied' : 'Copy link'}</button>
			<button class="clear-btn" onclick={onClear}>Clear</button>
		</div>
	</div>

	<PresetsPanel
		{savedPresets}
		{presetNameInput}
		{presetSaved}
		onSave={onSavePreset}
		onLoad={onLoadPreset}
		onDelete={onDeletePreset}
		{onNameInput}
	/>

	<HistoryPanel
		{historyEntries}
		onLoad={onLoadHistory}
		onDelete={onDeleteHistory}
		onClearAll={onClearHistory}
	/>

	<details class="prompt-preview-section">
		<summary class="prompt-preview-label">Rendered Prompt</summary>
		<pre class="prompt-preview">{promptText}</pre>
	</details>

	<LLMPanel {command} {subject} {addendum} />
</section>

<style>
	.preview-panel {
		position: sticky;
		top: 1rem;
		overflow-y: auto;
		scrollbar-width: thin;
		scrollbar-color: var(--color-border) transparent;
	}

	.preview-panel::-webkit-scrollbar { width: 4px; }
	.preview-panel::-webkit-scrollbar-track { background: transparent; }
	.preview-panel::-webkit-scrollbar-thumb { background: var(--color-border); border-radius: 2px; }
	.preview-panel::-webkit-scrollbar-thumb:hover { background: var(--color-accent-muted); }

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

	.copy-prompt-btn { border-color: var(--color-success); color: var(--color-success); }
	.copy-prompt-btn:hover { background: var(--color-success); color: var(--color-bg); }

	.clear-btn { background: transparent; border-color: var(--color-border); color: var(--color-text-muted); }
	.clear-btn:hover { border-color: #f7768e; color: #f7768e; }

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

	@media (max-width: 767px) {
		.preview-toggle { display: block; }
		.preview-panel { position: static; display: none; }
		.preview-panel.visible { display: block; }
		.command-box .action-row { display: none; }

		.copy-btn, .copy-prompt-btn, .share-prompt-btn, .share-link-btn, .copy-link-btn, .clear-btn {
			min-height: 44px;
		}
	}
</style>
