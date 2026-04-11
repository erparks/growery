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
		<div class="container">
			<a href="/" class="app-title">growery</a>
		</div>

		{#if loading}
			<div class="loading">Loading plant data...</div>
		{:else if error}
			<div class="error">{error}</div>
		{:else if plant}
			<div class="plant-detail">
				<!-- Plant Information Table -->
				<section class="card">
					<h2>{plant.nickname}</h2>
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
		color: var(--color-heading);
		margin-bottom: 1rem;
		font-size: 1.5rem;
		font-weight: 600;
		letter-spacing: 0.02em;
	}

	.info-table {
		width: 100%;
		border-collapse: collapse;
	}

	.info-table tbody tr {
		border-bottom: 1px solid var(--color-border);
	}

	.info-table tbody tr:last-child {
		border-bottom: none;
	}

	.info-table .label {
		padding: 0.75rem 1rem 0.75rem 0;
		font-weight: 500;
		color: var(--color-text-muted);
		width: 30%;
		text-align: left;
		vertical-align: top;
	}

	.info-table .value {
		padding: 0.75rem 0;
		color: var(--color-text);
	}

	.loading,
	.error {
		text-align: center;
		padding: 2rem;
		color: var(--color-text-muted);
		font-size: 1.1rem;
	}

	.error {
		color: var(--color-danger);
	}

</style>
