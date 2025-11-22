<script>
	import { goto } from '$app/navigation';

	let nickname = '';
	let species = '';
	let submitting = false;
	let error = '';

	const handleSubmit = async (e) => {
		e.preventDefault();
		submitting = true;
		error = '';

		try {
			const response = await fetch('/api/plants/', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({
					nickname: nickname.trim(),
					species: species.trim()
				})
			});

			if (response.ok) {
				goto('/');
			} else {
				const data = await response.json();
				error = data.error || 'Failed to create plant';
			}
		} catch (err) {
			error = 'Network error. Please try again.';
			console.error('Error creating plant:', err);
		} finally {
			submitting = false;
		}
	};

	const handleCancel = () => {
		goto('/');
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

				{#if error}
					<div class="error-message">{error}</div>
				{/if}

				<div class="form-actions">
					<button type="button" class="cancel-button" on:click={handleCancel} disabled={submitting}>
						Cancel
					</button>
					<button type="submit" class="submit-button" disabled={submitting || !nickname.trim() || !species.trim()}>
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

