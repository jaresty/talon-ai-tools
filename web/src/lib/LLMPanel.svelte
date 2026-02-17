<script lang="ts">
	const LLM_CONFIG_KEY = 'bar-llm-config';

	interface LLMConfig {
		provider: 'anthropic' | 'openai' | 'ollama';
		model: string;
		apiKey: string;
		temperature: number;
	}

	const DEFAULT_MODELS: Record<LLMConfig['provider'], string> = {
		anthropic: 'claude-opus-4-6',
		openai: 'gpt-5',
		ollama: 'llama3.2'
	};

	function loadConfig(): LLMConfig {
		try {
			const saved = localStorage.getItem(LLM_CONFIG_KEY);
			if (saved) return JSON.parse(saved);
		} catch { /* ignore */ }
		return { provider: 'anthropic', model: 'claude-opus-4-6', apiKey: '', temperature: 0.7 };
	}

	function saveConfig(cfg: LLMConfig) {
		localStorage.setItem(LLM_CONFIG_KEY, JSON.stringify(cfg));
	}

	let { command, subject, addendum }: { command: string; subject: string; addendum: string } = $props();

	let config = $state<LLMConfig>(loadConfig());
	let response = $state('');
	let loading = $state(false);
	let errorMsg = $state('');
	let showKey = $state(false);

	$effect(() => {
		saveConfig(config);
	});

	function onProviderChange() {
		config.model = DEFAULT_MODELS[config.provider];
	}

	function buildUserMessage(): string {
		let msg = `Bar command: \`${command}\`\n\n`;
		if (subject.trim()) msg += `Subject:\n${subject.trim()}\n\n`;
		if (addendum.trim()) msg += `Directive:\n${addendum.trim()}\n\n`;
		msg += 'Please respond to the above prompt composition.';
		return msg;
	}

	async function send() {
		if (!config.apiKey.trim() && config.provider !== 'ollama') {
			errorMsg = 'API key required.';
			return;
		}
		errorMsg = '';
		response = '';
		loading = true;
		try {
			if (config.provider === 'anthropic') {
				await sendAnthropic();
			} else if (config.provider === 'openai') {
				await sendOpenAI();
			} else {
				await sendOllama();
			}
		} catch (e) {
			errorMsg = String(e);
		} finally {
			loading = false;
		}
	}

	async function sendAnthropic() {
		const res = await fetch('https://api.anthropic.com/v1/messages', {
			method: 'POST',
			headers: {
				'content-type': 'application/json',
				'x-api-key': config.apiKey,
				'anthropic-version': '2023-06-01',
				'anthropic-dangerous-direct-browser-access': 'true'
			},
			body: JSON.stringify({
				model: config.model,
				max_tokens: 4096,
				temperature: config.temperature,
				messages: [{ role: 'user', content: buildUserMessage() }]
			})
		});
		if (!res.ok) {
			const err = await res.text();
			throw new Error(`Anthropic ${res.status}: ${err}`);
		}
		const data = await res.json();
		response = data.content?.[0]?.text ?? '';
	}

	async function sendOpenAI() {
		const res = await fetch('https://api.openai.com/v1/chat/completions', {
			method: 'POST',
			headers: {
				'content-type': 'application/json',
				'authorization': `Bearer ${config.apiKey}`
			},
			body: JSON.stringify({
				model: config.model,
				temperature: config.temperature,
				messages: [{ role: 'user', content: buildUserMessage() }]
			})
		});
		if (!res.ok) {
			const err = await res.text();
			throw new Error(`OpenAI ${res.status}: ${err}`);
		}
		const data = await res.json();
		response = data.choices?.[0]?.message?.content ?? '';
	}

	async function sendOllama() {
		const res = await fetch('http://localhost:11434/api/generate', {
			method: 'POST',
			headers: { 'content-type': 'application/json' },
			body: JSON.stringify({
				model: config.model,
				prompt: buildUserMessage(),
				stream: false
			})
		});
		if (!res.ok) {
			const err = await res.text();
			throw new Error(`Ollama ${res.status}: ${err}`);
		}
		const data = await res.json();
		response = data.response ?? '';
	}

	let copied = $state(false);
	function copyResponse() {
		navigator.clipboard.writeText(response);
		copied = true;
		setTimeout(() => (copied = false), 1500);
	}
</script>

<div class="llm-panel">
	<div class="llm-header">LLM Integration</div>

	<div class="llm-config">
		<div class="config-row">
			<label class="config-label">Provider</label>
			<select class="config-select" bind:value={config.provider} onchange={onProviderChange}>
				<option value="anthropic">Anthropic</option>
				<option value="openai">OpenAI</option>
				<option value="ollama">Ollama (local)</option>
			</select>
		</div>

		<div class="config-row">
			<label class="config-label">Model</label>
			<input class="config-input" type="text" bind:value={config.model} />
		</div>

		{#if config.provider !== 'ollama'}
			<div class="config-row">
				<label class="config-label">API Key</label>
				<div class="key-row">
					<input
						class="config-input key-input"
						type={showKey ? 'text' : 'password'}
						bind:value={config.apiKey}
						placeholder="sk-…"
					/>
					<button class="toggle-key" onclick={() => (showKey = !showKey)}>
						{showKey ? 'hide' : 'show'}
					</button>
				</div>
			</div>
		{/if}

		<div class="config-row">
			<label class="config-label">Temperature <span class="temp-val">{config.temperature}</span></label>
			<input
				class="config-range"
				type="range"
				min="0" max="1" step="0.05"
				bind:value={config.temperature}
			/>
		</div>
	</div>

	<button class="send-btn" onclick={send} disabled={loading}>
		{loading ? 'Sending…' : 'Send to LLM'}
	</button>

	{#if errorMsg}
		<div class="llm-error">{errorMsg}</div>
	{/if}

	{#if response}
		<div class="response-box">
			<div class="response-header">
				<span>Response</span>
				<button class="copy-response" onclick={copyResponse}>{copied ? '✓' : 'Copy'}</button>
			</div>
			<pre class="response-text">{response}</pre>
		</div>
	{/if}
</div>

<style>
	.llm-panel {
		margin-top: 1rem;
		padding: 1rem;
		background: var(--color-surface);
		border: 1px solid var(--color-border);
		border-radius: var(--radius);
	}

	.llm-header {
		font-size: 0.75rem;
		text-transform: uppercase;
		letter-spacing: 0.05em;
		color: var(--color-text-muted);
		margin-bottom: 0.75rem;
	}

	.llm-config { display: flex; flex-direction: column; gap: 0.5rem; margin-bottom: 0.75rem; }

	.config-row { display: flex; flex-direction: column; gap: 0.2rem; }

	.config-label {
		font-size: 0.72rem;
		color: var(--color-text-muted);
		display: flex;
		align-items: center;
		gap: 0.4rem;
	}

	.temp-val { color: var(--color-accent); font-family: var(--font-mono); }

	.config-select, .config-input {
		width: 100%;
		padding: 0.3rem 0.4rem;
		background: var(--color-bg);
		border: 1px solid var(--color-border);
		border-radius: var(--radius);
		color: var(--color-text);
		font-size: 0.8rem;
	}

	.config-select:focus, .config-input:focus { outline: none; border-color: var(--color-accent-muted); }

	.key-row { display: flex; gap: 0.4rem; }

	.key-input { flex: 1; }

	.toggle-key {
		padding: 0.3rem 0.5rem;
		background: transparent;
		border: 1px solid var(--color-border);
		border-radius: var(--radius);
		color: var(--color-text-muted);
		cursor: pointer;
		font-size: 0.72rem;
		white-space: nowrap;
	}

	.config-range { width: 100%; accent-color: var(--color-accent); }

	.send-btn {
		width: 100%;
		padding: 0.45rem;
		background: var(--color-accent-muted);
		border: 1px solid var(--color-accent);
		border-radius: var(--radius);
		color: var(--color-text);
		cursor: pointer;
		font-size: 0.85rem;
		margin-bottom: 0.5rem;
	}

	.send-btn:hover:not(:disabled) { background: var(--color-accent); }
	.send-btn:disabled { opacity: 0.5; cursor: default; }

	.llm-error {
		color: #f7768e;
		font-size: 0.78rem;
		padding: 0.4rem 0;
		word-break: break-word;
	}

	.response-box {
		margin-top: 0.5rem;
		border: 1px solid var(--color-border);
		border-radius: var(--radius);
		overflow: hidden;
	}

	.response-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 0.3rem 0.6rem;
		background: var(--color-bg);
		border-bottom: 1px solid var(--color-border);
		font-size: 0.72rem;
		color: var(--color-text-muted);
	}

	.copy-response {
		padding: 0.15rem 0.4rem;
		background: var(--color-accent-muted);
		border: 1px solid var(--color-accent);
		border-radius: 3px;
		color: var(--color-text);
		cursor: pointer;
		font-size: 0.7rem;
	}

	.response-text {
		margin: 0;
		padding: 0.6rem;
		font-size: 0.78rem;
		line-height: 1.55;
		white-space: pre-wrap;
		word-break: break-word;
		max-height: 400px;
		overflow-y: auto;
		color: var(--color-text);
	}
</style>
