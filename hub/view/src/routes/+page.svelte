<script>
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';

	import PlantCard from '$lib/components/PlantCard.svelte';
	import { pickMicrocopy } from '$lib/microcopy.js';

	let plants = $state({ plants: [] });
	let homeTagline = $state('');
	let fabAria = $state('Add new plant');

	const getPlants = async () => {
		const response = await fetch('/api/plants');
		plants = await response.json();
	};

	onMount(async () => {
		const d = new Date();
		homeTagline = pickMicrocopy('homeTagline', d);
		fabAria = pickMicrocopy('fabAria', d);
		await getPlants();
	});

	const handleAddPlant = () => {
		goto('/add-plant');
	};
</script>

<main>
	<div class="container column">
		<div class="container home-hero">
			<h1 class="app-title app-title--streetlight">growery</h1>
			{#if homeTagline}
				<p class="microcopy microcopy-muted home-tagline">{homeTagline}</p>
			{/if}
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
	<button class="floating-add-button" onclick={handleAddPlant} aria-label={fabAria}>
		+
	</button>
</main>
