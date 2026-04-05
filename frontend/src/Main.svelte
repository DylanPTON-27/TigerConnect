<script>
	import Calendar from "./Calendar.svelte";
	import { Carousel } from '@skeletonlabs/skeleton-svelte';
</script>

<div>
<Carousel slideCount={2} slidesPerPage={1} spacing="16px">
	<Carousel.ItemGroup class='h-[80vh] w-[70vw]'>
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
					<Carousel.Indicator {index} class='h-6 w-6 border-2 ml-0.75 mr-0.75'/>
				{/each}
			{/snippet}
		</Carousel.Context>
	</Carousel.IndicatorGroup>
</Carousel>
</div>