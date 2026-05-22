// Lazy-loading embedder using @huggingface/transformers (all-MiniLM-L6-v2).
// The pipeline is initialised once on first call; subsequent calls reuse it.
// Returns null on any error so callers can degrade to BM25-only.

const MODEL = 'Xenova/all-MiniLM-L6-v2';

type PipelineFn = (text: string) => Promise<{ data: Float32Array }>;

export interface EmbedderOptions {
	// Inject a pipeline function for testing; omit to use transformers.js.
	pipeline?: PipelineFn;
}

// createEmbedder returns an async function that embeds a query string into a
// unit-normalised 384-dim Float32Array, or null if the model is unavailable.
export function createEmbedder(opts: EmbedderOptions = {}): (q: string) => Promise<Float32Array | null> {
	let pipelinePromise: Promise<PipelineFn> | null = null;

	function getPipeline(): Promise<PipelineFn> {
		if (pipelinePromise) return pipelinePromise;
		if (opts.pipeline) {
			pipelinePromise = Promise.resolve(opts.pipeline);
			return pipelinePromise;
		}
		pipelinePromise = import('@huggingface/transformers').then(({ pipeline, env }) => {
			env.allowLocalModels = false;
			return pipeline('feature-extraction', MODEL, { dtype: 'q8' }) as Promise<PipelineFn>;
		}).catch(() => {
			pipelinePromise = null;
			throw new Error('transformers pipeline init failed');
		});
		return pipelinePromise;
	}

	return async (query: string): Promise<Float32Array | null> => {
		try {
			const pipe = await getPipeline();
			const output = await pipe(query);
			const vec = output.data;
			// L2-normalise in case model doesn't return unit vectors.
			let norm = 0;
			for (let i = 0; i < vec.length; i++) norm += vec[i] * vec[i];
			norm = Math.sqrt(norm);
			if (norm === 0) return vec;
			const result = new Float32Array(vec.length);
			for (let i = 0; i < vec.length; i++) result[i] = vec[i] / norm;
			return result;
		} catch {
			return null;
		}
	};
}
