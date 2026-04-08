<script>
	import "./app.css";
	const BACKEND_URL = "http://localhost:8000"; // change to render url for prod
</script>

<main
	class="landing-background w-full grid items-stretch border border-surface-200-800"
>
	<div class="flex justify-center items-center">
		<a href={`${BACKEND_URL}/login`}>
			<button type="button" class="btn preset-filled">Login Here</button>
		</a>
	</div>
</main>
