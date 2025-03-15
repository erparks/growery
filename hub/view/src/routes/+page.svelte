<script>
	import { onMount } from 'svelte';

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
</script>

<main>
	<div class="container column">
		<div class="container">
			<h1 class="app-title">growery</h1>
		</div>

		<div class="flex-grid">
			<ControlsCard />
		</div>

		<div class="flex-grid">
			{#each plants as plant}
				<PlantCard {plant} />
			{/each}
		</div>
	</div>
</main>
