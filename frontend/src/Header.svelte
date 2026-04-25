<script>
	import { AppBar } from "@skeletonlabs/skeleton-svelte";
	import Notifications from "./Notifications.svelte";
	import Switch from "./Switch.svelte";

	const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

	function handleLogout() {
		sessionStorage.removeItem("username");
		sessionStorage.removeItem("accessToken");
		sessionStorage.removeItem("refreshToken");
		sessionStorage.removeItem("displayName");
		window.location.href = `${API_BASE}/logoutapp`;
		return;
	}
</script>

<AppBar class="justify-center h-auto bg-transparent">
	<AppBar.Toolbar class="grid grid-cols-3 items-center">
		<AppBar.Lead class="flex items-center">
			<a href="/app.html">
				<img class="brand-logo" src="/tigerconnect-logo.png" alt="TigerConnect" />
			</a>
		</AppBar.Lead>

		<AppBar.Headline></AppBar.Headline>
		
		<AppBar.Trail class="justify-self-end">
			<Switch />
			<Notifications />
			<button type="button" class="btn hover:preset-tonal" onclick={handleLogout}>Log Out</button>
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

	.brand-logo {
		height: 3.1rem;
		width: auto;
		display: block;
	}

	@media (max-width: 640px) {
		.brand-logo {
			height: 2.4rem;
		}
	}
</style>
