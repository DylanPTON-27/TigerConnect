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
			'/login': 'http://localhost:8000',
			'/logoutapp': 'http://localhost:8000',
			'/api': 'http://localhost:8000',
			'/friends': 'http://localhost:8000',
			'/calendar': 'http://localhost:8000',
		},
	},
	build: {
    rolldownOptions: {
      input: {
        index: resolve(import.meta.dirname, 'index.html'),
        app: resolve(import.meta.dirname, 'app.html'),
      },
    },
  },
});
