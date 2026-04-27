<script lang="ts">
  import { onMount } from "svelte";
  import { Switch } from "@skeletonlabs/skeleton-svelte";
  import { Avatar } from '@skeletonlabs/skeleton-svelte';
  import { Portal, Tooltip } from '@skeletonlabs/skeleton-svelte';
  import { waitForToken } from './helpers.svelte';
  import FriendList from "./FriendList.svelte";
  import Chat from "./Chat.svelte";

  const API_BASE = import.meta.env.VITE_API_BASE_URL || "";
  let checked = $state(false);
  let initials = $state("");
  let uname = $state("");
  let src = $state("");

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

  async function uploadFile(file) {
		const formData = new FormData();
		formData.append("image", file);

    src = URL.createObjectURL(file);

		const token = sessionStorage.getItem("accessToken");
		if (!token) return;

		const res = await fetch(`${API_BASE}/friends/update_photo`, {
			method: "POST",
			headers: {
				Authorization: `Bearer ${token}`,
			},
			body: formData,
		});
	}

  function handleImageChange(event) {
		const file = event.target.files?.[0];
		if (!file) return;
		void uploadFile(file);
		event.target.value = "";
	}

  async function getImage(token) {

    const res = await fetch(`${API_BASE}/friends/get_photo`, {
			method: "POST",
			headers: {
				Authorization: `Bearer ${token}`,
			},
		});

    if (!res.ok) console.log("Could not fetch profile photo!");

    const blob = await res.blob();
    src = URL.createObjectURL(blob);
  }

  async function getStatus(token) {
    
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

    uname = sessionStorage.getItem("displayName");
    initials = sessionStorage.getItem("username").substring(0, 2).toUpperCase();
  }


  onMount(() => {
    const f = async() => {
      await waitForToken("accessToken");
      const token = sessionStorage.getItem("accessToken");
      if (!token) return;

      getImage(token);
      getStatus(token);
    }

    f();
  });
</script>

<div class="h-full w-[95%]">
  <div class="grid grid-flow-col grid-rows-1 gap-4 h-[95%] m-auto">
    <div class="col-span-1 card">
      <div class="w-full flex items-center p-5">
        <Tooltip positioning={{ placement: 'top' }}>
          <Tooltip.Trigger>
            <label class="cursor-pointer" for="avatar-input">
              <Avatar>
                <Avatar.Image src={src} class="filter-[url(#apollo)]" alt="filtered" />
                <Avatar.Fallback>{initials}</Avatar.Fallback>
              </Avatar>

              <input
                id="avatar-input"
                type="file"
                accept="image/*"
                class="hidden"
                onchange={handleImageChange}
              />
            </label>
          </Tooltip.Trigger>

          <Portal>
            <Tooltip.Positioner>
              <Tooltip.Content class="card p-2 preset-filled-surface-950-50">
                <span>Upload Profile Picture</span>
                <Tooltip.Arrow class="[--arrow-size:--spacing(2)] [--arrow-background:var(--color-surface-950-50)]">
                  <Tooltip.ArrowTip />
                </Tooltip.Arrow>
              </Tooltip.Content>
            </Tooltip.Positioner>
          </Portal>
        </Tooltip>

        <h1 class="ml-5 mr-auto text-2xl">{uname}</h1>

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

      <hr class="hr" />

      <div class="stuffBox">
        <Chat />
      </div>
    </div>

    

    <div class="row-span-full card friendContainer">
      <FriendList />
    </div>
  </div>
</div>

<style>
  @import "tailwindcss";
  @custom-variant dark (&:where([data-mode=dark], [data-mode=dark] *));

  .card {
    @apply m-1 h-full w-full;
    border: 1px solid var(--tc-border);
    background: var(--tc-surface);
    border-radius: 12px;
    color: var(--tc-text);
  }

  .friendContainer {
    @apply flex justify-center items-center;
  }

  .stuffBox {
    @apply flex justify-center items-center;
    @apply p-5;
    color: var(--tc-muted);
  }
</style>
