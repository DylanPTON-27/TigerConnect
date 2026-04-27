<script>
    import '@talkjs/web-components/default.css';
    import '@talkjs/web-components';
    import { getTalkSession } from '@talkjs/core';
    import { selectedFriend } from "./sharedVars.svelte.js";
    import { onMount } from 'svelte';
    import { waitForToken } from './helpers.svelte';
    import { html } from '@talkjs/web-components';
    import { Avatar } from '@skeletonlabs/skeleton-svelte';

    const appId = 'tnJk8fmq';
    const API_BASE = import.meta.env.VITE_API_BASE_URL || "";

    let userId = $state("");
    let session = $state(null);
    let conversationId = $state("");
    let convIds = $state({});
    let photo = $state("");

    function getConvo(selectedFriend) {
        if (session && selectedFriend.netid) {
            conversationId = convIds[selectedFriend.netid];
        }
    }

    async function getToken() {
        const response = await fetch(`${API_BASE}/friends/get-talkjs-token`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${sessionStorage.getItem("accessToken")}`,
        },
        body: JSON.stringify({}),
        });
        const data = await response.json();
        return data.token;
    }

    async function startUp(token) {
        const storedUsername = sessionStorage.getItem("username");

        // Only proceed if we have a logged-in user
        if (storedUsername && !session) {
            userId = storedUsername;
            
            // Initialize session only once
            session = getTalkSession({appId, userId: storedUsername});
            session.setToken(token);
        }

        const res = await fetch(`${API_BASE}/friends/conversations`, {
			method: "POST",
			headers: {
				"Content-Type": "application/json",
				Authorization: `Bearer ${sessionStorage.getItem("accessToken")}`,
			},
			body: JSON.stringify({}),
		});
        convIds = await res.json();
    }

    function changeImage(selectedFriend) {
        if (selectedFriend.photo === "") {
            const initials = selectedFriend.netid.substring(0, 2).toUpperCase();
            photo = html`<div className="img">${initials}</div>`;
        }
        else {
            photo = html`<div className="t-theme-avatar" style=${{ backgroundImage: `url(${selectedFriend.photo})` }}/>`;
        }
    }

    function Image() {
        return photo;
    }

    onMount(() => {
        const f = async () => {
            await waitForToken("accessToken");
            const token = await getToken();
            startUp(token);
        };

        f();
    });

    $effect(() => {
        changeImage(selectedFriend);
        getConvo(selectedFriend);
    });
</script>

{#if session && conversationId}
    <t-chatbox
        id="chat"
        app-id={appId}
        user-id={userId}
        conversation-id={conversationId}
        theme = {{Avatar: Image}}
    >
    </t-chatbox>
{:else}
    <div class="loading-state">
        {#if !userId}
            <p>Waiting for login...</p>
        {:else}
            <p>Select a friend to start chatting</p>
        {/if}
    </div>
{/if}

<style>
    @import "tailwindcss";

    :global(.t-theme-chat-header) {
        background-color:var(--tc-surface);
        color: var(--tc-text);
        border-color: var(--tc-accent);
    }

    :global(.t-theme-message-field) {
        background-color:var(--tc-surface);
        color: var(--tc-text);
    }

    :global(.t-theme-message-field .t-wrapper) {
        background-color: var(--tc-surface);
        color: var(--tc-text);
        border-color: var(--tc-accent);
    }

    :global(.t-theme-message-field .t-wrapper .t-theme-recording-preview .t-textbox-column) {
        background-color: white;
        border: none;
        color: black;
    }

    :global(.t-theme-message-field .t-wrapper .t-theme-voice-recorder .t-textbox-column) {
        background-color: white;
        border: none;
        color: black;
    }

    :global(.t-theme-message-field .t-editor .t-text-input) {
        background-color: transparent;
        border: none;
    }

    :global(.t-theme-chat-header button svg) {
        stroke: var(--tc-text);
    }

    :global(.t-actions) {
        color: var(--tc-text);
    }

    #chat {
        width: 100%;
        height: 60vh;
        background-color:var(--tc-bg);
        border-color: var(--tc-accent);
    }

    .loading-state {
        border-color: var(--tc-accent);
    }
</style>