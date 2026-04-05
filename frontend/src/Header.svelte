<script>
    // @ts-ignore
    import { CalendarIcon, MenuIcon, Bell } from '@lucide/svelte';
	import { AppBar } from '@skeletonlabs/skeleton-svelte';
    import Switch from "./Switch.svelte";
    import { drawerState } from '././sharedVars.svelte.js';
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
	button:hover {
		border-color: #646cff;
	}
	button:focus,
	button:focus-visible {
		outline: 4px auto -webkit-focus-ring-color;
	}
</style>

<AppBar class="bg-zinc-100 dark:bg-zinc-900 h-[10vh] flex justify-center">
	<AppBar.Toolbar class="grid-cols-[auto_1fr_auto]">
		<AppBar.Lead>
			<button type="button" class="btn-icon hover:preset-tonal" onclick={() => drawerState.toggleDrawers()}><MenuIcon /></button>
            <!-- The above button is supposed to be status but idk what symbol to use -->
		</AppBar.Lead>
		<AppBar.Headline>
			<p class="text-2xl">TigerConnect</p>
		</AppBar.Headline>
		<AppBar.Trail>
            <Switch />
			<button type="button" class="btn-icon hover:preset-tonal"><Bell class="size-6" /></button>
			<button type="button" class="btn-icon hover:preset-tonal"><CalendarIcon class="size-6" /></button>
		</AppBar.Trail>
	</AppBar.Toolbar>
</AppBar>