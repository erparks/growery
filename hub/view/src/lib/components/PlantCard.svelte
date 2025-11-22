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

<div class="card">
	<a href={`/plant_detail/?plant_id=${plant['id']}`}>
		<div class="card-content">
			<div class="card-text">
				<h3>{plant['nickname']}</h3>
				<span class="text-small">({plant['species']})</span>
			</div>
			{#if !loading && imageUrl}
				<div class="card-image">
					<img src={imageUrl} alt={`${plant['nickname']} photo`} />
				</div>
			{/if}
		</div>
	</a>
</div>

<style>
	.card-content {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 1rem;
		width: 100%;
	}

	.card-text {
		flex: 1;
		text-align: left;
	}

	.card-image {
		flex-shrink: 0;
		width: 80px;
		height: 80px;
		overflow: hidden;
		border-radius: 4px;
		background-color: rgba(0, 0, 0, 0.3);
	}

	.card-image img {
		width: 100%;
		height: 100%;
		object-fit: cover;
	}
</style>
