<script>
	import { browser } from '$app/environment';
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import AppMenu from '$lib/components/AppMenu.svelte';
	import SunTheme from '$lib/components/SunTheme.svelte';

	onMount(() => {
		const fullUrl = window.location.pathname + window.location.search;
		goto(fullUrl);
	});
</script>

{#if browser}
	<SunTheme />
{/if}
<div class="app-shell">
	<AppMenu />
	<div class="app-shell__main">
		<slot />
	</div>
</div>

