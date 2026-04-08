<script>
  import "./app.css";
  import { onMount } from "svelte";

  const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

  onMount(() => {
    const params = new URLSearchParams(window.location.search);

    // Robust fallback: if CAS nonce lands on "/", forward to app route.
    if (params.get("nonce")) {
      window.location.href = `/app.html?${params.toString()}`;
      return;
    }

    if (params.get("logout") === "1") {
      sessionStorage.removeItem("username");
      sessionStorage.removeItem("accessToken");
      sessionStorage.removeItem("refreshToken");
      params.delete("logout");
      const next = `${window.location.pathname}${params.toString() ? `?${params.toString()}` : ""}`;
      history.replaceState({}, "", next);
      return;
    }

    if (sessionStorage.getItem("accessToken")) {
      window.location.href = "/app.html";
    }
  });
</script>

<main class="landing-background w-full grid items-stretch border border-surface-200-800">
  <div class="flex justify-center items-center">
    <a href={`${API_BASE}/login`}>
      <button type="button" class="btn preset-filled">Login Here</button>
    </a>
  </div>
</main>
