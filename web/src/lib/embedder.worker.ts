// Web Worker for transformer pipeline — keeps model init and inference off the main thread.

const MODEL = 'Xenova/all-MiniLM-L6-v2';

type PipelineFn = (text: string, opts: { pooling: string; normalize: boolean }) => Promise<{ data: Float32Array }>;

let pipelinePromise: Promise<PipelineFn> | null = null;

function getPipeline(): Promise<PipelineFn> {
	if (pipelinePromise) return pipelinePromise;
	pipelinePromise = import('@huggingface/transformers').then(({ pipeline, env }) => {
		env.allowLocalModels = false;
		return pipeline('feature-extraction', MODEL, { dtype: 'q8' }) as Promise<PipelineFn>;
	}).catch((e) => {
		pipelinePromise = null;
		throw e;
	});
	return pipelinePromise;
}

self.onmessage = async (e: MessageEvent<{ id: number; text: string }>) => {
	const { id, text } = e.data;
	try {
		const pipe = await getPipeline();
		const output = await pipe(text, { pooling: 'mean', normalize: true });
		self.postMessage({ id, result: Array.from(output.data) });
	} catch {
		self.postMessage({ id, error: true });
	}
};
