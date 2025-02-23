<script>
	import { onMount } from 'svelte';

	import PlantCard from '$lib/components/PlantCard.svelte';

	let plants = [];

	const getPlants = async () => {
		const response = await fetch('/api/plants');
		plants = await response.json();
	};

	onMount(async () => {
		await getPlants();
	});
</script>

<main>
	<div class="container">
		<h1 class="app-title">growery</h1>
	</div>

	<div class="container flex-grid">
		{#each plants as plant}
			<PlantCard {plant} />
		{/each}
	</div>
</main>
