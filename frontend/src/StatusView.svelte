<script lang="ts">
<<<<<<< HEAD
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
=======
</script>

<div>
  <p>Status Page WIP.</p>
  <p>Click on Calendar at top for more fleshed out Calendar Page.</p>
  <p>Menu Icon in top left works only in Calendar view right now.</p>
  <p>TigerConnect redirects to here.</p>
  <p>
    Toggle Light/Dark is setup but isn't connected to the actual calendar in
    Calendar.svelte
  </p>
  <p>Notifcations view should be pretty much done.</p>
  <p>
    Log out just redirects to a landing page that only has a login button. Needs
    to be connected to CAS auth.
  </p>
</div>
>>>>>>> d5465e5 (fixed some layout issues)
