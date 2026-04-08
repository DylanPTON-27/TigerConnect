<script>
	// @ts-ignore
	import { Menu } from "@lucide/svelte";
	import { AppBar } from "@skeletonlabs/skeleton-svelte";
	import { sidebarState } from "./sharedVars.svelte.js";
	import Notifications from "./Notifications.svelte";
	import Switch from "./Switch.svelte";

	const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
</script>

<AppBar class="bg-zinc-400 dark:bg-zinc-900 flex justify-center">
	<AppBar.Toolbar class="grid grid-cols-3 items-center">
		<AppBar.Lead class="flex items-center">
			<button
				type="button"
				class="btn hover:preset-tonal"
				onclick={() => sidebarState.toggleSidebar()}
			>
				<Menu class="size-6" />
			</button>
		</AppBar.Lead>
		<AppBar.Headline class="justify-self-center">
			<a href="/app.html">
				<button type="button" class="Title">TigerConnect</button>
			</a>
		</AppBar.Headline>
		<AppBar.Trail class="justify-self-end">
			<Switch />
			<Notifications />
			<a href={`${API_BASE}/logoutapp`}>
				<button type="button" class="btn hover:preset-tonal">Log Out</button>
			</a>
		</AppBar.Trail>
	</AppBar.Toolbar>
</AppBar>

<style>
	@import "tailwindcss";
	@custom-variant dark (&:where([data-mode=dark], [data-mode=dark] *));

	button {
		border-radius: 8px;
		margin-right: 5px;
		margin-left: 5px;
		padding: 0.8em 1em;
		font-size: 1em;
		font-weight: 500;
		font-family: inherit;
		cursor: pointer;
		transition: border-color 0.25s;
		@apply bg-black dark:bg-white;
		@apply text-white dark:text-black;
	}
	button:focus,
	button:focus-visible {
		outline: 4px auto -webkit-focus-ring-color;
	}

	.Title {
		font-size: 2em;
		font-weight: 700;
		padding: 0em 1em;
		@apply bg-transparent;
		@apply text-black dark:text-white;
	}
</style>
