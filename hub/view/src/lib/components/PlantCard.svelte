<script>
	import { onMount } from 'svelte';

	export let plant;
</script>

<div class="card">
	<a href={`/plant_detail/?plant_id=${plant['id']}`}>
		<h3>{plant['nickname']}</h3>
		<span class="text-small">({plant['species']})</span>
	</a>
</div>
