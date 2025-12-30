<script>
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';
	import { NoteService } from '$lib/services/noteService.js';

	let plantId = null;
	let plant = null;
	let loadingPlant = false;

	let content = '';
	let dueDateLocal = '';
	let imageFile = null;
	let submitting = false;
	let error = '';

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
		<div class="container">
			<h1 class="app-title">
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
		</div>

		<div class="form-container">
			<form on:submit={handleSubmit}>
				<div class="form-group">
					<label for="dueDate">Due (Optional)</label>
					<input
						id="dueDate"
						type="datetime-local"
						bind:value={dueDateLocal}
						disabled={submitting}
					/>
				</div>

				<div class="form-group">
					<label for="image">Image (Optional)</label>
					<input id="image" type="file" accept="image/*" on:change={handleImageChange} disabled={submitting} />
					<div class="file-hint">Optional: attach a photo to this note</div>
				</div>

				<div class="form-group">
					<label for="content">Note</label>
					<textarea
						id="content"
						bind:value={content}
						required
						rows="6"
						placeholder="What did you notice? What did you do? Any changes?"
						disabled={submitting}
					></textarea>
				</div>

				{#if error}
					<div class="error-message">{error}</div>
				{/if}

				<div class="form-actions">
					<button type="button" class="cancel-button" on:click={backToPlant} disabled={submitting}>
						Cancel
					</button>
					<button type="submit" class="submit-button" disabled={submitting || !content.trim()}>
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

	label {
		font-family: 'IBM Plex Mono', monospace;
		color: #00ff88;
		font-size: 0.9rem;
	}

	input,
	textarea {
		background-color: rgba(0, 0, 0, 0.5);
		border: 1px solid rgba(0, 255, 136, 0.5);
		color: #00ff88;
		font-family: 'Source Code Pro', monospace;
		padding: 0.75rem;
		border-radius: 4px;
		font-size: 1rem;
		transition: all 0.3s ease-in-out;
	}

	textarea {
		resize: vertical;
		min-height: 140px;
	}

	input:focus,
	textarea:focus {
		outline: none;
		border-color: #00ff00;
		box-shadow: 0 0 10px rgba(0, 255, 0, 0.3);
	}

	input:disabled,
	textarea:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	input::placeholder,
	textarea::placeholder {
		color: rgba(0, 255, 136, 0.5);
	}

	input[type='file'] {
		cursor: pointer;
		padding: 0.5rem;
	}

	input[type='file']::file-selector-button {
		background: black;
		border: 1px solid rgba(0, 255, 136, 0.5);
		color: #00ff88;
		font-family: 'IBM Plex Mono', monospace;
		padding: 0.5rem 1rem;
		border-radius: 4px;
		cursor: pointer;
		margin-right: 1rem;
		transition: all 0.3s ease-in-out;
	}

	input[type='file']::file-selector-button:hover {
		border-color: #00ff00;
		box-shadow: 0 0 10px rgba(0, 255, 0, 0.3);
	}

	.file-hint {
		font-size: 0.8rem;
		color: rgba(0, 255, 136, 0.6);
		font-family: 'Source Code Pro', monospace;
		margin-top: 0.25rem;
	}

	.error-message {
		background-color: rgba(255, 0, 0, 0.2);
		border: 1px solid rgba(255, 0, 0, 0.5);
		color: #ff6b6b;
		padding: 0.75rem;
		border-radius: 4px;
		font-family: 'Source Code Pro', monospace;
		font-size: 0.9rem;
	}

	.form-actions {
		display: flex;
		gap: 1rem;
		justify-content: flex-end;
		margin-top: 1rem;
	}

	.submit-button,
	.cancel-button {
		background: black;
		border: 2px solid #00ff00;
		color: #00ff00;
		font-family: 'IBM Plex Mono', monospace;
		font-size: 16px;
		padding: 10px 24px;
		cursor: pointer;
		transition: all 0.3s ease-in-out;
		box-shadow: 0 0 10px rgba(0, 255, 0, 0.3);
		border-radius: 8px;
	}

	.submit-button:hover:not(:disabled) {
		background: #00ff00;
		color: black;
		box-shadow: 0 0 20px #00ff00;
	}

	.cancel-button {
		border-color: rgba(0, 255, 136, 0.5);
		color: rgba(0, 255, 136, 0.8);
		box-shadow: 0 0 10px rgba(0, 255, 136, 0.2);
	}

	.cancel-button:hover:not(:disabled) {
		border-color: rgba(0, 255, 136, 0.8);
		color: #00ff88;
		box-shadow: 0 0 15px rgba(0, 255, 136, 0.4);
	}

	.submit-button:disabled,
	.cancel-button:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}
</style>


