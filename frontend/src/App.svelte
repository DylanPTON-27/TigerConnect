<script lang="ts">
	import { onMount } from "svelte";
	import Sidebar from "./Sidebar.svelte";
	import Main from "./Main.svelte";
	import Header from "./Header.svelte";

	onMount(async () => {
		const url = new URL(window.location.href);
		const nonce = url.searchParams.get("nonce");
		if (!nonce) return;

		const res = await fetch(`/api/gettokens?nonce=${encodeURIComponent(nonce)}`);
		if (!res.ok) return;

		const [username, accessToken, refreshToken] = await res.json();
		sessionStorage.setItem("username", username);
		sessionStorage.setItem("accessToken", accessToken);
		sessionStorage.setItem("refreshToken", refreshToken);

		url.searchParams.delete("nonce");
		history.replaceState({}, "", url.toString());
	});
</script>

<div>
	<Header />
	<div class="grid grid-cols-[auto_1fr]">
		<div>
			<Sidebar />
		</div>
		<div id="main">
			<Main />
		</div>
	</div>
</div>
