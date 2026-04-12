<script>
	import { onMount, onDestroy } from 'svelte';
	import { applySunTheme } from '$lib/sunTheme.js';

	let intervalId;

	function onVisibility() {
		if (document.visibilityState === 'visible') applySunTheme();
	}

	onMount(() => {
		applySunTheme();
		intervalId = setInterval(applySunTheme, 60_000);
		document.addEventListener('visibilitychange', onVisibility);
	});

	onDestroy(() => {
		if (intervalId) clearInterval(intervalId);
		if (typeof document !== 'undefined') {
			document.removeEventListener('visibilitychange', onVisibility);
		}
	});
</script>
