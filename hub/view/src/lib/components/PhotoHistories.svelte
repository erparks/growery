<script>
	import { onMount } from 'svelte';

	let { plantId } = $props();

	let allPhotoHistories = $state([]);
	let displayedCount = $state(5);
	let loading = $state(false);
	let groupPhotosByDate = $state([]);
	let enlargedImage = $state(null);
	let uploading = $state(false);
	let uploadProgress = $state('');
	let fileInput = null;

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

	const openEnlarged = (photoHistory) => {
		enlargedImage = photoHistory;
		// Prevent body scroll when modal is open
		document.body.style.overflow = 'hidden';
	};

	const closeEnlarged = () => {
		enlargedImage = null;
		// Restore body scroll
		document.body.style.overflow = '';
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

	const handleFileSelect = async (event) => {
		const files = Array.from(event.target.files || []);
		if (files.length === 0) return;

		uploading = true;
		uploadProgress = '';

		try {
			for (let i = 0; i < files.length; i++) {
				const file = files[i];
				uploadProgress = `Uploading ${i + 1} of ${files.length}: ${file.name}`;

				const formData = new FormData();
				formData.append('image', file);

				const response = await fetch(`/api/plants/${plantId}/photo_histories`, {
					method: 'POST',
					body: formData
				});

				if (!response.ok) {
					const error = await response.json();
					throw new Error(error.error || `Failed to upload ${file.name}`);
				}
			}

			uploadProgress = 'Upload complete!';

			// Refresh the photo list
			await fetchAllPhotos();

			// Clear the file input
			if (fileInput) {
				fileInput.value = '';
			}

			// Clear progress message after a short delay
			setTimeout(() => {
				uploadProgress = '';
			}, 2000);
		} catch (error) {
			uploadProgress = `Error: ${error.message}`;
			console.error('Upload error:', error);
		} finally {
			uploading = false;
		}
	};

	const triggerFileInput = () => {
		if (fileInput) {
			fileInput.click();
		}
	};
</script>

<section class="card">
	<div class="card-header">
		<h2>Images</h2>
		<button class="upload-btn" onclick={triggerFileInput} disabled={uploading}>
			{uploading ? 'Uploading...' : 'Upload Images'}
		</button>
		<input
			type="file"
			accept="image/*"
			multiple
			bind:this={fileInput}
			onchange={handleFileSelect}
			style="display: none;"
		/>
	</div>
	{#if uploadProgress}
		<div class="upload-progress">{uploadProgress}</div>
	{/if}
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
							<div
								class="photo-item"
								role="button"
								tabindex="0"
								onclick={() => openEnlarged(photoHistory)}
								onkeydown={(e) => {
									if (e.key === 'Enter' || e.key === ' ') {
										e.preventDefault();
										openEnlarged(photoHistory);
									}
								}}
							>
								<img
									src={getImageUrl(photoHistory)}
									alt="Plant photo from {formatDate(photoHistory.created_at)}"
									loading="lazy"
									class="clickable-image"
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

<!-- Enlarged Image Modal -->
{#if enlargedImage}
	<div
		class="image-modal"
		role="dialog"
		aria-modal="true"
		aria-label="Enlarged image view"
		onclick={closeEnlarged}
		onkeydown={(e) => {
			if (e.key === 'Escape') {
				closeEnlarged();
			}
		}}
		tabindex="-1"
	>
		<div
			class="modal-content"
			role="document"
			onclick={(e) => e.stopPropagation()}
			onkeydown={(e) => e.stopPropagation()}
		>
			<button class="close-button" onclick={closeEnlarged} aria-label="Close enlarged image"
				>×</button
			>
			<img
				src={getImageUrl(enlargedImage)}
				alt="Plant photo from {formatDate(enlargedImage.created_at)}"
				class="enlarged-image"
			/>
			<div class="modal-meta">
				<span class="modal-date">{formatDate(enlargedImage.created_at)}</span>
			</div>
		</div>
	</div>
{/if}

<style>
	.card {
		margin: 2rem 0;
		text-align: left;
	}

	.card-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 1rem;
		gap: 1rem;
		flex-wrap: wrap;
	}

	.card h2 {
		color: #00ff00;
		margin: 0;
		font-size: 1.5rem;
	}

	.upload-btn {
		background-color: rgba(0, 255, 136, 0.2);
		border: 1px solid rgba(0, 255, 136, 0.5);
		color: #00ff88;
		padding: 0.5rem 1.5rem;
		border-radius: 8px;
		font-size: 0.9rem;
		cursor: pointer;
		transition:
			background-color 0.2s ease,
			border-color 0.2s ease,
			transform 0.2s ease;
		font-family: inherit;
	}

	.upload-btn:hover:not(:disabled) {
		background-color: rgba(0, 255, 136, 0.3);
		border-color: rgba(0, 255, 136, 0.7);
		transform: translateY(-2px);
	}

	.upload-btn:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	.upload-progress {
		padding: 0.75rem 1rem;
		background-color: rgba(0, 255, 136, 0.1);
		border: 1px solid rgba(0, 255, 136, 0.3);
		border-radius: 8px;
		color: #00ff88;
		margin-bottom: 1rem;
		font-size: 0.9rem;
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
		cursor: pointer;
		outline: none;
	}

	.photo-item:hover,
	.photo-item:focus {
		transform: translateY(-4px);
		box-shadow: 0 4px 12px rgba(0, 255, 136, 0.4);
	}

	.photo-item:focus-visible {
		outline: 2px solid #00ff88;
		outline-offset: 2px;
	}

	.photo-item img {
		width: 100%;
		height: 200px;
		object-fit: cover;
		display: block;
	}

	.clickable-image {
		cursor: pointer;
		transition: opacity 0.2s ease;
	}

	.clickable-image:hover {
		opacity: 0.9;
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

	.image-modal {
		position: fixed;
		top: 0;
		left: 0;
		right: 0;
		bottom: 0;
		background-color: rgba(0, 0, 0, 0.9);
		display: flex;
		align-items: center;
		justify-content: center;
		z-index: 1000;
		padding: 2rem;
		cursor: pointer;
	}

	.modal-content {
		position: relative;
		max-width: 90vw;
		max-height: 90vh;
		display: flex;
		flex-direction: column;
		align-items: center;
		cursor: default;
	}

	.close-button {
		position: absolute;
		top: -2.5rem;
		right: 0;
		background: rgba(0, 0, 0, 0.8);
		border: 2px solid rgba(0, 255, 136, 0.5);
		color: #00ff88;
		font-size: 2rem;
		width: 40px;
		height: 40px;
		border-radius: 50%;
		cursor: pointer;
		display: flex;
		align-items: center;
		justify-content: center;
		transition: all 0.2s ease;
		font-family: 'IBM Plex Mono', monospace;
		line-height: 1;
		padding: 0;
	}

	.close-button:hover {
		background: rgba(0, 255, 136, 0.2);
		border-color: #00ff88;
		transform: scale(1.1);
	}

	.enlarged-image {
		max-width: 100%;
		max-height: 85vh;
		object-fit: contain;
		border-radius: 8px;
		box-shadow: 0 4px 20px rgba(0, 255, 136, 0.3);
	}

	.modal-meta {
		margin-top: 1rem;
		padding: 0.75rem;
		background-color: rgba(0, 0, 0, 0.7);
		border-radius: 8px;
		border: 1px solid rgba(0, 255, 136, 0.3);
	}

	.modal-date {
		font-size: 1rem;
		color: #00ff88;
	}
</style>
