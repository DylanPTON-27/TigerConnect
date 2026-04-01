<script>
	import Calendar from "./Calendar.svelte";
	import { Carousel } from '@skeletonlabs/skeleton-svelte';
</script>

<div>
<Carousel slideCount={2} slidesPerPage={1} spacing="16px">
	<Carousel.ItemGroup class='h-[80vh] w-[60vw]'>
		<Carousel.Item index={0}>
			<Calendar />
		</Carousel.Item>

		<Carousel.Item index={1}>
			Other Page
		</Carousel.Item>
	</Carousel.ItemGroup>
	<Carousel.IndicatorGroup>
		<Carousel.Context>
			{#snippet children(carousel)}
				{#each carousel().pageSnapPoints as _, index}
					<Carousel.Indicator {index}/>
				{/each}
			{/snippet}
		</Carousel.Context>
	</Carousel.IndicatorGroup>
</Carousel>
</div>