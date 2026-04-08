<script>
	import "temporal-polyfill/global";
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

	const API_BASE = import.meta.env.VITE_API_BASE_URL || "";
	let statusMessage = "";
	let calendarRenderKey = 0;
	let calendarApp = createCalendar({
		views: [createViewDay(), createViewWeek()],
		events: [],
		timezone: "US/Eastern",
		isDark: themeState.themeIsDark,
		plugins: [createCurrentTimePlugin()],
	});

	function toPlainDate(dateLike) {
		if (!dateLike) return Temporal.Now.plainDateISO("US/Eastern");
		if (dateLike instanceof Temporal.PlainDate) return dateLike;
		return dateLike.toPlainDate();
	}

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
		const second = timePart.slice(4, 6) || "00";
		return `${year}-${month}-${day}T${hour}:${minute}:${second}`;
	}

	function toTemporalStart(raw) {
		if (!raw.includes("T")) {
			return Temporal.PlainDate.from(formatDateOnly(raw));
		}
		const iso = formatDateTime(raw);
		if (raw.endsWith("Z")) {
			return Temporal.Instant.from(`${iso}Z`).toZonedDateTimeISO("US/Eastern");
		}
		return Temporal.ZonedDateTime.from(`${iso}[US/Eastern]`);
	}

	function toTemporalEnd(raw) {
		if (!raw.includes("T")) {
			return Temporal.PlainDate.from(formatDateOnly(raw));
		}
		const iso = formatDateTime(raw);
		if (raw.endsWith("Z")) {
			return Temporal.Instant.from(`${iso}Z`).toZonedDateTimeISO("US/Eastern");
		}
		return Temporal.ZonedDateTime.from(`${iso}[US/Eastern]`);
	}

	function makeSafeEventId(rawId) {
		const base = (rawId || crypto.randomUUID()).toString();
		const safe = base.replace(/[^A-Za-z0-9_-]/g, "_");
		return `ev_${safe}`;
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
					events.push({
						id: makeSafeEventId(current.uid),
						title: current.summary || "Untitled Event",
						start: toTemporalStart(current.dtstart),
						end: toTemporalEnd(current.dtend),
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
			const selectedDate = parsedEvents.length > 0
				? toPlainDate(parsedEvents[0].start)
				: Temporal.Now.plainDateISO("US/Eastern");

			calendarApp = createCalendar({
				views: [createViewDay(), createViewWeek()],
				events: parsedEvents,
				selectedDate,
				timezone: "US/Eastern",
				isDark: themeState.themeIsDark,
				plugins: [createCurrentTimePlugin()],
			});
			calendarRenderKey += 1;
			statusMessage = `Loaded ${parsedEvents.length} events from latest upload.`;
		} catch (err) {
			console.error(err);
			statusMessage = `Failed to load calendar: ${err?.message || err}`;
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

{#key calendarRenderKey}
	<ScheduleXCalendar {calendarApp} />
{/key}

<style>
	:global(.sx-svelte-calendar-wrapper) {
		width: 90%;
		max-width: 100vw;
		height: 80vh;
		max-height: 90vh;
		margin: auto;
	}
</style>
