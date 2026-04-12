<script>
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import exifr from 'exifr';
	import { pickMicrocopy } from '$lib/microcopy.js';

	let addPlantSubtitle = $state('');

	let nickname = '';
	let species = '';
	let imageFile = null;
	let imagePreview = null;
	let imageDate = null;
	let submitting = false;
	let error = '';

	const extractImageDate = async (file) => {
		try {
			const exifData = await exifr.parse(file, {
				pick: ['DateTimeOriginal', 'CreateDate', 'DateCreated', 'DateTime', 'ModifyDate'],
				translateKeys: false,
				translateValues: false,
				reviveValues: true
			});

			if (!exifData) {
				return null;
			}

			// Try date fields in priority order
			const dateFields = [
				'DateTimeOriginal',
				'CreateDate',
				'DateCreated',
				'DateTime',
				'ModifyDate'
			];

			for (const field of dateFields) {
				if (exifData[field]) {
					const date = new Date(exifData[field]);
					if (!isNaN(date.getTime())) {
						return date;
					}
				}
			}
		} catch (err) {
			// Silently fail - will use current date as fallback
		}
		return null;
	};

	const handleImageChange = async (e) => {
		const file = e.target.files[0];
		if (file) {
			// Validate file type
			const allowedTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/gif', 'image/webp'];

			if (!allowedTypes.includes(file.type)) {
				error = 'Invalid file type. Please select a PNG, JPG, GIF, or WEBP image.';
				e.target.value = '';
				imageFile = null;
				imagePreview = null;
				imageDate = null;
				return;
			}

			imageFile = file;
			error = '';

			// Extract date from EXIF metadata
			imageDate = await extractImageDate(file);

			// Create preview
			const reader = new FileReader();
			reader.onload = (e) => {
				imagePreview = e.target.result;
			};
			reader.readAsDataURL(file);
		} else {
			imageFile = null;
			imagePreview = null;
			imageDate = null;
		}
	};

	const handleSubmit = async (e) => {
		e.preventDefault();
		submitting = true;
		error = '';

		try {
			// First, create the plant
			const plantResponse = await fetch('/api/plants/', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({
					nickname: nickname.trim(),
					species: species.trim()
				})
			});

			if (!plantResponse.ok) {
				const data = await plantResponse.json();
				error = data.error || 'Failed to create plant';
				submitting = false;
				return;
			}

			const newPlant = await plantResponse.json();

			// If an image was selected, upload it
			if (imageFile && newPlant.id) {
				const formData = new FormData();
				formData.append('image', imageFile);
				// Include date if we extracted it from EXIF
				if (imageDate) {
					formData.append('date', imageDate.toISOString());
				}

				const imageResponse = await fetch(`/api/plants/${newPlant.id}/photo_histories`, {
					method: 'POST',
					body: formData
				});

				if (!imageResponse.ok) {
					const data = await imageResponse.json();
					error = data.error || 'Plant created but failed to upload image';
					submitting = false;
					return;
				}
			}

			// Success - redirect to home
			goto('/');
		} catch (err) {
			error = 'Network error. Please try again.';
			console.error('Error creating plant:', err);
			submitting = false;
		}
	};

	const handleCancel = () => {
		goto('/');
	};

	const removeImage = () => {
		imageFile = null;
		imagePreview = null;
		imageDate = null;
		// Reset the file input
		const fileInput = document.getElementById('image');
		if (fileInput) {
			fileInput.value = '';
		}
	};

	onMount(() => {
		addPlantSubtitle = pickMicrocopy('addPlantSubtitle', new Date());
	});
</script>

<main>
	<div class="container column">
		<div class="container">
			<h1 class="form-page-title">Add New Plant</h1>
			{#if addPlantSubtitle}
				<p class="microcopy microcopy-muted form-page-subtitle">{addPlantSubtitle}</p>
			{/if}
		</div>

		<div class="form-container">
			<form on:submit={handleSubmit}>
				<div class="form-group">
					<label class="form-label" for="nickname">Nickname</label>
					<input
						class="form-field"
						type="text"
						id="nickname"
						bind:value={nickname}
						required
						placeholder="e.g., Basil"
						disabled={submitting}
					/>
				</div>

				<div class="form-group">
					<label class="form-label" for="species">Species</label>
					<input
						class="form-field"
						type="text"
						id="species"
						bind:value={species}
						required
						placeholder="e.g., Ocimum basilicum"
						disabled={submitting}
					/>
				</div>

				<div class="form-group">
					<label class="form-label" for="image">Image (Optional)</label>
					<input
						class="form-field form-file-button"
						type="file"
						id="image"
						accept="image/*"
						on:change={handleImageChange}
						disabled={submitting}
					/>
					<div class="file-hint">Tap to take a photo or choose from gallery</div>
				</div>

				{#if imagePreview}
					<div class="image-preview-container">
						<div class="image-preview-wrapper">
							<img src={imagePreview} alt="Preview" class="image-preview" />
							<button
								type="button"
								class="remove-image-button"
								on:click={removeImage}
								disabled={submitting}
							>
								×
							</button>
						</div>
					</div>
				{/if}

				{#if error}
					<div class="form-error">{error}</div>
				{/if}

				<div class="form-actions">
					<button type="button" class="btn btn-ghost" on:click={handleCancel} disabled={submitting}>
						Cancel
					</button>
					<button
						type="submit"
						class="btn btn-primary"
						disabled={submitting || !nickname.trim() || !species.trim()}
					>
						{submitting ? 'Adding...' : 'Add Plant'}
					</button>
				</div>
			</form>
		</div>
	</div>
</main>

<style>
	.form-container {
		max-width: 500px;
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

	input[type='file'] {
		cursor: pointer;
		padding: 0.5rem;
	}

	.file-hint {
		font-size: 0.8rem;
		color: var(--color-text-muted);
		margin-top: 0.25rem;
	}

	.image-preview-container {
		margin-top: 0.5rem;
	}

	.image-preview-wrapper {
		position: relative;
		display: inline-block;
		border: 1px solid var(--color-border);
		border-radius: var(--radius-md);
		padding: 0.5rem;
		background-color: var(--color-surface-solid);
	}

	.image-preview {
		max-width: 100%;
		max-height: 300px;
		display: block;
		border-radius: var(--radius-sm);
	}

	.remove-image-button {
		position: absolute;
		top: 0.75rem;
		right: 0.75rem;
		width: 32px;
		height: 32px;
		border-radius: 50%;
		background-color: var(--color-surface-raised);
		border: 1px solid var(--color-danger);
		color: var(--color-danger);
		font-size: 1.5rem;
		font-family: inherit;
		cursor: pointer;
		display: flex;
		align-items: center;
		justify-content: center;
		transition:
			background 0.2s ease,
			color 0.2s ease;
		line-height: 1;
		padding: 0;
	}

	.remove-image-button:hover:not(:disabled) {
		background-color: var(--color-danger-soft);
		color: var(--color-danger);
	}

	.remove-image-button:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	.form-actions {
		display: flex;
		gap: 1rem;
		justify-content: flex-end;
		margin-top: 1rem;
		flex-wrap: wrap;
	}
</style>
