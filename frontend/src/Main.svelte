<script lang="ts">
	import { Carousel } from "@skeletonlabs/skeleton-svelte";
	import Calendar from "./Calendar.svelte";
	import StatusView from "./StatusView.svelte";

	const tabs = ["Status", "Calendar"];
</script>

<Carousel slideCount={2} slidesPerPage={1} spacing="16px">
	<Carousel.ItemGroup class="carousel">
		<Carousel.Item index={0}>
			<div class="flex justify-center h-full">
				<StatusView />
			</div>
		</Carousel.Item>

		<Carousel.Item index={1}>
			<Calendar />
		</Carousel.Item>
	</Carousel.ItemGroup>
	<Carousel.IndicatorGroup class="mt-2">
		<Carousel.Context>
			{#snippet children(carousel)}
				{#each carousel().pageSnapPoints as _, index}
					<Carousel.Indicator {index} class="indicators">
						{tabs[index]}
					</Carousel.Indicator>
				{/each}
			{/snippet}
		</Carousel.Context>
	</Carousel.IndicatorGroup>
</Carousel>

<style>
	@import "tailwindcss";

	:global(.carousel) {
		@apply h-auto w-full;
	}

	:global(.indicators) {
		@apply text-[2vh];
		@apply h-[5vh] w-auto;
		@apply border-2;
		@apply ml-0.75 mr-0.75;
		@apply rounded-xl;
		@apply p-2;
		@apply flex items-center justify-center;
	}

	:global(.indicators[data-current]) {
		@apply text-black;
		background-color: #ff8f1f;
		border-color: #e77500;
	}
</style>
