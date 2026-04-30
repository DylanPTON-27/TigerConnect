<script>
	import { onMount } from "svelte";
	import { waitForToken } from './helpers.svelte';
	import { Popover, Portal} from "@skeletonlabs/skeleton-svelte";
	import { Handshake, EllipsisVertical } from "@lucide/svelte";
	import { selectedFriend } from "./sharedVars.svelte.js";
	import "./app.css";

	const API_BASE = import.meta.env.VITE_API_BASE_URL || "";
	let friends = $state([]);
	let receiverNetid = $state("");
	let requestMessage = $state("");

	async function loadFriends() {
		friends = [
			// {
            // "netid": "dc4986",
            // "name": "Dylan Conard",
            // "status": "active",
            // "photoUrl": ""
			// }
		];
		const token = sessionStorage.getItem("accessToken");
		if (!token) return;

		const res = await fetch(`${API_BASE}/friends/get_friends_and_status`, {
			method: "POST",
			headers: {
				"Content-Type": "application/json",
				Authorization: `Bearer ${token}`,
			},
			body: JSON.stringify({}),
		});
		if (res.ok) {
			const friendsJSON = await res.json();
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

	async function removeFriendRequest() {
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
	<div class="flex">
		<input
			class="friend-input px-2 py-1 w-full"
			placeholder="NetID (e.g. ab1234)"
			bind:value={receiverNetid}
		/>
		<button type="button" class="add-btn" onclick={sendFriendRequest}>
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
														removeFriendRequest();}}>
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
														<button class="remove-btn" style="width:5rem;" onclick={() => actOnRequest(senderId, "accept")}>
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

	.friend-input {
		border: 1px solid var(--tc-border);
		border-radius: 10px;
		background: var(--tc-surface);
		color: var(--tc-text);
	}

	.add-btn {
		border: 1px solid var(--tc-btn);
		background: var(--tc-btn);
		color: var(--tc-btn-text);
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
