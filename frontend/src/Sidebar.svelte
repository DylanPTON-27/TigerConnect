<script>
    import { Handshake, X } from '@lucide/svelte';
    import { sidebarState } from './sharedVars.svelte.js'; 
    import { Navigation } from '@skeletonlabs/skeleton-svelte';
    import './app.css'


    const links = [
		{ label: 'Alice Fu', href: '/#', status: 'online'},
		{ label: 'Bob', href: '/#', status: 'offline'},
		{ label: 'Charlie', href: '/#', status: 'offline'},
		{ label: 'Dwight', href: '/#', status: 'online'},
	];
</script>

<style>
	@import 'tailwindcss';
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

	.x-icon {
		outline: transparent;
		padding: 0.5em 0.5em;
		@apply bg-transparent;
		@apply text-black dark:text-white;
}
</style>

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