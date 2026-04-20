<script>
	import { onMount } from "svelte";
	import { Popover } from "@skeletonlabs/skeleton-svelte";
	import { Bell, X, Check } from "@lucide/svelte";

	const API_BASE = import.meta.env.VITE_API_BASE_URL || "";
	let requests = [];

	onMount(async () => {
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
		}
	});

	async function actOnRequest(sender, action) {
		const token = sessionStorage.getItem("accessToken");
		if (!token) return;

		const endpoint = action === "accept" ? "accept" : "reject";
		const res = await fetch(`${API_BASE}/friends/${endpoint}`, {
			method: "POST",
			headers: {
				Authorization: `Bearer ${token}`,
			},
			body: JSON.stringify({ sender: Array.isArray(sender) ? sender[0] : sender }),
		});
		if (res.ok) {
			requests = requests.filter((r) => (Array.isArray(r) ? r[0] : r) !== (Array.isArray(sender) ? sender[0] : sender));
			window.dispatchEvent(new Event("friends:changed"));
		}
	}
</script>

<Popover>
	<Popover.Trigger><Bell class="size-9.5 rounded-xl p-1 border-2" /></Popover.Trigger>
	<Popover.Positioner class="z-1!">
		<Popover.Content class="card w-96 p-4 bg-surface-100-900 shadow-xl">
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
				<hr class="hr border-t-4 border-primary-500" />
				{#each requests as senderId}
					<div
						class="grid grid-cols-[1fr_auto_auto] gap-4 items-center"
					>
						<div>
							<span class="underline">{Array.isArray(senderId) ? senderId[0] : senderId}</span> wants to be
							your friend
						</div>
						<div>
							<button class="btn-icon preset-filled" onclick={() => actOnRequest(senderId, "accept")}
								><Check class="size-6" /></button
							>
						</div>
						<div>
							<button class="btn-icon preset-filled" onclick={() => actOnRequest(senderId, "reject")}
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
		border-radius: 20px;
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
</style>
