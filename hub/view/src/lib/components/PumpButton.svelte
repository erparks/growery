<script>
	let pumping = false;

	const turnOnPump = async () => {
		pumping = true;
		await fetch('/api/pumps', { method: 'POST' });
		pumping = false;
	};
</script>

<button class="pump-button" class:pump-button-pumping={pumping} on:click={turnOnPump}>pump</button>
