<script>
    // @ts-ignore
    import { Menu } from '@lucide/svelte';
	import { AppBar } from '@skeletonlabs/skeleton-svelte';
    import { sidebarState } from '././sharedVars.svelte.js';
	import Notifications from "./Notifications.svelte";
	import Switch from "./Switch.svelte";
	import './css/header.css'
</script>

<AppBar class="bg-zinc-400 dark:bg-zinc-900 flex justify-center">
	<AppBar.Toolbar class="grid grid-cols-3 items-center">
		<AppBar.Lead class="justify-self-start">
			<button type="button" class="btn hover:preset-tonal" onclick={() => sidebarState.toggleSidebar()}><Menu class="size-6" /></button>
			<a href = "/calendar.html">
			<button type="button" class="btn hover:preset-tonal">Calendar</button>
			</a>
			<a href = "/">
			<button type="button" class="btn hover:preset-tonal">Status</button>
			</a>
		</AppBar.Lead>
		<AppBar.Headline class="justify-self-center">
			<a href = "/"><button type="button" class="Title">TigerConnect</button></a>
		</AppBar.Headline>
		<AppBar.Trail class="justify-self-end">
            <Switch />
			<Notifications />
			<a href = "/landing.html">
				<button type="button" class="btn hover:preset-tonal">Log Out</button>
			</a>
		</AppBar.Trail>
	</AppBar.Toolbar>
</AppBar>