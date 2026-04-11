<script>
	import { onMount } from 'svelte';

	export let plant;

	let mostRecentPhoto = null;
	let loading = true;
	let imageUrl = null;

	const fetchMostRecentPhoto = async () => {
		try {
			loading = true;
			const response = await fetch(`/api/plants/${plant.id}/photo_histories`);
			if (response.ok) {
				const photoHistories = await response.json();
				if (photoHistories && photoHistories.length > 0) {
					mostRecentPhoto = photoHistories[0]; // First one is most recent (ordered by created_at desc)
					imageUrl = `/api/plants/${plant.id}/photo_histories/${mostRecentPhoto.id}`;
				}
			}
		} catch (error) {
			console.error('Error fetching photo history:', error);
		} finally {
			loading = false;
		}
	};

	onMount(() => {
		fetchMostRecentPhoto();
	});
</script>

<a href={`/plant_detail/?plant_id=${plant['id']}`} class="card card-link plant-card">
	{#if !loading && imageUrl}
		<div class="card-image">
			<img src={imageUrl} alt={`${plant['nickname']} photo`} />
		</div>
	{/if}
	<div class="card-text">
		<h3 class="plant-name">
			{plant['nickname']}
			{#if plant.has_incomplete_notes}
				<span class="incomplete-star" aria-label="Has incomplete notes" title="Has incomplete notes"
					>*</span
				>
			{/if}
		</h3>
		<span class="text-small species">({plant['species']})</span>
	</div>
</a>

<style>
	.plant-card {
		display: block;
		width: 100%;
		padding: 0;
		overflow: hidden;
		text-align: left;
		color: var(--color-text, #e4ebe6);
		text-decoration: none;
		transition:
			transform 0.2s ease,
			box-shadow 0.2s ease,
			border-color 0.2s ease;
	}

	.plant-card:hover {
		color: var(--color-text, #e4ebe6);
		text-decoration: none;
		transform: translateY(-3px);
		box-shadow: var(--shadow-soft, 0 12px 40px rgba(0, 0, 0, 0.35));
		border-color: var(--color-border-strong, rgba(130, 158, 142, 0.38));
	}

	.plant-card:focus-visible {
		outline: 2px solid var(--color-accent, #8fb39a);
		outline-offset: 3px;
	}

	.card-image {
		width: 100%;
		aspect-ratio: 4 / 3;
		overflow: hidden;
		background-color: var(--color-surface-solid, #131a17);
	}

	.card-image img {
		width: 100%;
		height: 100%;
		object-fit: cover;
		display: block;
	}

	.card-text {
		padding: 1rem 1.15rem 1.15rem;
	}

	.plant-name {
		display: block;
		margin: 0 0 0.35rem;
		font-size: 1.125rem;
		font-weight: 600;
		letter-spacing: 0.02em;
		color: var(--color-heading, #dce8df);
	}

	.species {
		display: block;
	}

	.incomplete-star {
		color: var(--color-danger, #c08080);
		font-weight: 700;
	}
</style>
