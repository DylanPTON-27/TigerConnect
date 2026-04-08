<script lang="ts">
  import { onMount } from "svelte";
  import { Switch } from "@skeletonlabs/skeleton-svelte";

  // Replace with actual user ID logic
  const userId = "Bob";

  let checked = false;

  // Fetch current status on mount
  onMount(async () => {
    const res = await fetch("/friends/get_status", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user: userId }),
    });
    if (res.ok) {
      const data = await res.json();
      // Assuming backend returns { is_active: true/false } or just true/false
      checked = !!data.is_active || !!data;
    }
  });

  // Update status when toggled
  async function handleToggle(details) {
    checked = details.checked;
    await fetch("/friends/status_update", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user: userId, active: checked }),
    });
  }
</script>

<div class="h-full w-[95%]">
  <div class="grid grid-flow-col grid-rows-3 gap-4 h-[95%] m-auto">
    <div class="row-span-3 card">
      <div>
        <h1>Status</h1>
        <br /><br />
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
    </div>
    <div class="col-span-2 card">02</div>
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
