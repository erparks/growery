<script>
	import { browser } from '$app/environment';
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import SunTheme from '$lib/components/SunTheme.svelte';

	onMount(() => {
		const fullUrl = window.location.pathname + window.location.search;
		goto(fullUrl);
	});
</script>

{#if browser}
	<SunTheme />
{/if}
<slot />

