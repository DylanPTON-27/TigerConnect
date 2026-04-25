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

<main class="landing-wrap h-full w-full flex items-center justify-center px-6">
  <div class="hero-card w-full max-w-2xl rounded-2xl p-8 md:p-10 text-center">
    <h1 class="hero-title text-4xl md:text-5xl mb-3">TigerConnect</h1>
    <p class="hero-subtitle text-base md:text-lg mb-8">
      See when your friends are free and plan hangouts faster.
    </p>
    <a href={`${API_BASE}/login`}>
      <button type="button" class="cta-btn">Login with Princeton CAS</button>
    </a>
  </div>
</main>

<style>
  @import "tailwindcss";

  .landing-wrap {
    background: var(--tc-bg);
  }

  .hero-card {
    border: 1px solid var(--tc-border);
    background: var(--tc-surface);
  }

  .hero-title {
    color: var(--tc-text);
    font-weight: 600;
  }

  .hero-subtitle {
    color: var(--tc-muted);
  }

  .cta-btn {
    border-radius: 10px;
    border: 1px solid var(--tc-btn);
    background: var(--tc-btn);
    color: var(--tc-btn-text);
    font-size: 1rem;
    font-weight: 600;
    padding: 0.8rem 1.15rem;
    transition: all 0.2s ease;
  }

  .cta-btn:hover {
    background: var(--tc-accent);
    border-color: var(--tc-accent);
    color: var(--tc-text);
  }
</style>
