<script>
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';

	onMount(() => {
		const fullUrl = window.location.pathname + window.location.search;
		goto(fullUrl);
	});
</script>

<slot />
