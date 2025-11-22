<script>
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import PhotoHistories from '$lib/components/PhotoHistories.svelte';

	let plant = null;
	let loading = true;
	let error = null;

	const fetchPlantData = async () => {
		try {
			loading = true;
			error = null;

			const plantId = $page.url.searchParams.get('plant_id');
			if (!plantId) {
				error = 'No plant ID provided';
				return;
			}

			// Fetch plant data
			const plantResponse = await fetch(`/api/plants/${plantId}`);
			if (!plantResponse.ok) {
				error = 'Plant not found';
				return;
			}
			plant = await plantResponse.json();

			// Photo histories are now fetched by the PhotoHistories component itself
		} catch (err) {
			error = 'Failed to load plant data';
			console.error('Error fetching plant data:', err);
		} finally {
			loading = false;
		}
	};

	const formatDate = (dateString) => {
		if (!dateString) return 'N/A';
		const date = new Date(dateString);

		const monthNames = [
			'Jan.',
			'Feb.',
			'Mar.',
			'Apr.',
			'May.',
			'Jun.',
			'Jul.',
			'Aug.',
			'Sep.',
			'Oct.',
			'Nov.',
			'Dec.'
		];
		const formattedDate = `${monthNames[date.getMonth()]} ${date.getDate().toString().padStart(2, '0')}, ${date.getFullYear()}`;

		const now = new Date();
		const seconds = Math.floor((now - date) / 1000);

		const timeAgo = (() => {
			const units = [
				{ label: 'week', secs: 60 * 60 * 24 * 7 },
				{ label: 'day', secs: 60 * 60 * 24 },
				{ label: 'hour', secs: 60 * 60 },
				{ label: 'minute', secs: 60 }
			];
			for (const { label, secs } of units) {
				const value = Math.floor(seconds / secs);
				if (value >= 1) {
					return `${value} ${label}${value > 1 ? 's' : ''} ago`;
				}
			}
			return 'just now';
		})();

		return `${formattedDate} (${timeAgo})`;
	};

	onMount(() => {
		fetchPlantData();
	});
</script>

<main>
	<div class="container column">
		{#if loading}
			<div class="loading">Loading plant data...</div>
		{:else if error}
			<div class="error">{error}</div>
		{:else if plant}
			<div class="plant-detail">
				<h1 class="app-title">{plant.nickname}</h1>

				<!-- Plant Information Table -->
				<section class="card">
					<h2>Plant Information</h2>
					<table class="info-table">
						<tbody>
							<tr>
								<td class="label">Nickname</td>
								<td class="value">{plant.nickname || 'N/A'}</td>
							</tr>
							<tr>
								<td class="label">Species</td>
								<td class="value">{plant.species || 'N/A'}</td>
							</tr>
							<tr>
								<td class="label">Added</td>
								<td class="value">{formatDate(plant.created_at)}</td>
							</tr>
						</tbody>
					</table>
				</section>

				<!-- Photo Histories Section -->
				<PhotoHistories plantId={plant.id} />
			</div>
		{/if}
	</div>
</main>

<style>
	.plant-detail {
		width: 100%;
		max-width: 1200px;
		margin: 0 auto;
	}

	.plant-detail .card {
		margin: 2rem 0;
		text-align: left;
	}

	.plant-detail .card h2 {
		color: #00ff00;
		margin-bottom: 1rem;
		font-size: 1.5rem;
	}

	.info-table {
		width: 100%;
		border-collapse: collapse;
	}

	.info-table tbody tr {
		border-bottom: 1px solid rgba(0, 255, 136, 0.3);
	}

	.info-table tbody tr:last-child {
		border-bottom: none;
	}

	.info-table .label {
		padding: 0.75rem 1rem;
		font-weight: bold;
		color: #00ff88;
		width: 30%;
		text-align: left;
	}

	.info-table .value {
		padding: 0.75rem 1rem;
		color: #00ff00;
	}

	.loading,
	.error {
		text-align: center;
		padding: 2rem;
		color: #00ff88;
		font-size: 1.2rem;
	}

	.error {
		color: #ff4444;
	}
</style>
