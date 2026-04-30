<script lang='ts'>
	import { onMount } from "svelte";
	import { waitForToken } from './helpers.svelte';
	import { Popover} from "@skeletonlabs/skeleton-svelte";
	import { Handshake, EllipsisVertical } from "@lucide/svelte";
	import { selectedFriend } from "./sharedVars.svelte.js";
	import { Combobox, Portal, type ComboboxRootProps, useListCollection } from '@skeletonlabs/skeleton-svelte';
	import "./app.css";

	const API_BASE = import.meta.env.VITE_API_BASE_URL || "";
	let friends = $state([]);
	let receiverNetid = $state("");
	let requestMessage = $state("");
	let data = $state([]);
	let items = $state([]);

	const collection = $derived(
		useListCollection({
			items: items,
			itemToString: (item) => item.label,
			itemToValue: (item) => item.value,
		}),
	);

	const onOpenChange = () => {
		items = data;
	};

	const onSelect = (event) => {
		receiverNetid = event.itemValue;
	}

	const onInputValueChange: ComboboxRootProps['onInputValueChange'] = (event) => {
		console.log(data);
		const filtered = data.filter((item) => item.value.toLowerCase().includes(event.inputValue.toLowerCase()));
		if (filtered.length > 0) {
			items = filtered;
		} else {
			items = data;
		}
	};

	async function loadFriends() {
		friends = [
			{
            "netid": "dc4986",
            "name": "Dylan Conard",
            "status": "active",
            "photoUrl": ""
			},
			{
            "netid": "cs-TigerConnect",
            "name": "TigerConnect",
            "status": "active",
            "photoUrl": ""
			}
		];
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
			const returnedJSON = await res.json();
			const friendsJSON = returnedJSON.friends;
			data = returnedJSON.all_users;
			for (const row of friendsJSON) {
				friends.push(row);
			}
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

	async function removeFriend() {
		const receiver = receiverNetid.trim().toLowerCase();
		if (!receiver) return;

		const token = sessionStorage.getItem("accessToken");
		if (!token) {
			requestMessage = "Missing auth token.";
			return;
		}

		const res = await fetch(`${API_BASE}/friends/remove`, {
			method: "POST",
			headers: {
				"Content-Type": "application/json",
				Authorization: `Bearer ${token}`,
			},
			body: JSON.stringify({ receiver }),
		});

		if (res.ok) {
			requestMessage = "Friend removed.";
			receiverNetid = "";
			await loadFriends();
		} else {
			const err = await res.json().catch(() => ({}));
			requestMessage = err.error || "Failed to remove friend.";
		}
	}

	async function blockFriend() {
		const receiver = receiverNetid.trim().toLowerCase();
		if (!receiver) return;

		const token = sessionStorage.getItem("accessToken");
		if (!token) {
			requestMessage = "Missing auth token.";
			return;
		}

		const res = await fetch(`${API_BASE}/friends/block`, {
			method: "POST",
			headers: {
				"Content-Type": "application/json",
				Authorization: `Bearer ${token}`,
			},
			body: JSON.stringify({ receiver }),
		});

		if (res.ok) {
			requestMessage = "Friend blocked.";
			receiverNetid = "";
			await loadFriends();
		} else {
			const err = await res.json().catch(() => ({}));
			requestMessage = err.error || "Failed to block friend.";
		}
	}

	async function unblockFriend() {
		const receiver = receiverNetid.trim().toLowerCase();
		if (!receiver) return;

		const token = sessionStorage.getItem("accessToken");
		if (!token) {
			requestMessage = "Missing auth token.";
			return;
		}

		const res = await fetch(`${API_BASE}/friends/unblock`, {
			method: "POST",
			headers: {
				"Content-Type": "application/json",
				Authorization: `Bearer ${token}`,
			},
			body: JSON.stringify({ receiver }),
		});

		if (res.ok) {
			requestMessage = "Friend blocked.";
			receiverNetid = "";
			await loadFriends();
		} else {
			const err = await res.json().catch(() => ({}));
			requestMessage = err.error || "Failed to block friend.";
		}
	}

	function handleFriendsChanged() {
		void loadFriends();
	}

	function selectFriend(name, netid, photo) {
		selectedFriend.changeFriend(name, netid, photo);
	}

	onMount(() => {
		const f = async () => {
			await waitForToken("accessToken");
			await loadFriends();
			window.addEventListener("friends:changed", handleFriendsChanged);
			return () => window.removeEventListener("friends:changed", handleFriendsChanged);
		};

		f();
	});
</script>

<div class="container">
<header class="text-xl font-bold flex items-center">
	<Handshake class="size-6 inline-block mr-1" />
	Friends List
</header>
<article class="flex items-center h-[15%]">
	<div class="flex h-[50%] w-full">
		<Combobox class="px-2 w-full" placeholder="Search People..." {collection} {onOpenChange} {onInputValueChange} {onSelect} inputBehavior="autohighlight" >
			<Combobox.Control>
				<Combobox.Input class="h-[5vh] rounded-[10px]" />
				<Combobox.Trigger />
			</Combobox.Control>
			<Portal>
				<Combobox.Positioner>
					<Combobox.Content>
						{#each items as item (item.value)}
							<Combobox.Item {item}>
								<Combobox.ItemText>{item.label}</Combobox.ItemText>
								<Combobox.ItemIndicator />
							</Combobox.Item>
						{/each}
					</Combobox.Content>
				</Combobox.Positioner>
			</Portal>
		</Combobox>

		<button type="button" class="add-btn flex items-center" onclick={sendFriendRequest}>
			Add
		</button>
	</div>
	{#if requestMessage}
		<p class="text-sm mb-2">{requestMessage}</p>
	{/if}
</article>
<footer>
	{#each friends as friend}
		<div class="grid grid-cols-[1fr_auto] gap-1 items-center">
			<button type="button" class="names" onclick={() => selectFriend(friend.name, friend.netid, friend.photoUrl)}>
				<div>
					<span class="truncate">{friend.name}</span>
				</div>
				<div>
					{#if friend.status === 'offline'}
						<span class="ml-auto shrink-0 text-red-600">Busy</span>
					{:else}
						<span class="ml-auto shrink-0 text-green-600">Free</span>
					{/if}
				</div>
			</button>
			<div class="justify-self-center">
				<Popover>
					<Popover.Trigger>
						<button class="btn-icon action-btn">
							<EllipsisVertical class="size-6" />
						</button>
					</Popover.Trigger>
					<Portal>
						<Popover.Positioner class=grid grid-cols-[auto]>
							<Popover.Content class="card notif-surface max-w-md p-1.5 shadow-xl justify-items-center">
								<div>
									<Popover positioning={{ placement: 'left' }}>
										<Popover.Trigger>
											<button class="remove-btn">
												Remove Friend
											</button>
										</Popover.Trigger>
										<Portal>
											<Popover.Positioner>
												<Popover.Content class="card notif-surface max-w-md p-1.5 shadow-xl justify-items-center">
														<header>
															Are you sure?
														</header>
														<button class="remove-btn" style="width:5rem;" onclick={() => {
														receiverNetid = friend.netid;
														removeFriend();}}>
															Yes
														</button>
														<Popover.CloseTrigger class="mt-1 mb-1 text-base justify-items-center bg-transparent" 
														style="width:9rem;color:var(--tc-text);border:2px solid var(--tc-border);padding: 0.2rem 0rem;border-radius:10px;width:5rem;">
															No
														</Popover.CloseTrigger>
													<Popover.Arrow class="[--arrow-size:--spacing(2)] [--arrow-background:var(--color-surface-100-900)]">
														<Popover.ArrowTip />
													</Popover.Arrow>
												</Popover.Content>
											</Popover.Positioner>
										</Portal>
									</Popover>
								</div>

								<div>
									<Popover positioning={{ placement: 'left' }}>
										<Popover.Trigger>
											<button class="remove-btn">
												Block Friend
											</button>
										</Popover.Trigger>
										<Portal>
											<Popover.Positioner>
												<Popover.Content class="card notif-surface max-w-md p-1.5 shadow-xl justify-items-center">
														<header>
															Are you sure?
														</header>
														<button class="remove-btn" style="width:5rem;" onclick={() => {
														receiverNetid = friend.netid;
														blockFriend();}}>
															Yes
														</button>
														<Popover.CloseTrigger class="mt-1 mb-1 text-base justify-items-center bg-transparent" 
														style="width:9rem;color:var(--tc-text);border:2px solid var(--tc-border);padding: 0.2rem 0rem;border-radius:10px;width:5rem;">
															No
														</Popover.CloseTrigger>
													<Popover.Arrow class="[--arrow-size:--spacing(2)] [--arrow-background:var(--color-surface-100-900)]">
														<Popover.ArrowTip />
													</Popover.Arrow>
												</Popover.Content>
											</Popover.Positioner>
										</Portal>
									</Popover>
								</div>

								<Popover.Arrow class="[--arrow-size:--spacing(2)] [--arrow-background:var(--color-surface-100-900)]">
									<Popover.ArrowTip />
								</Popover.Arrow>
							</Popover.Content>
						</Popover.Positioner>
					</Portal>
				</Popover>
			</div>
		</div>
	{/each}
</footer>
</div>

<style>
	@import "tailwindcss";
	@import '@skeletonlabs/skeleton';
	@custom-variant dark (&:where([data-mode=dark], [data-mode=dark] *));

	.container {
		@apply divide-y;
		@apply h-[95%] w-[90%];
		background: var(--tc-surface);
		border: 1px solid var(--tc-border);
		border-radius: 12px;
		padding: 0.9rem;
		color: var(--tc-text);
	}

	button {
		border-radius: 10px;
		margin-right: 0.4rem;
		margin-left: 0.4rem;
		padding: 0.55em 0.9em;
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

	.add-btn {
		border: 1px solid var(--tc-btn);
		background: var(--tc-btn);
		color: var(--tc-btn-text);
		height: 5vh;
	}

	.add-btn:hover {
		background: var(--tc-accent);
		border-color: var(--tc-accent);
		color: var(--tc-text);
	}

	.names {
		@apply mt-1 mb-1 text-base;
		@apply grid grid-cols-[1fr_auto] justify-items-start w-full;
		@apply truncate;
		@apply bg-transparent;
		color: var(--tc-text);
		border: 1px solid var(--tc-border);
		padding: 0.5rem 0.7rem;
	}

	.remove-btn {
		@apply mt-1 mb-1 text-base;
		@apply justify-items-center;
		@apply bg-transparent;
		width: 9rem;
		color: var(--tc-text);
		border: 2px solid var(--tc-border);
		padding: 0.2rem 0rem;
	}
</style>
