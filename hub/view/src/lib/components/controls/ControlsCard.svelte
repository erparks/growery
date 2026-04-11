<script>
	import PumpButton from '../PumpButton.svelte';
</script>

<div class="card controls-card">
	<h3 class="controls-title">controls</h3>
	<PumpButton />
</div>

<style>
	.controls-title {
		margin: 0 0 1rem;
		font-size: 1rem;
		font-weight: 500;
		color: var(--color-text-muted);
		letter-spacing: 0.04em;
		text-transform: lowercase;
	}
</style>
