<script>
	import { onMount } from "svelte";
	import { sidebarState } from "./sharedVars.svelte.js";
	import { Navigation } from "@skeletonlabs/skeleton-svelte";
	import { SquarePlus, SquareMinus, X } from "@lucide/svelte";
	import "./app.css";

	const API_BASE = import.meta.env.VITE_API_BASE_URL || "";
	let friends = [];
	let receiverNetid;
	let requestMessage;

	async function loadFriends() {
		const token = sessionStorage.getItem("accessToken");
		if (!token) return;

		const res = await fetch(`${API_BASE}/friends/get_all_friends`, {
			method: "POST",
			headers: {
				"Content-Type": "application/json",
				Authorization: `Bearer ${token}`,
			},
			body: JSON.stringify({}),
		});
		if (res.ok) {
			friends = await res.json();
			console.log(friends);
		}
	}

	async function sendFriendRequest() {
		const receiver = receiverNetid.trim().toLowerCase();
		if (!receiver) return;

		const token = sessionStorage.getItem("accessToken");
		if (!token) {
			requestMessage = "Missing auth token.";
			return;
		}

		const res = await fetch(`${API_BASE}/friends/request`, {
			method: "POST",
			headers: {
				"Content-Type": "application/json",
				Authorization: `Bearer ${token}`,
			},
			body: JSON.stringify({ receiver }),
		});

		if (res.ok) {
			requestMessage = "Friend request sent.";
			receiverNetid = "";
			await loadFriends();
		} else {
			const err = await res.json().catch(() => ({}));
			requestMessage = err.error || "Failed to send request.";
		}
	}

	function handleFriendsChanged() {
		void loadFriends();
	}

	onMount(() => {
		void loadFriends();
		window.addEventListener("friends:changed", handleFriendsChanged);
		return () => window.removeEventListener("friends:changed", handleFriendsChanged);
	});

	const links = [
		{ label: 'Alice Fu', href: '/#', status: 'online'},
		{ label: 'Bob', href: '/#', status: 'offline'},
		{ label: 'Charlie', href: '/#', status: 'offline'},
		{ label: 'Dwight', href: '/#', status: 'online'},
	];
</script>

<div
	class="grid grid-cols-[auto_1fr_auto] gap-4 items-center"
>
	<div class="mb-3 flex gap-2">
		<input
			class="input border rounded px-2 py-1 w-full"
			placeholder="NetID (e.g. ab1234)"
			bind:value={receiverNetid}
		/>
		<button type="button" class="btn preset-filled" onclick={sendFriendRequest}>
			Add
		</button>
	</div>
	{#if requestMessage}
		<p class="text-sm mb-2">{requestMessage}</p>
	{/if}
</div>
<div>
	{#each friends as friend}
		<button type="button" class="grid grid-cols-[1fr_auto] justify-items-start w-full min-w-0 names">
			<div>
				<span class="truncate">{Array.isArray(friend) ? friend[0] : friend}</span>
			</div>
			<div>
				<span class="ml-auto shrink-0">(STATUS)</span>
			</div>
		</button>
	{/each}
	</div>

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

	.friends-icon {
		outline: transparent;
		padding: 0.5em 0.5em;
		@apply bg-transparent;
		@apply text-black dark:text-white;
	}

	.names {
		font-size: 1em;
		padding: 0em 1em;
		@apply truncate;
		@apply bg-transparent;
		@apply text-black dark:text-white;
	}
</style>
