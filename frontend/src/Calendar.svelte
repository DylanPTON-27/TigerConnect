<script>
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

	const calendarApp = createCalendar({
		views: [createViewDay(), createViewWeek()],
		events: [
			{
				id: "1",
				title: "Event 1",
				start: Temporal.PlainDate.from("2024-07-06"),
				end: Temporal.PlainDate.from("2024-07-06"),
				calendarId: "personal",
			},
			{
				id: "2",
				title: "Event 2",
				start: Temporal.ZonedDateTime.from(
					"2024-07-06T02:00:00+09:00[Asia/Tokyo]",
				),
				end: Temporal.ZonedDateTime.from(
					"2024-07-06T04:00:00+09:00[Asia/Tokyo]",
				),
				calendarId: "personal",
			},
		],
		timezone: "US/Eastern",
		isDark: themeState.themeIsDark,
		plugins: [createCurrentTimePlugin()],
	});
</script>

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
