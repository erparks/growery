<script>
	import { onMount } from 'svelte';
	import { NoteService } from '$lib/services/noteService.js';
	import { pickMicrocopy } from '$lib/microcopy.js';
	import { formatTimeAgo } from '$lib/formatTimeAgo.js';

	let { plantId, onTimelineRefresh } = $props();

	let timelineItems = $state([]);
	let displayedCount = $state(5);
	let loading = $state(false);
	let enlargedImage = $state(null);

	let editingNoteId = $state(null);
	let editingContent = $state('');
	let editingDueDateLocal = $state('');
	let completingNoteId = $state(null);

	let sectionTitle = $state('Images & Notes');
	let timelineLoadingLine = $state('');
	let timelineEmptyLine = $state('');
	/** Skip notifying parent on the first timeline fetch (parent loads notes in parallel). */
	let timelineFetchCount = 0;
	const loadMore = () => {
		if (displayedCount >= timelineItems.length) return;
		displayedCount += 10;
	};

	/** Bottom sentinel for infinite scroll (when more items are buffered client-side) */
	let loadMoreSentinel = $state(null);

	$effect(() => {
		const el = loadMoreSentinel;
		if (!el || typeof IntersectionObserver === 'undefined') return;

		const observer = new IntersectionObserver(
			(entries) => {
				const entry = entries[0];
				if (!entry?.isIntersecting) return;
				requestAnimationFrame(() => loadMore());
			},
			{ root: null, rootMargin: '0px 0px 200px 0px', threshold: 0 }
		);

		observer.observe(el);
		return () => observer.disconnect();
	});

	const fetchTimeline = async () => {
		if (loading) return;
		try {
			loading = true;
			timelineItems = await NoteService.getTimeline(plantId);
		} catch (err) {
			console.error('Error fetching timeline:', err);
		} finally {
			loading = false;
			timelineFetchCount += 1;
			if (timelineFetchCount > 1) {
				onTimelineRefresh?.();
			}
		}
	};

	onMount(() => {
		const d = new Date();
		sectionTitle = pickMicrocopy('timelineSectionTitle', d);
		timelineLoadingLine = pickMicrocopy('timelineLoading', d);
		timelineEmptyLine = pickMicrocopy('timelineEmpty', d);
		fetchTimeline();
	});

	/** Called from plant detail after uploads so the grid refreshes */
	export async function refreshTimeline() {
		await fetchTimeline();
	}

	const displayedItems = $derived(timelineItems.slice(0, displayedCount));
	const hasMore = $derived(displayedCount < timelineItems.length);

	const timelinePhotoItems = $derived(timelineItems.filter((item) => item.kind === 'photo'));
	const enlargedPhotoIndex = $derived(
		enlargedImage
			? timelinePhotoItems.findIndex((item) => item.photo_history.id === enlargedImage.id)
			: -1
	);

	const goPrevPhoto = () => {
		const i = enlargedPhotoIndex;
		if (i <= 0) return;
		enlargedImage = timelinePhotoItems[i - 1].photo_history;
	};

	const goNextPhoto = () => {
		const i = enlargedPhotoIndex;
		if (i < 0 || i >= timelinePhotoItems.length - 1) return;
		enlargedImage = timelinePhotoItems[i + 1].photo_history;
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

	$effect(() => {
		if (!enlargedImage) return;
		const handler = (e) => {
			if (e.key === 'Escape') {
				closeEnlarged();
			} else if (e.key === 'ArrowLeft') {
				e.preventDefault();
				goPrevPhoto();
			} else if (e.key === 'ArrowRight') {
				e.preventDefault();
				goNextPhoto();
			}
		};
		window.addEventListener('keydown', handler);
		return () => {
			window.removeEventListener('keydown', handler);
		};
	});

	const toIsoOrNull = (datetimeLocalValue) => {
		if (!datetimeLocalValue) return null;
		const dt = new Date(datetimeLocalValue);
		if (Number.isNaN(dt.getTime())) return null;
		return dt.toISOString();
	};

	const createNoteForPhoto = async (photoHistoryId) => {
		const content = prompt('Add a note for this photo:');
		if (!content || !content.trim()) return;

		try {
			await NoteService.createNote(plantId, {
				content: content.trim(),
				photoHistoryId
			});
			await fetchTimeline();
		} catch (err) {
			console.error('Error creating note for photo:', err);
			alert('Failed to add note. Please try again.');
		}
	};

	const startEditingNote = (note) => {
		editingNoteId = note.id;
		editingContent = note.content || '';
		editingDueDateLocal = note.due_date ? new Date(note.due_date).toISOString().slice(0, 16) : '';
	};

	const cancelEditingNote = () => {
		editingNoteId = null;
		editingContent = '';
		editingDueDateLocal = '';
	};

	const saveNoteEdits = async (noteId) => {
		try {
			const dueDate = toIsoOrNull(editingDueDateLocal);
			await NoteService.updateNote(plantId, noteId, {
				content: editingContent,
				dueDate,
				clearDueDate: !dueDate
			});
			cancelEditingNote();
			await fetchTimeline();
		} catch (err) {
			console.error('Error updating note:', err);
			alert('Failed to update note. Please try again.');
		}
	};

	const deleteNote = async (noteId) => {
		if (!confirm('Delete this note? The associated photo (if any) will remain.')) return;
		try {
			await NoteService.deleteNote(plantId, noteId);
			await fetchTimeline();
		} catch (err) {
			console.error('Error deleting note:', err);
			alert('Failed to delete note. Please try again.');
		}
	};

	const completeNote = async (noteId) => {
		if (completingNoteId) return;
		completingNoteId = noteId;
		try {
			await NoteService.completeNote(plantId, noteId);
			await fetchTimeline();
		} catch (err) {
			console.error('Error completing note:', err);
			alert('Failed to mark note complete. Please try again.');
		} finally {
			completingNoteId = null;
		}
	};

	const toggleNoteCompleted = async (note) => {
		if (!note?.id) return;
		if (completingNoteId) return;
		completingNoteId = note.id;
		try {
			if (note.completed_at) {
				await NoteService.uncompleteNote(plantId, note.id);
			} else {
				await NoteService.completeNote(plantId, note.id);
			}
			await fetchTimeline();
		} catch (err) {
			console.error('Error toggling note completion:', err);
			alert('Failed to update completion. Please try again.');
		} finally {
			completingNoteId = null;
		}
	};

	const deletePhoto = async (photoId) => {
		if (!confirm('Are you sure you want to delete this photo? This action cannot be undone.')) {
			return;
		}

		try {
			const response = await fetch(`/api/plants/${plantId}/photo_histories/${photoId}`, {
				method: 'DELETE'
			});

			if (response.ok) {
				// Refresh timeline (notes may become standalone if they were attached)
				await fetchTimeline();
			} else {
				console.error('Failed to delete photo');
				alert('Failed to delete photo. Please try again.');
			}
		} catch (err) {
			console.error('Error deleting photo:', err);
			alert('An error occurred while deleting the photo.');
		}
	};
</script>

<section class="photo-timeline" aria-label="Photos and notes">
	<h2 class="timeline-heading">{sectionTitle}</h2>
	{#if loading && timelineItems.length === 0}
		<p class="no-photos">{timelineLoadingLine || 'Loading timeline...'}</p>
	{:else if timelineItems.length === 0}
		<p class="no-photos">{timelineEmptyLine || 'No images or notes yet for this plant.'}</p>
	{:else}
		<div class="photos-grid">
			{#each displayedItems as item}
							{#if item.kind === 'photo'}
								<div
									class="photo-item"
									class:wide={item.notes && item.notes.some((n) => (n.content || '').length > 180)}
									role="button"
									tabindex="0"
									onclick={() => openEnlarged(item.photo_history)}
									onkeydown={(e) => {
										if (e.key === 'Enter' || e.key === ' ') {
											e.preventDefault();
											openEnlarged(item.photo_history);
										}
									}}
								>
									<button
										class="delete-btn"
										onclick={(e) => {
											e.stopPropagation();
											deletePhoto(item.photo_history.id);
										}}
										aria-label="Delete photo"
										title="Delete photo"
									>
										<svg
											xmlns="http://www.w3.org/2000/svg"
											width="16"
											height="16"
											fill="currentColor"
											viewBox="0 0 16 16"
										>
											<path
												d="M5.5 5.5A.5.5 0 0 1 6 6v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm2.5 0a.5.5 0 0 1 .5.5v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm3 .5a.5.5 0 0 0-1 0v6a.5.5 0 0 0 1 0V6z"
											/>
											<path
												fill-rule="evenodd"
												d="M14.5 3a1 1 0 0 1-1 1H13v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V4h-.5a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1H6a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1h3.5a1 1 0 0 1 1 1v1zM4.118 4 4 4.059V13a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1V4.059L11.882 4H4.118zM2.5 3V2h11v1h-11z"
											/>
										</svg>
									</button>
									<img
										src={getImageUrl(item.photo_history)}
										alt="Plant photo from {formatTimeAgo(item.photo_history.created_at)}"
										loading="lazy"
										class="clickable-image"
									/>
									<div class="photo-meta">
										<div class="meta-row">
											<span class="photo-date">{formatTimeAgo(item.photo_history.created_at)}</span>
											<button
												class="small-btn"
												onclick={(e) => {
													e.stopPropagation();
													createNoteForPhoto(item.photo_history.id);
												}}
											>
												Add note
											</button>
										</div>
										{#if item.notes && item.notes.length > 0}
											<div class="notes-list">
												{#each item.notes as note}
													<div class="note-chip">
														{#if editingNoteId === note.id}
															<div
																class="note-edit"
																onclick={(e) => e.stopPropagation()}
																onkeydown={(e) => e.stopPropagation()}
															>
																<textarea
																	class="note-textarea"
																	bind:value={editingContent}
																	rows="3"
																	onclick={(e) => e.stopPropagation()}
																	onkeydown={(e) => e.stopPropagation()}
																></textarea>
																<div class="note-row" onclick={(e) => e.stopPropagation()}>
																	<input
																		class="note-input"
																		type="datetime-local"
																		bind:value={editingDueDateLocal}
																		onclick={(e) => e.stopPropagation()}
																		onkeydown={(e) => e.stopPropagation()}
																	/>
																	<div class="note-actions">
																		<button
																			class="small-btn"
																			onclick={(e) => {
																				e.stopPropagation();
																				saveNoteEdits(note.id);
																			}}
																		>
																			Save
																		</button>
																		<button
																			class="small-btn danger"
																			onclick={(e) => {
																				e.stopPropagation();
																				cancelEditingNote();
																			}}
																		>
																			Cancel
																		</button>
																	</div>
																</div>
															</div>
														{:else}
															<div class="note-view" class:completed={!!note.completed_at}>
																<div class="note-content">{note.content}</div>
																<div class="note-sub">
																	<div class="note-line note-time">
																		Created: {formatTimeAgo(note.created_at)}
																	</div>
																	{#if note.due_date}
																		<div class="note-line note-due">Due: {formatTimeAgo(note.due_date)}</div>
																	{/if}
																	{#if note.completed_at}
																		<div class="note-line note-completed">
																			Completed: {formatTimeAgo(note.completed_at)}
																		</div>
																	{/if}
																</div>
																<div class="note-actions">
																	{#if note.due_date}
																		<button
																			class="small-btn check-btn"
																			disabled={completingNoteId === note.id}
																			aria-label={note.completed_at ? 'Mark note incomplete' : 'Mark note complete'}
																			title={note.completed_at ? 'Undo complete' : 'Mark complete'}
																			onclick={(e) => {
																				e.stopPropagation();
																				toggleNoteCompleted(note);
																			}}
																		>
																			{#if note.completed_at}
																				<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true">
																					<path
																						fill="currentColor"
																						d="M19 3H5a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V5a2 2 0 0 0-2-2Zm-8 14-4-4 1.4-1.4L11 14.2l6.6-6.6L19 9l-8 8Z"
																					/>
																				</svg>
																			{:else}
																				Complete
																			{/if}
																		</button>
																	{/if}
																	<button
																		class="small-btn"
																		onclick={(e) => {
																			e.stopPropagation();
																			startEditingNote(note);
																		}}
																	>
																		Edit
																	</button>
																	<button
																		class="small-btn danger"
																		onclick={(e) => {
																			e.stopPropagation();
																			deleteNote(note.id);
																		}}
																	>
																		Delete
																	</button>
																</div>
															</div>
														{/if}
													</div>
												{/each}
											</div>
										{/if}
									</div>
								</div>
							{:else if item.kind === 'note'}
								<div class="note-item">
									<div class="note-item-header">
										<span class="photo-date">Note</span>
										<div class="note-actions">
											{#if item.note.due_date}
												<button
													class="small-btn check-btn"
													disabled={completingNoteId === item.note.id}
													aria-label={item.note.completed_at ? 'Mark note incomplete' : 'Mark note complete'}
													title={item.note.completed_at ? 'Undo complete' : 'Mark complete'}
													onclick={() => toggleNoteCompleted(item.note)}
												>
													{#if item.note.completed_at}
														<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true">
															<path
																fill="currentColor"
																d="M19 3H5a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V5a2 2 0 0 0-2-2Zm-8 14-4-4 1.4-1.4L11 14.2l6.6-6.6L19 9l-8 8Z"
															/>
														</svg>
													{:else}
														Complete
													{/if}
												</button>
											{/if}
											<button class="small-btn" onclick={() => startEditingNote(item.note)}
												>Edit</button
											>
											<button class="small-btn danger" onclick={() => deleteNote(item.note.id)}
												>Delete</button
											>
										</div>
									</div>
									{#if editingNoteId === item.note.id}
										<textarea class="note-textarea" bind:value={editingContent} rows="4"></textarea>
										<div class="note-row">
											<input
												class="note-input"
												type="datetime-local"
												bind:value={editingDueDateLocal}
											/>
											<div class="note-actions">
												<button class="small-btn" onclick={() => saveNoteEdits(item.note.id)}
													>Save</button
												>
												<button class="small-btn danger" onclick={cancelEditingNote}>Cancel</button>
											</div>
										</div>
									{:else}
										<div class="note-content" class:completed={!!item.note.completed_at}>
											{item.note.content}
										</div>
										<div class="note-sub">
											<div class="note-line note-time">
												Created: {formatTimeAgo(item.note.created_at)}
											</div>
											{#if item.note.due_date}
												<div class="note-line note-due">Due: {formatTimeAgo(item.note.due_date)}</div>
											{/if}
											{#if item.note.completed_at}
												<div class="note-line note-completed">
													Completed: {formatTimeAgo(item.note.completed_at)}
												</div>
											{/if}
										</div>
									{/if}
								</div>
							{/if}
			{/each}
		</div>
		{#if hasMore}
			<div
				class="timeline-load-sentinel"
				bind:this={loadMoreSentinel}
				aria-hidden="true"
			></div>
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
		tabindex="-1"
	>
		<button
			type="button"
			class="modal-backdrop"
			aria-label="Close enlarged image"
			onclick={closeEnlarged}
		></button>
		<div class="modal-content" role="document">
			<div class="modal-image-wrap">
				{#if enlargedPhotoIndex > 0}
					<button
						type="button"
						class="modal-nav-btn modal-nav-prev"
						onclick={(e) => {
							e.stopPropagation();
							goPrevPhoto();
						}}
						aria-label="Previous image"
					>
						<svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true">
							<path
								fill="currentColor"
								d="M15.41 7.41 14 6l-6 6 6 6 1.41-1.41L10.83 12z"
							/>
						</svg>
					</button>
				{/if}
				{#if enlargedPhotoIndex >= 0 && enlargedPhotoIndex < timelinePhotoItems.length - 1}
					<button
						type="button"
						class="modal-nav-btn modal-nav-next"
						onclick={(e) => {
							e.stopPropagation();
							goNextPhoto();
						}}
						aria-label="Next image"
					>
						<svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true">
							<path
								fill="currentColor"
								d="M10 6 8.59 7.41 13.17 12l-4.58 4.59L10 18l6-6z"
							/>
						</svg>
					</button>
				{/if}
				<button class="close-button" onclick={closeEnlarged} aria-label="Close enlarged image"
					>×</button
				>
				<img
					src={getImageUrl(enlargedImage)}
					alt="Plant photo from {formatTimeAgo(enlargedImage.created_at)}"
					class="enlarged-image"
				/>
			</div>
			<div class="modal-meta">
				<span class="modal-date">{formatTimeAgo(enlargedImage.created_at)}</span>
			</div>
		</div>
	</div>
{/if}

<style>
	/* No panel behind header/grid — cards sit on the page sky gradient */
	.photo-timeline {
		margin: 0.5rem 0 1rem;
		padding: 0;
		text-align: left;
		background: transparent;
		border: none;
		box-shadow: none;
		backdrop-filter: none;
	}

	.timeline-heading {
		color: var(--color-heading);
		margin: 0 0 0.75rem;
		font-size: 1.5rem;
		font-weight: 600;
		letter-spacing: 0.02em;
	}

	.photos-grid {
		display: grid;
		width: 100%;
		/* Match plant detail meta row: equal columns that grow to fill the section width */
		grid-template-columns: repeat(auto-fit, minmax(min(280px, 100%), 1fr));
		gap: 1rem;
		margin-top: 0.25rem;
	}

	@media (min-width: 768px) {
		.photos-grid {
			gap: 1.25rem;
		}
	}

	.photo-item {
		position: relative;
		display: flex;
		flex-direction: column;
		width: 100%;
		max-width: 100%;
		justify-self: stretch;
		border: 1px solid var(--color-border);
		border-radius: var(--radius-md);
		overflow: hidden;
		background-color: var(--color-surface-solid);
		transition:
			transform 0.2s ease,
			box-shadow 1.5s ease,
			border-color 0.2s ease;
		cursor: pointer;
		outline: none;
	}

	.photo-item:hover,
	.photo-item:focus {
		transform: translateY(-3px);
		box-shadow: var(--shadow-card);
		border-color: var(--color-border-strong);
	}

	.photo-item:focus-visible {
		outline: 2px solid var(--color-accent);
		outline-offset: 2px;
	}

	.delete-btn {
		position: absolute;
		top: 8px;
		right: 8px;
		background: rgba(18, 26, 22, 0.78);
		border: 1px solid var(--color-border);
		color: var(--color-danger);
		width: 32px;
		height: 32px;
		border-radius: 50%;
		display: flex;
		align-items: center;
		justify-content: center;
		cursor: pointer;
		opacity: 0;
		transition:
			opacity 0.2s,
			background 0.2s,
			transform 0.2s;
		z-index: 10;
	}

	.photo-item:hover .delete-btn,
	.delete-btn:focus {
		opacity: 1;
	}

	.delete-btn:hover {
		background: var(--color-surface-raised);
		transform: scale(1.05);
		color: var(--color-danger);
	}

	@media (hover: none) or (max-width: 768px) {
		.delete-btn {
			opacity: 1;
		}
	}

	/* Natural aspect ratio: width follows column, height from image intrinsic ratio */
	.photo-item img {
		width: 100%;
		height: auto;
		display: block;
		background: var(--color-bg);
	}

	/* Long attached notes: span full row width of the grid */
	.photo-item.wide {
		grid-column: 1 / -1;
		width: 100%;
		max-width: min(100%, 952px);
		justify-self: center;
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
		background-color: var(--color-surface-raised);
		width: 100%;
		box-sizing: border-box;
	}

	.meta-row {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 0.5rem;
	}

	.small-btn {
		background-color: var(--color-accent-soft);
		border: 1px solid var(--color-border-strong);
		color: var(--color-heading);
		padding: 0.25rem 0.5rem;
		border-radius: var(--radius-sm);
		font-size: 0.8rem;
		cursor: pointer;
		font-family: inherit;
	}

	.small-btn:hover {
		background-color: rgba(163, 201, 176, 0.3);
		border-color: var(--color-accent);
	}

	.small-btn:disabled {
		opacity: 0.6;
		cursor: not-allowed;
	}

	.small-btn.danger {
		border-color: rgba(192, 128, 128, 0.45);
		color: var(--color-danger);
		background-color: var(--color-danger-soft);
	}

	.small-btn.check-btn {
		display: inline-flex;
		align-items: center;
		justify-content: center;
	}

	.note-view.completed .note-content,
	.note-content.completed {
		text-decoration: line-through;
		opacity: 0.75;
	}

	.note-completed {
		color: var(--color-accent);
	}

	.notes-list {
		margin-top: 0.75rem;
		display: flex;
		flex-direction: column;
		gap: 0.75rem;
	}

	.note-chip {
		border: 1px solid var(--color-border);
		border-radius: var(--radius-md);
		padding: 0.5rem;
		background: var(--color-surface-solid);
		width: 100%;
		box-sizing: border-box;
	}

	.note-view {
		display: flex;
		flex-direction: column;
		gap: 0.35rem;
	}

	.note-content {
		color: var(--color-text);
		white-space: pre-wrap;
		word-break: break-word;
		font-size: 0.9rem;
	}

	.note-sub {
		display: flex;
		flex-direction: column;
		gap: 0.25rem;
		color: var(--color-text-muted);
		font-size: 0.8rem;
	}

	.note-line {
		line-height: 1.2;
	}

	.note-actions {
		display: flex;
		gap: 0.5rem;
		flex-wrap: wrap;
	}

	.note-edit {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
		width: 100%;
		max-width: 100%;
	}

	.note-item {
		border: 1px solid var(--color-border);
		border-radius: var(--radius-md);
		background-color: var(--color-surface-solid);
		padding: 0.75rem;
		display: flex;
		flex-direction: column;
		gap: 0.75rem;
	}

	.note-item-header {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 0.75rem;
	}

	.note-row {
		margin-top: 0.75rem;
		display: flex;
		gap: 1rem;
		align-items: flex-end;
		flex-wrap: wrap;
		width: 100%;
		max-width: 100%;
	}

	.note-input,
	.note-textarea {
		background-color: var(--color-surface-solid);
		border: 1px solid var(--color-border);
		border-radius: var(--radius-md);
		color: var(--color-text);
		padding: 0.5rem 0.75rem;
		font-family: inherit;
		box-sizing: border-box;
		max-width: 100%;
	}

	.note-input:focus,
	.note-textarea:focus {
		outline: none;
		border-color: var(--color-accent);
		box-shadow: var(--focus-ring);
	}

	.note-textarea {
		width: 100%;
		resize: vertical;
	}

	.note-input {
		width: 100%;
		min-width: 0;
		flex: 1 1 308px;
	}

	.photo-date {
		font-size: 0.875rem;
		color: var(--color-text-muted);
	}

	.no-photos {
		color: var(--color-text-muted);
		text-align: center;
		padding: 1.25rem 1rem;
		font-style: italic;
	}

	/* Triggers IntersectionObserver when scrolled near bottom */
	.timeline-load-sentinel {
		width: 100%;
		height: 1px;
		margin-top: 0.5rem;
		pointer-events: none;
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
		background-color: rgba(12, 18, 16, 0.9);
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
		z-index: 2;
	}

	.modal-image-wrap {
		position: relative;
		display: inline-block;
		max-width: 100%;
		line-height: 0;
	}

	.modal-backdrop {
		position: absolute;
		inset: 0;
		background: transparent;
		border: none;
		padding: 0;
		margin: 0;
		cursor: pointer;
		z-index: 1;
	}

	.modal-nav-btn {
		position: absolute;
		top: 50%;
		transform: translateY(-50%);
		z-index: 4;
		width: 44px;
		height: 44px;
		padding: 0;
		display: flex;
		align-items: center;
		justify-content: center;
		border-radius: 50%;
		border: 1px solid var(--color-border-strong);
		background: rgba(18, 26, 22, 0.85);
		color: var(--color-heading);
		cursor: pointer;
		transition:
			background 0.2s ease,
			border-color 0.2s ease,
			transform 0.2s ease;
		font-family: inherit;
		box-shadow: var(--shadow-soft);
	}

	.modal-nav-btn:hover {
		background: var(--color-surface-raised);
		border-color: var(--color-accent);
	}

	.modal-nav-prev {
		left: 0.5rem;
	}

	.modal-nav-next {
		right: 0.5rem;
	}

	.close-button {
		position: absolute;
		top: 0.5rem;
		right: 0.5rem;
		z-index: 5;
		background: var(--color-surface-solid);
		border: 1px solid var(--color-border-strong);
		color: var(--color-text-muted);
		font-size: 1.75rem;
		width: 40px;
		height: 40px;
		border-radius: 50%;
		cursor: pointer;
		display: flex;
		align-items: center;
		justify-content: center;
		transition: all 0.2s ease;
		font-family: inherit;
		line-height: 1;
		padding: 0;
	}

	.close-button:hover {
		background: var(--color-surface-raised);
		border-color: var(--color-accent);
		color: var(--color-heading);
		transform: scale(1.05);
	}

	.enlarged-image {
		max-width: 100%;
		max-height: 85vh;
		object-fit: contain;
		border-radius: var(--radius-md);
		box-shadow: var(--shadow-soft);
		transition: box-shadow 1.5s ease;
	}

	.modal-meta {
		margin-top: 1rem;
		padding: 0.75rem;
		background-color: var(--color-surface-solid);
		border-radius: var(--radius-md);
		border: 1px solid var(--color-border);
	}

	.modal-date {
		font-size: 1rem;
		color: var(--color-text-muted);
	}
</style>
