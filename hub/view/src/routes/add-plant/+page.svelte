<script>
	import { goto } from '$app/navigation';
	import exifr from 'exifr';

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
</script>

<main>
	<div class="container column">
		<div class="container">
			<h1 class="app-title">Add New Plant</h1>
		</div>

		<div class="form-container">
			<form on:submit={handleSubmit}>
				<div class="form-group">
					<label for="nickname">Nickname</label>
					<input
						type="text"
						id="nickname"
						bind:value={nickname}
						required
						placeholder="e.g., Basil"
						disabled={submitting}
					/>
				</div>

				<div class="form-group">
					<label for="species">Species</label>
					<input
						type="text"
						id="species"
						bind:value={species}
						required
						placeholder="e.g., Ocimum basilicum"
						disabled={submitting}
					/>
				</div>

				<div class="form-group">
					<label for="image">Image (Optional)</label>
					<input
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
					<div class="error-message">{error}</div>
				{/if}

				<div class="form-actions">
					<button type="button" class="cancel-button" on:click={handleCancel} disabled={submitting}>
						Cancel
					</button>
					<button
						type="submit"
						class="submit-button"
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

	label {
		font-family: 'IBM Plex Mono', monospace;
		color: #00ff88;
		font-size: 0.9rem;
	}

	input {
		background-color: rgba(0, 0, 0, 0.5);
		border: 1px solid rgba(0, 255, 136, 0.5);
		color: #00ff88;
		font-family: 'Source Code Pro', monospace;
		padding: 0.75rem;
		border-radius: 4px;
		font-size: 1rem;
		transition: all 0.3s ease-in-out;
	}

	input:focus {
		outline: none;
		border-color: #00ff00;
		box-shadow: 0 0 10px rgba(0, 255, 0, 0.3);
	}

	input:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	input::placeholder {
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

	.image-preview-container {
		margin-top: 0.5rem;
	}

	.image-preview-wrapper {
		position: relative;
		display: inline-block;
		border: 1px solid rgba(0, 255, 136, 0.5);
		border-radius: 4px;
		padding: 0.5rem;
		background-color: rgba(0, 0, 0, 0.3);
	}

	.image-preview {
		max-width: 100%;
		max-height: 300px;
		display: block;
		border-radius: 4px;
	}

	.remove-image-button {
		position: absolute;
		top: 0.75rem;
		right: 0.75rem;
		width: 32px;
		height: 32px;
		border-radius: 50%;
		background-color: rgba(0, 0, 0, 0.8);
		border: 2px solid #ff6b6b;
		color: #ff6b6b;
		font-size: 1.5rem;
		font-family: 'IBM Plex Mono', monospace;
		cursor: pointer;
		display: flex;
		align-items: center;
		justify-content: center;
		transition: all 0.3s ease-in-out;
		line-height: 1;
		padding: 0;
	}

	.remove-image-button:hover:not(:disabled) {
		background-color: #ff6b6b;
		color: black;
		box-shadow: 0 0 15px rgba(255, 107, 107, 0.5);
	}

	.remove-image-button:disabled {
		opacity: 0.5;
		cursor: not-allowed;
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
