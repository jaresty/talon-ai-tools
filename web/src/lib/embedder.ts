// Lazy-loading embedder that delegates to a Web Worker so model init and
// inference never block the main thread.
// Returns null on any error so callers can degrade to BM25-only.

export interface EmbedderOptions {
	// Inject a pipeline function for testing; omit to use the worker.
	pipeline?: (text: string) => Promise<Float32Array>;
}

// createEmbedder returns an async function that embeds a query string into a
// unit-normalised 384-dim Float32Array, or null if the model is unavailable.
export function createEmbedder(opts: EmbedderOptions = {}): (q: string) => Promise<Float32Array | null> {
	if (opts.pipeline) {
		const pipe = opts.pipeline;
		return async (query: string): Promise<Float32Array | null> => {
			try { return await pipe(query); } catch { return null; }
		};
	}

	let nextId = 0;
	const pending = new Map<number, { resolve: (v: Float32Array | null) => void }>();
	let worker: Worker | null = null;

	function getWorker(): Worker {
		if (worker) return worker;
		worker = new Worker(new URL('./embedder.worker.ts', import.meta.url), { type: 'module' });
		worker.onmessage = (e: MessageEvent<{ id: number; result?: number[]; error?: boolean }>) => {
			const { id, result, error } = e.data;
			const p = pending.get(id);
			if (!p) return;
			pending.delete(id);
			p.resolve(error || !result ? null : new Float32Array(result));
		};
		return worker;
	}

	return (query: string): Promise<Float32Array | null> => {
		return new Promise((resolve) => {
			try {
				const w = getWorker();
				const id = nextId++;
				pending.set(id, { resolve });
				w.postMessage({ id, text: query });
			} catch {
				resolve(null);
			}
		});
	};
}
