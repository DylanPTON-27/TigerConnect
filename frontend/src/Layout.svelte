<script lang="ts">
	import { CircleUserIcon } from '@lucide/svelte';
	import { Navigation } from '@skeletonlabs/skeleton-svelte';
    import { drawerState } from './sharedVars.svelte.js';
	import Main from "./Main.svelte";

	const links = [
		{ label: 'Alice', href: '/#', icon: CircleUserIcon },
		{ label: 'Bob', href: '/#', icon: CircleUserIcon },
		{ label: 'Charlie', href: '/#', icon: CircleUserIcon },
		{ label: 'Dwight', href: '/#', icon: CircleUserIcon },
	];

	const buttonClasses = 'btn hover:preset-tonal';
	let anchorRail = `${buttonClasses} aspect-square w-full max-w-[84px] flex flex-col items-center gap-0.5`;
	let anchorSidebar = `${buttonClasses} justify-start px-2 w-full`;
</script>

<main class="w-full h-[90vh] grid grid-cols-[auto_1fr] items-stretch border border-surface-200-800">
	<Navigation layout={drawerState.showDrawers ? 'rail' : 'sidebar'} class={drawerState.showDrawers ? '' : 'grid grid-rows-[1fr_auto] gap-4'}>
		<Navigation.Content class='m-auto'>
			<Navigation.Menu>
				{#each links as link (link)}
					{@const Icon = link.icon}
					<Navigation.TriggerAnchor>
						<Icon class={drawerState.showDrawers ? 'size-7' : 'size-7'} />
						<Navigation.TriggerText class='text-lg'>{link.label}</Navigation.TriggerText>
					</Navigation.TriggerAnchor>
				{/each}
			</Navigation.Menu>
		</Navigation.Content>
	</Navigation>

	<div class="flex justify-center items-center">
		<Main />
	</div>
</main>