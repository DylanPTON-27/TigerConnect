<script lang="ts">
	import Main from "./Main.svelte";
	import Header from "./Header.svelte";
    import { onMount } from "svelte";
	const API_BASE = import.meta.env.VITE_API_BASE_URL || "";
	
	onMount(async () => {
		const url = new URL(window.location.href);
		const nonce = url.searchParams.get("nonce");
		if (!nonce) return;

		const res = await fetch(`${API_BASE}/api/gettokens?nonce=${encodeURIComponent(nonce)}`);
		if (!res.ok) return;

		const [username, accessToken, refreshToken] = await res.json();
		sessionStorage.setItem("username", username);
		sessionStorage.setItem("accessToken", accessToken);
		sessionStorage.setItem("refreshToken", refreshToken);

		url.searchParams.delete("nonce");
		history.replaceState({}, "", url.toString());
	});

	async function refreshToken() {
		const token = sessionStorage.getItem("refreshToken")
		const res = await fetch(`${API_BASE}/api/refreshaccesstoken`, {
			method: "POST",
			headers: {
				Authorization: `Bearer ${token}`,
			},
		});

		if (res.status === 401 || res.status === 422) {
			sessionStorage.removeItem("username");
			sessionStorage.removeItem("accessToken");
			sessionStorage.removeItem("refreshToken");
			window.location.href = "/login";
        	return;
		}

		if (!res.ok) return;

		const newToken = await res.json();
		sessionStorage.setItem("accessToken", newToken);
	}

	onMount(async () => {
		setTimeout(() => {
			refreshToken();
			setInterval(async () => {
				refreshToken();
			}, 1_800_000); // 30 minutes
		}, 500);
	});
</script>

<div class="h-[8vh] flex items-center">
	<Header />
</div>
<div class="h-[92vh] flex items-center">
	<Main />
</div>
