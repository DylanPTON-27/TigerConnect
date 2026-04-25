<script>
	import { AppBar } from "@skeletonlabs/skeleton-svelte";
	import Notifications from "./Notifications.svelte";
	import Switch from "./Switch.svelte";

	const API_BASE = import.meta.env.VITE_API_BASE_URL || "";

	function handleLogout() {
		sessionStorage.removeItem("username");
		sessionStorage.removeItem("accessToken");
		sessionStorage.removeItem("refreshToken");
		sessionStorage.removeItem("displayName");
		window.location.href = `${API_BASE}/logoutapp`;
		return;
	}
</script>

<AppBar class="justify-center h-auto w-full tc-surface">
	<AppBar.Toolbar class="grid grid-cols-3 items-center px-3 py-1">
		<AppBar.Lead class="flex items-center">
			<a href="/app.html">
				<img class="brand-logo" src="/tigerconnect-logo.png" alt="TigerConnect" />
			</a>
		</AppBar.Lead>

		<AppBar.Headline></AppBar.Headline>
		
		<AppBar.Trail class="justify-self-end">
			<Switch />
			<Notifications />
			<button type="button" class="logout-btn" onclick={handleLogout}>Log Out</button>
		</AppBar.Trail>
	</AppBar.Toolbar>
</AppBar>

<style>
	@import "tailwindcss";
	@custom-variant dark (&:where([data-mode=dark], [data-mode=dark] *));

	button {
		border-radius: 10px;
		margin-right: 5px;
		margin-left: 5px;
		padding: 0.65em 0.95em;
		font-size: 1em;
		font-weight: 600;
		font-family: inherit;
		cursor: pointer;
		transition: all 0.2s ease;
	}
	button:focus,
	button:focus-visible {
		outline: 4px auto -webkit-focus-ring-color;
	}

	.logout-btn {
		border: 1px solid var(--tc-btn);
		background: var(--tc-btn);
		color: var(--tc-btn-text);
	}

	.logout-btn:hover {
		background: var(--tc-accent);
		border-color: var(--tc-accent);
		color: var(--tc-text);
	}

	.brand-logo {
		height: 2.7rem;
		width: auto;
		display: block;
	}

	@media (max-width: 640px) {
		.brand-logo {
			height: 2.4rem;
		}
	}
</style>
