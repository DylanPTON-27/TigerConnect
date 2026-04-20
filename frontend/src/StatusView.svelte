<script lang="ts">
  import { onMount } from "svelte";
  import { Switch } from "@skeletonlabs/skeleton-svelte";
  import FriendList from "./FriendList.svelte";

  const API_BASE = import.meta.env.VITE_API_BASE_URL || "";
  let checked = false;

  onMount(async () => {
    const token = sessionStorage.getItem("accessToken");
    if (!token) return;

    const res = await fetch(`${API_BASE}/friends/get_status`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({}),
    });

    if (res.ok) {
      const data = await res.json();
      checked = !!data.is_active || !!data;
    }
  });

  async function handleToggle(details) {
    checked = details.checked;
    const token = sessionStorage.getItem("accessToken");
    if (!token) return;

    await fetch(`${API_BASE}/friends/status_update`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ active: checked }),
    });
  }
</script>

<div class="h-full w-[95%]">
  <div class="grid grid-flow-col grid-rows-3 gap-4 h-[95%] m-auto">
    <div class="row-span-3 card">
      <div>
        <FriendList />
      </div>
    </div>
    <div class="col-span-2 card">
      <Switch
          {checked}
          onCheckedChange={handleToggle}
        >
          <Switch.Label class="h5">{checked ? "Free" : "Busy"}</Switch.Label>
          <Switch.Control class="bg-red-600 data-[state=checked]:bg-green-700">
            <Switch.Thumb />
          </Switch.Control>
          <Switch.HiddenInput />
        </Switch>
    </div>
    <div class="col-span-2 row-span-2 card">03</div>
  </div>
</div>

<style>
  @import "tailwindcss";
  @custom-variant dark (&:where([data-mode=dark], [data-mode=dark] *));

  .card {
    @apply m-1 h-full w-full;
    @apply border rounded-lg;
    @apply flex justify-center items-center;
  }
</style>
