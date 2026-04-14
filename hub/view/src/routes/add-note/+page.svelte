<script>
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';
	import { NoteService } from '$lib/services/noteService.js';
	import { pickMicrocopy } from '$lib/microcopy.js';

	let plantId = null;
	let plant = null;
	let loadingPlant = false;

	let content = '';
	let dueDateLocal = '';
	let imageFile = null;
	let submitting = false;
	let error = '';
	let addNoteSubtitle = $state('');

	const toIsoOrNull = (datetimeLocalValue) => {
		if (!datetimeLocalValue) return null;
		const dt = new Date(datetimeLocalValue);
		if (Number.isNaN(dt.getTime())) return null;
		return dt.toISOString();
	};

	const backToPlant = () => {
		if (plantId) goto(`/plant_detail?plant_id=${plantId}`);
		else goto('/');
	};

	const loadPlant = async () => {
		if (!plantId) return;
		loadingPlant = true;
		try {
			const resp = await fetch(`/api/plants/${plantId}`);
			if (resp.ok) {
				plant = await resp.json();
			}
		} catch (e) {
			// Non-fatal; page still works without plant metadata
		} finally {
			loadingPlant = false;
			if (plantId) {
				const nick = plant?.nickname?.trim() || `Plant #${plantId}`;
				addNoteSubtitle = pickMicrocopy('addNoteSubtitle', new Date(), { nickname: nick });
			}
		}
	};

	onMount(() => {
		plantId = $page.url.searchParams.get('plant_id');
		loadPlant();
	});

	const handleImageChange = (e) => {
		const file = e.target.files?.[0] || null;
		imageFile = file;
	};

	const handleSubmit = async (e) => {
		e.preventDefault();
		error = '';

		if (!plantId) {
			error = 'No plant selected.';
			return;
		}
		if (!content.trim()) {
			error = 'Please enter a note.';
			return;
		}

		submitting = true;
		try {
			const dueDate = toIsoOrNull(dueDateLocal);
			if (imageFile) {
				await NoteService.createNoteWithImage(plantId, {
					content: content.trim(),
					dueDate,
					imageFile
				});
			} else {
				await NoteService.createNote(plantId, {
					content: content.trim(),
					dueDate
				});
			}
			backToPlant();
		} catch (err) {
			error = err.message || 'Failed to create note.';
		} finally {
			submitting = false;
		}
	};
</script>

<main>
	<div class="container column">
		<div class="app-brand-header">
			<a href="/" class="app-title app-title--streetlight">growery</a>
		</div>
		<div class="container">
			<h1 class="form-page-title">
				{#if loadingPlant}
					Add Note
				{:else if plant?.nickname}
					{plant.nickname}
				{:else if plantId}
					Plant #{plantId}
				{:else}
					Add Note
				{/if}
			</h1>
			{#if !loadingPlant && plantId && addNoteSubtitle}
				<p class="microcopy microcopy-muted form-page-subtitle">{addNoteSubtitle}</p>
			{/if}
		</div>

		<div class="form-container">
			<form on:submit={handleSubmit}>
				<div class="form-group">
					<label class="form-label" for="dueDate">Due (Optional)</label>
					<input
						class="form-field"
						id="dueDate"
						type="datetime-local"
						bind:value={dueDateLocal}
						disabled={submitting}
					/>
				</div>

				<div class="form-group">
					<label class="form-label" for="image">Image (Optional)</label>
					<input
						class="form-field form-file-button"
						id="image"
						type="file"
						accept="image/*"
						on:change={handleImageChange}
						disabled={submitting}
					/>
					<div class="file-hint">Optional: attach a photo to this note</div>
				</div>

				<div class="form-group">
					<label class="form-label" for="content">Note</label>
					<textarea
						class="form-field"
						id="content"
						bind:value={content}
						required
						rows="6"
						placeholder="What did you notice? What did you do? Any changes?"
						disabled={submitting}
					></textarea>
				</div>

				{#if error}
					<div class="form-error">{error}</div>
				{/if}

				<div class="form-actions">
					<button type="button" class="btn btn-ghost" on:click={backToPlant} disabled={submitting}>
						Cancel
					</button>
					<button type="submit" class="btn btn-primary" disabled={submitting || !content.trim()}>
						{submitting ? 'Saving...' : 'Save Note'}
					</button>
				</div>
			</form>
		</div>
	</div>
</main>

<style>
	.form-container {
		max-width: 600px;
		width: 100%;
		margin: 2rem auto;
	}

	form {
		display: flex;
		flex-direction: column;
		gap: 1.5rem;
	}

	.form-group {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}

	textarea {
		resize: vertical;
		min-height: 140px;
	}

	input[type='file'] {
		cursor: pointer;
		padding: 0.5rem;
	}

	.file-hint {
		font-size: 0.8rem;
		color: var(--color-text-muted);
		margin-top: 0.25rem;
	}

	.form-actions {
		display: flex;
		gap: 1rem;
		justify-content: flex-end;
		margin-top: 1rem;
		flex-wrap: wrap;
	}
</style>


