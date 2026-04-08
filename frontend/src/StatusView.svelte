<script lang="ts">
  import { Switch } from "@skeletonlabs/skeleton-svelte";

  let checked = $state(false);
</script>

<div class="h-full w-[95%]">
  <div class="grid grid-flow-col grid-rows-3 gap-4 h-[95%] m-auto">
    <div class="row-span-3 card">
      <div>
        <h1>Status</h1>

        <br />
        <br />

        <Switch
          {checked}
          onCheckedChange={(details) => (checked = details.checked)}
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
