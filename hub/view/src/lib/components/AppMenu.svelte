<script>
	import { browser } from '$app/environment';
	import { afterNavigate } from '$app/navigation';
	import { onMount } from 'svelte';

	let open = $state(false);

	afterNavigate(() => {
		open = false;
	});

	onMount(() => {
		const onKey = (e) => {
			if (e.key === 'Escape') open = false;
		};
		window.addEventListener('keydown', onKey);
		return () => window.removeEventListener('keydown', onKey);
	});

	$effect(() => {
		if (!browser) return;
		document.body.style.overflow = open ? 'hidden' : '';
		return () => {
			document.body.style.overflow = '';
		};
	});

	const toggle = () => {
		open = !open;
	};

	const close = () => {
		open = false;
	};

	/** @param {MouseEvent} e */
	const onBackdropClick = (e) => {
		if (e.target === e.currentTarget) close();
	};
</script>

<div class="app-menu-root">
	<button
		type="button"
		class="app-menu-toggle"
		class:app-menu-toggle--open={open}
		onclick={toggle}
		aria-expanded={open}
		aria-controls="app-nav-drawer"
		aria-label={open ? 'Close menu' : 'Open menu'}
	>
		<span class="app-menu-bars" aria-hidden="true">
			<span></span>
			<span></span>
			<span></span>
		</span>
	</button>

	{#if open}
		<button
			type="button"
			class="app-menu-backdrop"
			onclick={onBackdropClick}
			aria-label="Close menu"
		></button>
	{/if}

	<nav
		id="app-nav-drawer"
		class="app-menu-drawer"
		class:app-menu-drawer--open={open}
		aria-hidden={!open}
	>
		<ul class="app-menu-list">
			<li>
				<a href="/" class="app-menu-link" onclick={close}>
					<span class="app-menu-link-icon" aria-hidden="true">
						<svg
							xmlns="http://www.w3.org/2000/svg"
							viewBox="0 0 24 24"
							fill="none"
							stroke="currentColor"
							stroke-width="2"
							stroke-linecap="round"
							stroke-linejoin="round"
						>
							<path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
							<polyline points="9 22 9 12 15 12 15 22" />
						</svg>
					</span>
					Home
				</a>
			</li>
			<li>
				<a href="/bulk-upload" class="app-menu-link" onclick={close}>
					<span class="app-menu-link-icon" aria-hidden="true">
						<svg
							xmlns="http://www.w3.org/2000/svg"
							viewBox="0 0 24 24"
							fill="none"
							stroke="currentColor"
							stroke-width="2"
							stroke-linecap="round"
							stroke-linejoin="round"
						>
							<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
							<polyline points="17 8 12 3 7 8" />
							<line x1="12" y1="3" x2="12" y2="15" />
						</svg>
					</span>
					Bulk Upload
				</a>
			</li>
		</ul>
	</nav>
</div>

<style>
	/* Fixed overlay: does not consume layout space or push page content; passes clicks through except controls */
	.app-menu-root {
		position: fixed;
		inset: 0;
		z-index: 1100;
		pointer-events: none;
		--app-menu-z-toggle: 1102;
		--app-menu-z-backdrop: 1090;
		--app-menu-z-drawer: 1095;
	}

	.app-menu-toggle,
	.app-menu-backdrop {
		pointer-events: auto;
	}

	.app-menu-toggle {
		position: fixed;
		top: 1.35rem;
		left: clamp(1rem, 4vw, 2.5rem);
		z-index: var(--app-menu-z-toggle);
		width: 44px;
		height: 44px;
		display: flex;
		align-items: center;
		justify-content: center;
		padding: 0;
		border-radius: var(--radius-md);
		border: 1px solid var(--color-border-strong);
		background: var(--color-surface-solid);
		color: var(--color-accent-warm);
		cursor: pointer;
		box-shadow: var(--shadow-card);
		transition:
			background 0.2s ease,
			border-color 0.2s ease,
			color 0.2s ease;
	}

	.app-menu-toggle:hover {
		background: rgba(212, 196, 168, 0.12);
		border-color: var(--color-accent-warm);
		color: #ebe3d4;
	}

	.app-menu-toggle:focus-visible {
		outline: none;
		box-shadow: var(--shadow-card), var(--focus-ring);
	}

	.app-menu-bars {
		display: flex;
		flex-direction: column;
		justify-content: center;
		gap: 5px;
		width: 20px;
		height: 16px;
	}

	.app-menu-bars span {
		display: block;
		height: 2px;
		width: 100%;
		border-radius: 1px;
		background: currentColor;
		transition:
			transform 0.2s ease,
			opacity 0.2s ease;
		transform-origin: center;
	}

	.app-menu-toggle--open .app-menu-bars span:nth-child(1) {
		transform: translateY(7px) rotate(45deg);
	}

	.app-menu-toggle--open .app-menu-bars span:nth-child(2) {
		opacity: 0;
	}

	.app-menu-toggle--open .app-menu-bars span:nth-child(3) {
		transform: translateY(-7px) rotate(-45deg);
	}

	.app-menu-backdrop {
		position: fixed;
		inset: 0;
		z-index: var(--app-menu-z-backdrop);
		margin: 0;
		padding: 0;
		border: none;
		background: rgba(8, 12, 10, 0.55);
		backdrop-filter: blur(2px);
		cursor: pointer;
	}

	.app-menu-drawer {
		position: fixed;
		top: 0;
		left: 0;
		bottom: 0;
		z-index: var(--app-menu-z-drawer);
		width: min(18rem, 86vw);
		max-width: 100%;
		margin: 0;
		padding: 6.25rem 1.25rem 1.5rem;
		border: none;
		border-right: 1px solid var(--color-border);
		background: var(--color-surface-solid);
		box-shadow: var(--shadow-soft);
		transform: translateX(-100%);
		transition: transform 0.22s ease;
		pointer-events: none;
		visibility: hidden;
	}

	.app-menu-drawer--open {
		transform: translateX(0);
		pointer-events: auto;
		visibility: visible;
	}

	.app-menu-list {
		list-style: none;
		margin: 0;
		padding: 0;
		display: flex;
		flex-direction: column;
		gap: 0.35rem;
	}

	.app-menu-link {
		display: flex;
		align-items: center;
		gap: 0.65rem;
		padding: 0.65rem 0.85rem;
		border-radius: var(--radius-sm);
		font-family: var(--font-sans);
		font-size: 1rem;
		font-weight: 500;
		color: var(--color-heading);
		text-decoration: none;
		border: 1px solid transparent;
		transition:
			background 0.15s ease,
			border-color 0.15s ease,
			color 0.15s ease;
	}

	.app-menu-link-icon {
		display: flex;
		align-items: center;
		justify-content: center;
		flex-shrink: 0;
		width: 1.35rem;
		height: 1.35rem;
		color: var(--color-accent);
		opacity: 0.92;
	}

	.app-menu-link:hover .app-menu-link-icon {
		color: var(--color-accent);
		opacity: 1;
	}

	.app-menu-link-icon svg {
		width: 100%;
		height: 100%;
		display: block;
	}

	.app-menu-link:hover {
		background: var(--color-accent-soft);
		border-color: var(--color-border);
		color: var(--color-accent);
	}

	.app-menu-link:focus-visible {
		outline: none;
		box-shadow: var(--focus-ring);
	}
</style>
