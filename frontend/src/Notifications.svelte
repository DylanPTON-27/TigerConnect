<script>
	import { Popover } from '@skeletonlabs/skeleton-svelte';
	import { Bell, X, Check } from '@lucide/svelte';
	import './css/header.css'

	const links = [
		{ label: 'Alice Fu', href: '/#', status: 'online'},
		{ label: 'Bob', href: '/#', status: 'online'},
		{ label: 'Charlie', href: '/#', status: 'online'},
		{ label: 'Dwight', href: '/#', status: 'online'},
	];
</script>


<Popover>
	<Popover.Trigger><Bell class="size-6" /></Popover.Trigger>
		<Popover.Positioner class="z-1!">
			<Popover.Content class="card w-96 p-4 bg-surface-100-900 shadow-xl">
				<div class="space-y-4">
					<header class="grid grid-cols-[auto_1fr_auto] gap-4 items-center">
						<div>
							<Bell class="size-6" />
						</div>
						<div>
							<Popover.Title class="text-lg font-bold">Notifications</Popover.Title>
							<p>(Incoming Friend Requests)</p>
						</div>
						<Popover.CloseTrigger class="x-icon hover:preset-tonal">
							<X class="size-4" />
						</Popover.CloseTrigger>
					</header>
					<hr class="hr border-t-4 border-primary-500" />
					{#each links as link (link)}
						<div class="grid grid-cols-[1fr_auto_auto] gap-4 items-center">
							<div> <span class="underline">{link.label}</span> wants to be your friend</div>
							<div> <button class="btn-icon preset-filled"><Check class="size-6" /></button></div>
							<div> <button class="btn-icon preset-filled"><X class="size-6" /></button></div>
						</div>
					{/each}
				</div>
				<Popover.Arrow class="[--arrow-size:--spacing(2)] [--arrow-background:var(--color-surface-100-900)]">
					<Popover.ArrowTip />
				</Popover.Arrow>
			</Popover.Content>
		</Popover.Positioner>
</Popover>