// Lazy-loading embedder using @huggingface/transformers (all-MiniLM-L6-v2).
// The pipeline is initialised once on first call; subsequent calls reuse it.
// Returns null on any error so callers can degrade to BM25-only.

const MODEL = 'Xenova/all-MiniLM-L6-v2';

// Pipeline call signature with mean-pooling + normalisation options.
type PipelineFn = (text: string, opts: { pooling: string; normalize: boolean }) => Promise<{ data: Float32Array }>;

export interface EmbedderOptions {
	// Inject a pipeline function for testing; omit to use transformers.js.
	pipeline?: (text: string) => Promise<Float32Array>;
}

// createEmbedder returns an async function that embeds a query string into a
// unit-normalised 384-dim Float32Array, or null if the model is unavailable.
export function createEmbedder(opts: EmbedderOptions = {}): (q: string) => Promise<Float32Array | null> {
	let pipelinePromise: Promise<PipelineFn> | null = null;

	function getPipeline(): Promise<PipelineFn> {
		if (pipelinePromise) return pipelinePromise;
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
			if (opts.pipeline) {
				return await opts.pipeline(query);
			}
			const pipe = await getPipeline();
			// pooling:'mean' averages over the sequence dimension → fixed 384-dim vector.
			// normalize:true returns unit vectors so no manual L2-norm needed.
			const output = await pipe(query, { pooling: 'mean', normalize: true });
			return output.data;
		} catch {
			return null;
		}
	};
}
