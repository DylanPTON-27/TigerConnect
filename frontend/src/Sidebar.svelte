<script>
    import { Handshake, X } from '@lucide/svelte';
    import { sidebarState } from './sharedVars.svelte.js'; 
    import { Navigation } from '@skeletonlabs/skeleton-svelte';
    import './app.css'
	import './css/header.css'


    const links = [
		{ label: 'Alice Fu', href: '/#', status: 'online'},
		{ label: 'Bob', href: '/#', status: 'offline'},
		{ label: 'Charlie', href: '/#', status: 'offline'},
		{ label: 'Dwight', href: '/#', status: 'online'},
	];
</script>

{#if sidebarState.sidebarOpen}
    <Navigation layout="sidebar" class="bg-zinc-300 dark:bg-zinc-800 grid grid-rows-[auto_1fr_auto] gap-4">
		<Navigation.Header class="grid grid-cols-[auto_1fr_auto] gap-4 items-center" >
			<div>
				<Handshake class="size-6" />
			</div>
			<div>
				<p class="text-lg font-bold">Friends List</p>
			</div>
			<div>
				<button type="button" class="x-icon hover:preset-tonal" onclick={() => sidebarState.toggleSidebar()}><X class="size-6" /></button>
			</div>
		</Navigation.Header>
		<Navigation.Content>
			{#each links as link (link)}
				<div class="flex items-center w-full min-w-0">
					<span class="truncate">{link.label}</span>
					<span class="ml-auto shrink-0">{link.status}</span>
				</div>
			{/each}
		</Navigation.Content>
	</Navigation>
{/if}