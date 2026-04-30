<script>
	import { onMount } from "svelte";
	import { Popover } from "@skeletonlabs/skeleton-svelte";
	import { Bell, X, Check } from "@lucide/svelte";
	import { waitForToken } from './helpers.svelte';

	const API_BASE = import.meta.env.VITE_API_BASE_URL || "";
	let requests = $state([]);
	let areNotifications = $state(false);

	async function fetchNotifications () {
		await waitForToken("accessToken");

		const token = sessionStorage.getItem("accessToken");
		if (!token) return;

		const res = await fetch(`${API_BASE}/friends/notifications`, {
			method: "POST",
			headers: {
				Authorization: `Bearer ${token}`,
			},
			body: JSON.stringify({}),
		});
		if (res.ok) {
			requests = await res.json();
			areNotifications = requests.length > 0;
		}
	}

	onMount(fetchNotifications);

	async function actOnRequest(sender, action) {
		const token = sessionStorage.getItem("accessToken");
		if (!token) return;

		const endpoint = action === "accept" ? "accept" : "reject";
		const res = await fetch(`${API_BASE}/friends/${endpoint}`, {
			method: "POST",
			headers: {
				"Content-Type": "application/json",
				Authorization: `Bearer ${token}`,
			},
			body: JSON.stringify({ sender: Array.isArray(sender) ? sender[0] : sender }),
		});
		if (res.ok) {
			requests = requests.filter((r) => (Array.isArray(r) ? r[0] : r) !== (Array.isArray(sender) ? sender[0] : sender));
			window.dispatchEvent(new Event("friends:changed"));
			areNotifications = requests.length > 0;
		}
	}
</script>

<Popover>
	<Popover.Trigger>
		<div class={areNotifications ? 'rounded-xl active' : 'rounded-xl'}>
			<Bell
				class="size-9.5 rounded-xl p-1 border-2"
				style="border-color:var(--tc-border);background:var(--tc-text);color:var(--tc-surface);"
			/>
		</div>
	</Popover.Trigger>
	<Popover.Positioner class="z-1000! relative">
		<Popover.Content class="notif-surface card w-96 p-4 shadow-xl">
			<div class="space-y-4">
				<header
					class="grid grid-cols-[auto_1fr_auto] gap-4 items-center"
				>
					<div>
						<Bell class="size-6" />
					</div>
					<div>
						<Popover.Title class="text-lg font-bold"
							>Notifications</Popover.Title
						>
						<p>(Incoming Friend Requests)</p>
					</div>
					<Popover.CloseTrigger class="x-icon hover:preset-tonal">
						<X class="size-4" />
					</Popover.CloseTrigger>
				</header>
				<hr class="notif-divider hr border-t-2" />
				{#each requests as senderId}
					<div
						class="grid grid-cols-[1fr_auto_auto] gap-4 items-center"
					>
						<div>
							<span class="underline">{Array.isArray(senderId) ? senderId[0] : senderId}</span> wants to be
							your friend
						</div>
						<div>
							<button class="btn-icon action-btn" onclick={() => actOnRequest(senderId, "accept")}
								><Check class="size-6" /></button
							>
						</div>
						<div>
							<button class="btn-icon action-btn" onclick={() => actOnRequest(senderId, "reject")}
								><X class="size-6" /></button
							>
						</div>
					</div>
				{/each}
			</div>
			<Popover.Arrow
				class="[--arrow-size:--spacing(2)] [--arrow-background:var(--color-surface-100-900)]"
			>
				<Popover.ArrowTip />
			</Popover.Arrow>
		</Popover.Content>
	</Popover.Positioner>
</Popover>

<style>
	@import "tailwindcss";
	@custom-variant dark (&:where([data-mode=dark], [data-mode=dark] *));

	button {
		border-radius: 10px;
		margin-right: 5px;
		margin-left: 5px;
		padding: 0.55em 0.85em;
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

	.action-btn {
		border: 1px solid var(--tc-btn);
		background: var(--tc-btn);
		color: var(--tc-btn-text);
	}

	.action-btn:hover {
		background: var(--tc-accent);
		border-color: var(--tc-accent);
		color: var(--tc-text);
	}

	:global(.notif-surface) {
		background: var(--tc-surface);
		border: 1px solid var(--tc-border);
		color: var(--tc-text);
	}

	.notif-divider {
		border-color: var(--tc-border);
	}

	.active {
		animation: notified 1.2s infinite;
	}

	@keyframes notified {
		0% {
			background-color: rgba(255, 0, 0, 0); 
		}

		50% {
			background-color: rgba(255, 143, 31, 0.35); 
		}

		100% {
			background-color: rgba(255, 0, 0, 0); 
		}
	}
</style>
