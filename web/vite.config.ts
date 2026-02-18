import { sveltekit } from '@sveltejs/kit/vite';
import { svelte } from '@sveltejs/vite-plugin-svelte';
import { defineConfig } from 'vitest/config';
import { fileURLToPath } from 'node:url';
import { dirname, resolve } from 'node:path';

const __dirname = dirname(fileURLToPath(import.meta.url));
const isTesting = !!process.env.VITEST;

export default defineConfig({
	plugins: [isTesting ? svelte() : sveltekit()],
	resolve: {
		conditions: ['browser', 'import', 'module', 'default'],
		alias: isTesting
			? [
					{ find: '$app/paths', replacement: resolve(__dirname, 'src/mocks/app-paths.ts') },
					{ find: '$lib', replacement: resolve(__dirname, 'src/lib') }
				]
			: []
	},
	test: {
		include: ['src/**/*.{test,spec}.{js,ts}'],
		environment: 'jsdom',
		globals: true
	}
});
