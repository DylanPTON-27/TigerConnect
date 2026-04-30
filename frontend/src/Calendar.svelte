<script>
	import "temporal-polyfill/global";
	import '@schedule-x/theme-default/dist/index.css'
	import { ScheduleXCalendar } from "@schedule-x/svelte";
	import {
		createCalendar,
		createViewDay,
		createViewWeek,
		createViewMonthGrid,
	} from "@schedule-x/calendar";
	import { themeState } from "./sharedVars.svelte.js";
	import { createCurrentTimePlugin } from "@schedule-x/current-time";
	import { createScrollControllerPlugin } from '@schedule-x/scroll-controller'
	import { createEventsServicePlugin } from '@schedule-x/events-service';
    import { onMount } from "svelte";
	import { waitForToken } from './helpers.svelte';

	const API_BASE = import.meta.env.VITE_API_BASE_URL || "";
	let calendarRenderKey = $state(0);
	const date = new Date();
	date.setHours(date.getHours() - 4);
	const hh = String(date.getHours()).padStart(2, '0');
	const mm = String(date.getMinutes()).padStart(2, '0');
	let numUsers = 0;
	const colorDict = $state({});
	let userEventDict = $state({});
	let visibleGroups = $state([]);
	const eventsService = createEventsServicePlugin();

	const colorCycle = {
		color0: {
			colorName: 'blue',
			lightColors: {
			main: '#1a73e8',
			container: '#d2e3fc',
			onContainer: '#000000',
			},
			darkColors: {
			main: '#8ab4f8',
			container: '#174ea6',
			onContainer: '#ffffff',
			},
		},
		color1: {
			colorName: 'red',
			lightColors: {
			main: '#d93025',
			container: '#fbd7d5',
			onContainer: '#000000',
			},
			darkColors: {
			main: '#f28b82',
			container: '#a50e0e',
			onContainer: '#ffffff',
			},
		},
		color2: {
			colorName: 'green',
			lightColors: {
			main: '#188038',
			container: '#ceead6',
			onContainer: '#000000',
			},
			darkColors: {
			main: '#81c995',
			container: '#0d652d',
			onContainer: '#ffffff',
			},
		},
		color3: {
			colorName: 'yellow',
			lightColors: {
			main: '#f9ab00',
			container: '#feefc3',
			onContainer: '#000000',
			},
			darkColors: {
			main: '#fdd663',
			container: '#af5d00',
			onContainer: '#ffffff',
			},
		},
		color4: {
			colorName: 'purple',
			lightColors: {
			main: '#9333ea',
			container: '#f3e8ff',
			onContainer: '#000000',
			},
			darkColors: {
			main: '#c084fc',
			container: '#581c87',
			onContainer: '#ffffff',
			},
		},
		color5: {
			colorName: 'cyan',
			lightColors: {
			main: '#007b83',
			container: '#cbf0f8',
			onContainer: '#000000',
			},
			darkColors: {
			main: '#4db6ac',
			container: '#004d40',
			onContainer: '#ffffff',
			},
		},
		color6: {
			colorName: 'orange',
			lightColors: {
			main: '#e67c73',
			container: '#fad2cf',
			onContainer: '#000000',
			},
			darkColors: {
			main: '#ff8a65',
			container: '#bf360c',
			onContainer: '#ffffff',
			},
		},
		color7: {
			colorName: 'indigo',
			lightColors: {
			main: '#3f51b5',
			container: '#e8eaf6',
			onContainer: '#000000',
			},
			darkColors: {
			main: '#7986cb',
			container: '#1a237e',
			onContainer: '#ffffff',
			},
		},
		color8: {
			colorName: 'gray',
			lightColors: {
			main: '#70757a',
			container: '#e8eaed',
			onContainer: '#000000',
			},
			darkColors: {
			main: '#9aa0a6',
			container: '#3c4043',
			onContainer: '#ffffff',
			},
		},
		color9: {
			colorName: 'brown',
			lightColors: {
			main: '#795548',
			container: '#d7ccc8',
			onContainer: '#000000',
			},
			darkColors: {
			main: '#a1887f',
			container: '#3e2723',
			onContainer: '#ffffff',
			},
		},
	};

	const scrollController = createScrollControllerPlugin({
	initialScroll: `${hh}:${mm}`
	})
	let calendarApp = $state(createCalendar({
		calendars: colorCycle,
		views: [createViewDay(), createViewWeek(), createViewMonthGrid()],
		events: [],
		timezone: "US/Eastern",
		plugins: [createCurrentTimePlugin(), scrollController, eventsService],
	}));

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

	function assignColor(username) {
		if (!(username in colorDict)) {
			colorDict[username] = `color${numUsers}`;
			numUsers = (numUsers + 1)%10;
			visibleGroups.push(username);
		}
		return colorDict[username];
	}

	function addToUserEvents(username, event) {
		if (username in userEventDict) {
			userEventDict[username].push(event);
		}
		else {
			userEventDict[username] = [event];
		}
	}

	function parseIcsToScheduleXEvents(icsText) {
		const unfolded = icsText.replace(/\r?\n[ \t]/g, "");
		const lines = unfolded.split(/\r?\n/);
		const events = [];
		let current = null;

		userEventDict = {};

		for (const line of lines) {
			if (line === "BEGIN:VEVENT") {
				current = {};
				continue;
			}
			if (line === "END:VEVENT") {
				if (current && current.dtstart && current.dtend) {
					event = {
						id: makeSafeEventId(current.summary),
						title: current.summary || "Untitled Event",
						start: toTemporalStart(current.dtstart),
						end: toTemporalEnd(current.dtend),
						calendarId: assignColor(current.summary),
					}
					events.push(event);
					addToUserEvents(current.summary, event);
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
			const token = sessionStorage.getItem("accessToken");
			if (!token) return;

			const res = await fetch(`${API_BASE}/calendar/get_cal`, {
				method: "POST",
				headers: {
					Authorization: `Bearer ${token}`,
				},
				body: JSON.stringify({}),
			});
			if (!res.ok) {
				return;
			}
			const icsText = await res.text();
			const allEvents = parseIcsToScheduleXEvents(icsText);

			calendarApp = createCalendar({
				calendars: colorCycle,
				views: [createViewDay(), createViewWeek(), createViewMonthGrid()],
				events: allEvents,
				timezone: "US/Eastern",
				plugins: [createCurrentTimePlugin(), scrollController, eventsService],
			});
			calendarRenderKey += 1;
		} catch (err) {
			console.error(err);
		}
	}

	async function uploadFile(file) {
		const formData = new FormData();
		formData.append("file", file);

		const token = sessionStorage.getItem("accessToken");
		if (!token) return;

		const res = await fetch(`${API_BASE}/calendar/upload`, {
			method: "POST",
			headers: {
				Authorization: `Bearer ${token}`,
			},
			body: formData,
		});
		if (!res.ok) {
			return;
		}
		
		await loadLatestCalendar();
	}

	function onFileChange(event) {
		const file = event.target.files?.[0];
		if (!file) return;
		void uploadFile(file);
		event.target.value = "";
	}

	function toggleDark(dark) {
		calendarApp.setTheme(dark ? "dark" : "light");
	}

	function toggleGroup(id) {
		if (visibleGroups.includes(id)) {
		visibleGroups = visibleGroups.filter(g => g !== id);
		} else {
		visibleGroups = [...visibleGroups, id];
		}
		visibleGroups = visibleGroups.filter(item => item !== undefined);
	}

	onMount(() => {
		const f = async () => {
			await waitForToken("accessToken"); 
			await loadLatestCalendar();
		};

		f();
	});

	$effect(() => toggleDark(themeState.themeIsDark));

	$effect(() => {
		if (eventsService.set) {
			let filteredEvents = [];
			for (const username of visibleGroups) {
				filteredEvents.push(userEventDict[username]);
			}
			eventsService.set(filteredEvents.flat());
		}
	})
</script>

<div class="mx-auto mt-3 mb-3 w-[90%] flex items-center gap-3">
	<label class="upload-btn cursor-pointer">
		Upload .ics
		<input type="file" accept=".ics,text/calendar" class="hidden" onchange={onFileChange} />
	</label>
</div>

{#key calendarRenderKey}
	<ScheduleXCalendar {calendarApp} />
{/key}

<div class="h-[5vh] flex justify-center items-center">
	{#each Object.keys(colorDict) as id}
		<div class="toggler">
			<label class="toggle-item" for={id}>
				{id}
			</label>
			<input 
				id={id}
				class="checkbox"
				type="checkbox" 
				checked={visibleGroups.includes(id)} 
				onchange={() => toggleGroup(id)} 
			/>
		</div>
	{/each}
</div>

<style>
	@import "tailwindcss";
	@custom-variant dark (&:where([data-mode=dark], [data-mode=dark] *));

	:global(.sx-svelte-calendar-wrapper) {
		width: 90%;
		max-width: 100vw;
		height: 68vh;
		max-height: 90vh;
		margin: auto;
		border: 1px solid var(--tc-border);
		border-radius: 12px;
		overflow: hidden;
		background: var(--tc-surface);
		color: var(--tc-text);
		position: relative;
		z-index: 500;
	}

	.toggler {
		margin-left: 1vw;
		margin-right: 1vw;
		display: flex;
		justify-content: center;
		align-items: center;
		padding: 5px;
		border-radius: 8px;
		border: 1px solid var(--tc-border);
		background: var(--tc-surface);
		color: var(--tc-text);
	}

	.toggler label {
		margin-left: 1vw;
		margin-right: 1vw;
	}

	.upload-btn {
		border: 1px solid var(--tc-btn);
		background: var(--tc-btn);
		color: var(--tc-btn-text);
		border-radius: 10px;
		padding: 0.55rem 0.9rem;
		font-weight: 600;
		transition: all 0.2s ease;
	}

	.upload-btn:hover {
		background: var(--tc-accent);
		border-color: var(--tc-accent);
		color: var(--tc-text);
	}
</style>
