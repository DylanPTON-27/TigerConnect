<script lang="ts">
	import { Carousel } from "@skeletonlabs/skeleton-svelte";
	import Calendar from "./Calendar.svelte";
</script>

<Carousel slideCount={2} slidesPerPage={1} spacing="16px">
	<Carousel.ItemGroup class="carousel">
		<Carousel.Item index={0}>
			<Calendar />
		</Carousel.Item>

		<Carousel.Item index={1}>Other Page</Carousel.Item>
	</Carousel.ItemGroup>
	<Carousel.IndicatorGroup>
		<Carousel.Context>
			{#snippet children(carousel)}
				{#each carousel().pageSnapPoints as _, index}
					<Carousel.Indicator {index} class="indicators" />
				{/each}
			{/snippet}
		</Carousel.Context>
	</Carousel.IndicatorGroup>
</Carousel>

<style>
	@import "tailwindcss";
	@custom-variant dark (&:where([data-mode=dark], [data-mode=dark] *));

	:global(.carousel) {
		@apply h-[80vh] w-[70vw];
		@apply m-auto;
	}

	:global(.indicators) {
		@apply h-6 w-6;
		@apply border-2;
		@apply ml-0.75 mr-0.75;
	}
</style>
