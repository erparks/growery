<script>
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';

	import PlantCard from '$lib/components/PlantCard.svelte';
	import ControlsCard from '$lib/components/controls/ControlsCard.svelte';

	let plants = [];

	const getPlants = async () => {
		const response = await fetch('/api/plants');
		plants = await response.json();
	};

	onMount(async () => {
		await getPlants();
	});

	const handleAddPlant = () => {
		goto('/add-plant');
	};
</script>

<main>
	<div class="container column">
		<div class="container">
			<h1 class="app-title">growery</h1>
		</div>

		<!-- <div class="flex-grid">
			<ControlsCard />
		</div> -->

		<div class="flex-grid">
			{#each plants.plants as plant}
				<PlantCard {plant} />
			{/each}
		</div>
	</div>
	<button class="floating-add-button" on:click={handleAddPlant} aria-label="Add new plant">
		+
	</button>
</main>
