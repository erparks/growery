<script>
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';
	import PhotoHistories from '$lib/components/PhotoHistories.svelte';
	import { pickMicrocopy, pickRandom } from '$lib/microcopy.js';
	import { formatTimeAgo } from '$lib/formatTimeAgo.js';

	const NO_NOTES_MESSAGES = [
		'No notes yet—add one when something’s worth remembering.',
		'The journal is quiet. Your first note could start a story.',
		'Nothing here yet. Tap Add note when something happens.',
		'Quiet on this page so far.',
		'No notes for this plant yet.',
		'Still waiting for the first note. When you’re ready, add one.',
		'Nothing written down yet. That can change in a moment.'
	];

	let plant = $state(null);
	let loading = $state(true);
	let error = $state(null);
	let plantLoadingLine = $state('');
	let plantSubtitle = $state('');
	let uploading = $state(false);
	let uploadProgress = $state('');
	let fileInput = $state(null);
	let timelineRef = $state(null);
	let plantNotes = $state([]);
	let notesLoading = $state(false);
	let emptyNotesLine = $state('');

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

			await fetchNotes(plantId);

			// Photo histories are now fetched by the PhotoHistories component itself
		} catch (err) {
			error = 'Failed to load plant data';
			console.error('Error fetching plant data:', err);
		} finally {
			loading = false;
		}
	};

	const formatDateShort = (dateString) => {
		if (!dateString) return '…';
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
		return `${monthNames[date.getMonth()]} ${date.getDate().toString().padStart(2, '0')}, ${date.getFullYear()}`;
	};

	$effect(() => {
		if (!plant?.created_at) {
			plantSubtitle = '';
			return;
		}
		const fd = formatDateShort(plant.created_at);
		plantSubtitle = `Since ${fd}.`;
	});

	const fetchNotes = async (plantId) => {
		if (!plantId) return;
		try {
			notesLoading = true;
			const res = await fetch(`/api/plants/${plantId}/notes`);
			if (!res.ok) {
				plantNotes = [];
				emptyNotesLine = pickRandom(NO_NOTES_MESSAGES);
				return;
			}
			const list = await res.json();
			plantNotes = [...list].sort(
				(a, b) => new Date(a.created_at) - new Date(b.created_at)
			);
			if (plantNotes.length === 0) {
				emptyNotesLine = pickRandom(NO_NOTES_MESSAGES);
			}
		} catch (err) {
			console.error('Error fetching notes:', err);
			plantNotes = [];
			emptyNotesLine = pickRandom(NO_NOTES_MESSAGES);
		} finally {
			notesLoading = false;
		}
	};

	const triggerFileInput = () => {
		fileInput?.click();
	};

	const handleFileSelect = async (event) => {
		const files = Array.from(event.target.files || []);
		if (files.length === 0 || !plant?.id) return;

		uploading = true;
		uploadProgress = '';

		try {
			for (let i = 0; i < files.length; i++) {
				const file = files[i];
				uploadProgress = `Uploading ${i + 1} of ${files.length}: ${file.name}`;

				const formData = new FormData();
				formData.append('image', file);

				const response = await fetch(`/api/plants/${plant.id}/photo_histories`, {
					method: 'POST',
					body: formData
				});

				if (!response.ok) {
					const errBody = await response.json();
					throw new Error(errBody.error || `Failed to upload ${file.name}`);
				}
			}

			uploadProgress = 'Upload complete!';
			await timelineRef?.refreshTimeline?.();
			if (fileInput) fileInput.value = '';
			setTimeout(() => {
				uploadProgress = '';
			}, 2000);
		} catch (err) {
			uploadProgress = `Error: ${err instanceof Error ? err.message : 'Upload failed'}`;
			console.error('Upload error:', err);
		} finally {
			uploading = false;
		}
	};

	onMount(() => {
		plantLoadingLine = pickMicrocopy('plantLoading', new Date());
		fetchPlantData();
	});
</script>

<main class="plant-detail-page">
	<div class="plant-detail-stack">
		<div class="app-brand-header">
			<a href="/" class="app-title app-title--streetlight">growery</a>
		</div>

		{#if loading}
			<div class="loading">{plantLoadingLine || 'Loading plant data...'}</div>
		{:else if error}
			<div class="error">{error}</div>
		{:else if plant}
			<div class="plant-detail">
				<div class="plant-detail-meta-row">
					<!-- Plant information -->
					<section class="card plant-info-card">
						<h2>{plant.nickname}</h2>
						{#if plantSubtitle}
							<p class="microcopy microcopy-muted plant-detail-subtitle">{plantSubtitle}</p>
						{/if}
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
									<td class="value">{formatTimeAgo(plant.created_at)}</td>
								</tr>
							</tbody>
						</table>
					</section>

					<!-- Notes preview + add note / upload images -->
					<section class="card plant-actions-card" aria-label="Notes and actions">
						<div class="plant-notes-preview">
							<h3 class="plant-notes-heading">Notes</h3>
							{#if notesLoading}
								<p class="plant-notes-status">Loading notes…</p>
							{:else if plantNotes.length === 0}
								<p class="plant-notes-empty">{emptyNotesLine}</p>
							{:else}
								<ul class="plant-notes-list">
									{#each plantNotes as note (note.id)}
										<li class="plant-note-item">
											<div class="plant-note-body">{note.content}</div>
											<div class="plant-note-meta">
												<span>{formatTimeAgo(note.created_at)}</span>
												{#if note.due_date}
													<span class="plant-note-due">Due: {formatTimeAgo(note.due_date)}</span>
												{/if}
												{#if note.completed_at}
													<span class="plant-note-done">Done: {formatTimeAgo(note.completed_at)}</span>
												{/if}
											</div>
										</li>
									{/each}
								</ul>
							{/if}
						</div>
						<div class="plant-actions-footer">
							<div class="plant-actions-row">
								<button
									type="button"
									class="plant-action-btn"
									onclick={() => goto(`/add-note?plant_id=${plant.id}`)}
								>
									Add note
								</button>
								<button
									type="button"
									class="plant-action-btn"
									onclick={triggerFileInput}
									disabled={uploading}
								>
									{uploading ? 'Uploading...' : 'Upload Image'}
								</button>
							</div>
							{#if uploadProgress}
								<p class="plant-upload-progress">{uploadProgress}</p>
							{/if}
							<input
								type="file"
								accept="image/*"
								multiple
								bind:this={fileInput}
								onchange={handleFileSelect}
								style="display: none;"
							/>
						</div>
					</section>
				</div>

				<!-- Photo Histories Section -->
				<PhotoHistories
					bind:this={timelineRef}
					plantId={plant.id}
					onTimelineRefresh={() => fetchNotes(plant.id)}
				/>
			</div>
		{/if}
	</div>
</main>

<style>
	.plant-detail-page {
		padding-top: 0;
	}

	.plant-detail-stack {
		display: flex;
		flex-direction: column;
		align-items: stretch;
		gap: 0.75rem;
		width: 100%;
	}

	.plant-detail {
		width: 100%;
		max-width: 56rem;
		margin: 0 auto;
	}

	/* Mobile: stack; tablet+: two columns — rows match tallest cell */
	.plant-detail-meta-row {
		display: grid;
		grid-template-columns: 1fr;
		gap: 1rem;
		width: 100%;
		margin-bottom: 1rem;
		align-items: stretch;
	}

	@media (min-width: 768px) {
		.plant-detail-meta-row {
			grid-template-columns: repeat(2, minmax(0, 1fr));
			gap: 1.25rem;
		}
	}

	.plant-detail .plant-detail-meta-row .card.plant-info-card,
	.plant-detail .plant-detail-meta-row .card.plant-actions-card {
		margin: 0;
		width: 100%;
		max-width: 28rem;
		justify-self: center;
		padding: 0.9rem 1rem 1rem;
		text-align: left;
		box-sizing: border-box;
		height: 100%;
		min-height: 12rem;
		align-self: stretch;
		display: flex;
		flex-direction: column;
	}

	@media (min-width: 768px) {
		.plant-detail .plant-detail-meta-row .card.plant-info-card,
		.plant-detail .plant-detail-meta-row .card.plant-actions-card {
			max-width: none;
			justify-self: stretch;
		}
	}

	.plant-detail .plant-info-card h2 {
		color: var(--color-heading);
		margin: 0 0 0.2rem;
		font-size: 1.35rem;
		font-weight: 600;
		letter-spacing: 0.02em;
	}

	.plant-notes-preview {
		flex: 1 1 auto;
		min-height: 0;
		display: flex;
		flex-direction: column;
		overflow: hidden;
	}

	.plant-notes-heading {
		margin: 0 0 0.5rem;
		font-size: 0.95rem;
		font-weight: 600;
		color: var(--color-heading);
		letter-spacing: 0.02em;
	}

	.plant-notes-status,
	.plant-notes-empty {
		margin: 0;
		font-size: 0.9rem;
		color: var(--color-text-muted);
		font-style: italic;
		line-height: 1.45;
	}

	.plant-notes-list {
		list-style: none;
		margin: 0;
		padding: 0;
		overflow-y: auto;
		flex: 1 1 auto;
		min-height: 0;
		display: flex;
		flex-direction: column;
		gap: 0.65rem;
	}

	.plant-note-item {
		padding: 0.5rem 0.65rem;
		background: var(--color-surface-solid);
		border: 1px solid var(--color-border);
		border-radius: var(--radius-md);
	}

	.plant-note-body {
		font-size: 0.9rem;
		color: var(--color-text);
		line-height: 1.45;
		white-space: pre-wrap;
		word-break: break-word;
	}

	.plant-note-meta {
		margin-top: 0.35rem;
		display: flex;
		flex-wrap: wrap;
		gap: 0.35rem 0.75rem;
		font-size: 0.78rem;
		color: var(--color-text-muted);
	}

	.plant-note-due {
		color: var(--color-accent);
	}

	.plant-note-done {
		color: var(--color-text-muted);
	}

	.plant-actions-footer {
		flex-shrink: 0;
		margin-top: auto;
		padding-top: 0.85rem;
		border-top: 1px solid var(--color-border);
	}

	.plant-actions-row {
		display: flex;
		flex-wrap: nowrap;
		align-items: stretch;
		gap: 0.65rem;
		width: 100%;
	}

	.plant-action-btn {
		flex: 1 1 0;
		min-width: 0;
		text-align: center;
		background-color: var(--color-accent-soft);
		border: 1px solid var(--color-border-strong);
		color: var(--color-heading);
		padding: 0.5rem 0.75rem;
		border-radius: var(--radius-md);
		font-size: 0.875rem;
		cursor: pointer;
		transition:
			background-color 0.2s ease,
			border-color 0.2s ease,
			transform 0.2s ease;
		font-family: inherit;
	}

	.plant-action-btn:hover:not(:disabled) {
		background-color: rgba(163, 201, 176, 0.3);
		border-color: var(--color-accent);
		transform: translateY(-1px);
	}

	.plant-action-btn:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	.plant-upload-progress {
		margin: 0.5rem 0 0;
		font-size: 0.9rem;
		color: var(--color-text-muted);
	}

	.plant-detail .plant-detail-subtitle {
		margin: 0 0 0.65rem;
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
		padding: 0.45rem 0.75rem 0.45rem 0;
		font-weight: 500;
		color: var(--color-text-muted);
		width: 32%;
		text-align: left;
		vertical-align: top;
	}

	.info-table .value {
		padding: 0.45rem 0;
		color: var(--color-text);
	}

	.loading,
	.error {
		text-align: center;
		padding: 1.25rem;
		color: var(--color-text-muted);
		font-size: 1.05rem;
	}

	.error {
		color: var(--color-danger);
	}

</style>
