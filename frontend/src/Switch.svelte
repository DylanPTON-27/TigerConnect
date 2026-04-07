<script lang="ts">
	import { Switch } from '@skeletonlabs/skeleton-svelte';
	import { themeState } from './sharedVars.svelte.js';

	let checked = $state(false);

	$effect(() => {
		const mode = localStorage.getItem('mode') || 'light';
		checked = mode === 'dark';
		themeState.themeIsDark = mode === 'dark';
	});

	const onCheckedChange = (event: { checked: boolean }) => {
		const mode = event.checked ? 'dark' : 'light';
		document.documentElement.setAttribute('data-mode', mode);
		localStorage.setItem('mode', mode);
		checked = event.checked;
		themeState.toggleTheme()
	};
</script>

<svelte:head>
	<script>
		document.documentElement.setAttribute('data-mode', localStorage.getItem('mode') || 'light');
	</script>
</svelte:head>

<Switch {checked} {onCheckedChange}>
	<Switch.Control class='bg-zinc-900 data-[state=checked]:bg-zinc-100'>
		<Switch.Thumb class='bg-zinc-100 data-[state=checked]:bg-zinc-900' />
	</Switch.Control>
	<Switch.HiddenInput />
</Switch>