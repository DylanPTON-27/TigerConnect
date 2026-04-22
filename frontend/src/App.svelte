<script lang="ts">
	import Main from "./Main.svelte";
	import Header from "./Header.svelte";
    import { onMount } from "svelte";
	import { waitForToken } from './helpers.svelte';
	const API_BASE = import.meta.env.VITE_API_BASE_URL || "";
	
	onMount(async () => {
		const url = new URL(window.location.href);
		const nonce = url.searchParams.get("nonce");
		const usernameFromUrl = url.searchParams.get("username");
		const accessTokenFromUrl = url.searchParams.get("accessToken");
		const refreshTokenFromUrl = url.searchParams.get("refreshToken");
		const displayNameFromUrl = url.searchParams.get("displayName");

		// Fallback bootstrap: backend may redirect with tokens directly
		// when nonce persistence fails due production DB schema mismatch.
		if (usernameFromUrl && accessTokenFromUrl && refreshTokenFromUrl) {
			sessionStorage.setItem("username", usernameFromUrl);
			sessionStorage.setItem("accessToken", accessTokenFromUrl);
			sessionStorage.setItem("refreshToken", refreshTokenFromUrl);
			sessionStorage.setItem("displayName", displayNameFromUrl || usernameFromUrl);

			url.searchParams.delete("username");
			url.searchParams.delete("accessToken");
			url.searchParams.delete("refreshToken");
			url.searchParams.delete("displayName");
			history.replaceState({}, "", url.toString());
			return;
		}

		if (!nonce) return;

		const res = await fetch(`${API_BASE}/api/gettokens?nonce=${encodeURIComponent(nonce)}`);
		if (!res.ok) return;

		const [username, accessToken, refreshToken, displayName] = await res.json();
		sessionStorage.setItem("username", username);
		sessionStorage.setItem("accessToken", accessToken);
		sessionStorage.setItem("refreshToken", refreshToken);
		sessionStorage.setItem("displayName", displayName);

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
			sessionStorage.removeItem("displayName");
			window.location.href = "/login";
        	return;
		}

		if (!res.ok) return;

		const newToken = await res.json();
		sessionStorage.setItem("accessToken", newToken);
	}

	onMount(async () => {
		await waitForToken("accessToken");
		refreshToken();
		setInterval(refreshToken, 1_800_000); // 30 minutes
	});
</script>

<div class="h-[8vh] flex items-center">
	<Header />
</div>
<div class="h-[92vh] flex items-center">
	<Main />
</div>
