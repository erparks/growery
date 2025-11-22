<script>
	import { onMount } from 'svelte';

	let { plantId } = $props();

	let allPhotoHistories = $state([]);
	let displayedCount = $state(5);
	let loading = $state(false);
	let groupPhotosByDate = $state([]);

	const loadMore = () => {
		displayedCount += 10;
	};

	const fetchAllPhotos = async () => {
		if (loading) return;
		try {
			loading = true;
			const response = await fetch(`/api/plants/${plantId}/photo_histories`);
			if (response.ok) {
				allPhotoHistories = await response.json();
			}
		} catch (err) {
			console.error('Error fetching photo histories:', err);
		} finally {
			loading = false;
		}
	};

	onMount(() => {
		fetchAllPhotos();
	});

	const getDateKey = (dateString) => {
		if (!dateString) return '';
		const date = new Date(dateString);
		return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`;
	};

	const displayedPhotos = $derived(allPhotoHistories.slice(0, displayedCount));
	const hasMore = $derived(displayedCount < allPhotoHistories.length);

	$effect(() => {
		const groups = new Map();
		for (const photo of displayedPhotos) {
			const dateKey = getDateKey(photo.created_at);
			if (!groups.has(dateKey)) {
				groups.set(dateKey, []);
			}
			groups.get(dateKey).push(photo);
		}
		// Convert to array of { date, photos } objects, sorted by date (newest first)
		groupPhotosByDate = Array.from(groups.entries())
			.map(([dateKey, photos]) => ({
				date: photos[0].created_at, // Use the first photo's date for formatting
				photos
			}))
			.sort((a, b) => new Date(b.date) - new Date(a.date));
	});

	const formatDateHeader = (dateString) => {
		if (!dateString) return 'N/A';
		const date = new Date(dateString);

		const monthNames = [
			'January',
			'February',
			'March',
			'April',
			'May',
			'June',
			'July',
			'August',
			'September',
			'October',
			'November',
			'December'
		];
		return `${monthNames[date.getMonth()]} ${date.getDate()}, ${date.getFullYear()}`;
	};

	const getImageUrl = (photoHistory) => {
		return `/api/plants/${plantId}/photo_histories/${photoHistory.id}`;
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
</script>

<section class="card">
	<h2>Images</h2>
	{#if loading && allPhotoHistories.length === 0}
		<p class="no-photos">Loading photos...</p>
	{:else if allPhotoHistories.length === 0}
		<p class="no-photos">No photos available for this plant.</p>
	{:else}
		<div class="photos-container">
			{#each groupPhotosByDate as dateGroup}
				<div class="date-section">
					<div class="date-divider">
						<h3 class="date-header">{formatDateHeader(dateGroup.date)}</h3>
						<div class="divider-line"></div>
					</div>
					<div class="photos-grid">
						{#each dateGroup.photos as photoHistory}
							<div class="photo-item">
								<img
									src={getImageUrl(photoHistory)}
									alt="Plant photo from {formatDate(photoHistory.created_at)}"
									loading="lazy"
								/>
								<div class="photo-meta">
									<span class="photo-date">{formatDate(photoHistory.created_at)}</span>
								</div>
							</div>
						{/each}
					</div>
				</div>
			{/each}
		</div>
		{#if hasMore}
			<div class="show-more-container">
				<button class="show-more-btn" onclick={loadMore} disabled={loading}>
					{loading ? 'Loading...' : 'Show More'}
				</button>
			</div>
		{/if}
	{/if}
</section>

<style>
	.card {
		margin: 2rem 0;
		text-align: left;
	}

	.card h2 {
		color: #00ff00;
		margin-bottom: 1rem;
		font-size: 1.5rem;
	}

	.photos-container {
		display: flex;
		flex-direction: column;
		gap: 2rem;
		margin-top: 1rem;
	}

	.date-section {
		display: flex;
		flex-direction: column;
		gap: 1rem;
	}

	.date-divider {
		display: flex;
		align-items: center;
		gap: 1rem;
		margin-bottom: 0.5rem;
	}

	.date-header {
		color: #00ff88;
		font-size: 1.25rem;
		font-weight: 600;
		margin: 0;
		white-space: nowrap;
	}

	.divider-line {
		flex: 1;
		height: 1px;
		background: linear-gradient(to right, rgba(0, 255, 136, 0.5), rgba(0, 255, 136, 0.1));
	}

	.photos-grid {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
		gap: 1.5rem;
	}

	.photo-item {
		display: flex;
		flex-direction: column;
		border: 1px solid rgba(0, 255, 136, 0.3);
		border-radius: 8px;
		overflow: hidden;
		background-color: rgba(0, 0, 0, 0.3);
		transition:
			transform 0.2s ease,
			box-shadow 0.2s ease;
	}

	.photo-item:hover {
		transform: translateY(-4px);
		box-shadow: 0 4px 12px rgba(0, 255, 136, 0.4);
	}

	.photo-item img {
		width: 100%;
		height: 200px;
		object-fit: cover;
		display: block;
	}

	.photo-meta {
		padding: 0.75rem;
		background-color: rgba(0, 0, 0, 0.5);
	}

	.photo-date {
		font-size: 0.875rem;
		color: #00ff88;
	}

	.no-photos {
		color: #00ff88;
		text-align: center;
		padding: 2rem;
		font-style: italic;
	}

	.show-more-container {
		display: flex;
		justify-content: center;
		margin-top: 2rem;
	}

	.show-more-btn {
		background-color: rgba(0, 255, 136, 0.2);
		border: 1px solid rgba(0, 255, 136, 0.5);
		color: #00ff88;
		padding: 0.75rem 2rem;
		border-radius: 8px;
		font-size: 1rem;
		cursor: pointer;
		transition:
			background-color 0.2s ease,
			border-color 0.2s ease,
			transform 0.2s ease;
	}

	.show-more-btn:hover:not(:disabled) {
		background-color: rgba(0, 255, 136, 0.3);
		border-color: rgba(0, 255, 136, 0.7);
		transform: translateY(-2px);
	}

	.show-more-btn:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	@media (max-width: 600px) {
		.photos-grid {
			grid-template-columns: 1fr;
		}
	}
</style>
