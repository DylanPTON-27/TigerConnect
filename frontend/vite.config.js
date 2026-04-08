import { defineConfig } from "vite";
import { svelte } from '@sveltejs/vite-plugin-svelte'
import { resolve } from 'path';
import tailwindcss from "@tailwindcss/vite"; 

export default defineConfig({
	plugins: [
		tailwindcss(), 
		svelte()
	],
	server: {
		proxy: {
			'/api': 'http://localhost:8000',
			'/friends': 'http://localhost:8000',
			'/calendar': 'http://localhost:8000',
		},
	},
	build: {
    rolldownOptions: {
      input: {
        main: resolve(import.meta.dirname, 'index.html'),
        landing: resolve(import.meta.dirname, 'landing.html'),
      },
    },
  },
});
