<script>
  import "./app.css";
  import { onMount } from "svelte";

  const BACKEND_URL = "http://localhost:8000";

  onMount(() => {
    sessionStorage.removeItem("username");
    sessionStorage.removeItem("accessToken");
    sessionStorage.removeItem("refreshToken");
  });
</script>

<main class="landing-background w-full grid items-stretch border border-surface-200-800">
  <div class="flex justify-center items-center">
    <a href={`${BACKEND_URL}/login`}>
      <button type="button" class="btn preset-filled">Login Here</button>
    </a>
  </div>
</main>
