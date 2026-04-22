<script>
	// @ts-ignore
	import { AppBar } from "@skeletonlabs/skeleton-svelte";
	import Notifications from "./Notifications.svelte";
	import Switch from "./Switch.svelte";

	const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
</script>

<AppBar class="justify-center h-auto bg-transparent">
	<AppBar.Toolbar class="grid grid-cols-3 items-center">
		<AppBar.Lead class="flex items-center">
			<a href="/app.html">
				<div class="Title underglow">TigerConnect</div>
			</a>
		</AppBar.Lead>

		<AppBar.Headline></AppBar.Headline>
		
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
		font-weight: 600;
		font-family: inherit;
		cursor: pointer;
		transition: border-color 0.25s;
		background: #111111;
		color: #ffffff;
		border: 1px solid #111111;
	}
	button:hover {
		background: #ff8f1f;
		border-color: #ff8f1f;
		color: #111111;
	}
	button:focus,
	button:focus-visible {
		outline: 4px auto -webkit-focus-ring-color;
	}

	.Title {
		border-radius: 100px;
		font-size: 2em;
		font-weight: 500;
		letter-spacing: 0.2px;
		color: #111111;
		@apply w-max;
		background-color: transparent;
	}
</style>
