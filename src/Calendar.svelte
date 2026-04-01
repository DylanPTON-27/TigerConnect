<script>
    import { ScheduleXCalendar } from '@schedule-x/svelte';
	import { createCalendar, createViewDay, createViewWeek } from '@schedule-x/calendar';
	import '@schedule-x/theme-default/dist/index.css';
	import 'temporal-polyfill/global'
 
	const calendarApp = createCalendar({
		views: [createViewDay(), createViewWeek()],
		events: [
			{
				id: '1',
				title: 'Event 1',
				start: Temporal.PlainDate.from('2024-07-06'),
				end: Temporal.PlainDate.from('2024-07-06'),
			},
			{
				id: '2',
				title: 'Event 2',
				start: Temporal.ZonedDateTime.from('2024-07-06T02:00:00+09:00[Asia/Tokyo]'),
				end: Temporal.ZonedDateTime.from('2024-07-06T04:00:00+09:00[Asia/Tokyo]'),
			},
		]
	})
</script>

<div>
	<ScheduleXCalendar calendarApp="{calendarApp}" />
</div>