import adapter from '@sveltejs/adapter-static';
import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
	plugins: [
		sveltekit({
			compilerOptions: {
				// Force runes mode for the project, except for libraries. Can be removed in svelte 6.
				runes: ({ filename }) =>
					filename.split(/[/\\]/).includes('node_modules') ? undefined : true
			},
			// статика, которую раздаёт FastAPI (app/main.py)
			adapter: adapter()
		})
	],
	server: {
		// в dev-режиме API — это uvicorn на :8000
		proxy: { '/api': 'http://localhost:8000' }
	}
});
