<script>
	import { onMount } from "svelte";
	import { ScheduleXCalendar } from "@schedule-x/svelte";
	import {
		createCalendar,
		createViewDay,
		createViewWeek,
	} from "@schedule-x/calendar";
	import { themeState } from "./sharedVars.svelte.js";
	import { createCurrentTimePlugin } from "@schedule-x/current-time";
	import "@schedule-x/theme-default/dist/index.css";
	import "temporal-polyfill/global";

	const API_BASE = import.meta.env.VITE_API_BASE_URL || "";
	let statusMessage = "";
	let calendarApp = createCalendar({
		views: [createViewDay(), createViewWeek()],
		events: [],
		timezone: "US/Eastern",
		isDark: themeState.themeIsDark,
		plugins: [createCurrentTimePlugin()],
	});

	function formatDateOnly(raw) {
		const year = raw.slice(0, 4);
		const month = raw.slice(4, 6);
		const day = raw.slice(6, 8);
		return `${year}-${month}-${day}`;
	}

	function formatDateTime(raw) {
		// Supports values like 20260408T220000Z or 20260408T220000.
		const datePart = raw.slice(0, 8);
		const timePart = raw.slice(9, 15);
		const year = datePart.slice(0, 4);
		const month = datePart.slice(4, 6);
		const day = datePart.slice(6, 8);
		const hour = timePart.slice(0, 2);
		const minute = timePart.slice(2, 4);
		return `${year}-${month}-${day} ${hour}:${minute}`;
	}

	function parseIcsToScheduleXEvents(icsText) {
		const unfolded = icsText.replace(/\r?\n[ \t]/g, "");
		const lines = unfolded.split(/\r?\n/);
		const events = [];
		let current = null;

		for (const line of lines) {
			if (line === "BEGIN:VEVENT") {
				current = {};
				continue;
			}
			if (line === "END:VEVENT") {
				if (current && current.dtstart && current.dtend) {
					const startRaw = current.dtstart;
					const endRaw = current.dtend;
					const isAllDay = !startRaw.includes("T");

					events.push({
						id: current.uid || crypto.randomUUID(),
						title: current.summary || "Untitled Event",
						start: isAllDay ? formatDateOnly(startRaw) : formatDateTime(startRaw),
						end: isAllDay ? formatDateOnly(endRaw) : formatDateTime(endRaw),
					});
				}
				current = null;
				continue;
			}
			if (!current) continue;

			const splitIndex = line.indexOf(":");
			if (splitIndex < 0) continue;
			const key = line.slice(0, splitIndex).split(";")[0].toLowerCase();
			const value = line.slice(splitIndex + 1).trim();

			if (key === "uid") current.uid = value;
			if (key === "summary") current.summary = value;
			if (key === "dtstart") current.dtstart = value;
			if (key === "dtend") current.dtend = value;
		}
		return events;
	}

	async function loadLatestCalendar() {
		try {
			const res = await fetch(`${API_BASE}/api/calendar`);
			if (!res.ok) {
				statusMessage = "No uploaded .ics yet.";
				return;
			}
			const icsText = await res.text();
			const parsedEvents = parseIcsToScheduleXEvents(icsText);

			calendarApp = createCalendar({
				views: [createViewDay(), createViewWeek()],
				events: parsedEvents,
				timezone: "US/Eastern",
				isDark: themeState.themeIsDark,
				plugins: [createCurrentTimePlugin()],
			});
			statusMessage = `Loaded ${parsedEvents.length} events from latest upload.`;
		} catch (err) {
			statusMessage = "Failed to load calendar.";
		}
	}

	async function uploadFile(file) {
		const formData = new FormData();
		formData.append("file", file);
		const res = await fetch(`${API_BASE}/api/upload`, {
			method: "POST",
			body: formData,
		});
		if (!res.ok) {
			statusMessage = "Upload failed.";
			return;
		}
		statusMessage = "Upload succeeded. Reloading events...";
		await loadLatestCalendar();
	}

	function onFileChange(event) {
		const file = event.target.files?.[0];
		if (!file) return;
		void uploadFile(file);
		event.target.value = "";
	}

	onMount(() => {
		void loadLatestCalendar();
	});
</script>

<div class="mx-auto mb-3 w-[90%] flex items-center gap-3">
	<label class="btn preset-filled cursor-pointer">
		Upload .ics
		<input type="file" accept=".ics,text/calendar" class="hidden" on:change={onFileChange} />
	</label>
	{#if statusMessage}
		<span class="text-sm">{statusMessage}</span>
	{/if}
</div>

<ScheduleXCalendar {calendarApp} />

<style>
	:global(.sx-svelte-calendar-wrapper) {
		width: 90%;
		max-width: 100vw;
		height: 80vh;
		max-height: 90vh;
		margin: auto;
	}
</style>
