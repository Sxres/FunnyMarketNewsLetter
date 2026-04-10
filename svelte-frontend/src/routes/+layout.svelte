<script lang="ts">
	let { children } = $props();
</script>

<svelte:head>
	<title>Market Chat</title>
	<meta name="viewport" content="width=device-width, initial-scale=1" />
</svelte:head>

{@render children()}

<style>
	@font-face {
		font-family: 'Overused Grotesk';
		src: url('/fonts/OverusedGrotesk-Book.otf') format('opentype');
		font-weight: 400;
		font-style: normal;
		font-display: swap;
	}

	:global(html, body) {
		margin: 0;
		padding: 0;
		height: 100%;
		background: #000;
		color: #eaeaea;
		font-family: 'Overused Grotesk', 'Segoe UI', system-ui, sans-serif;
		font-size: 14px;
		-webkit-font-smoothing: antialiased;
	}
	:global(*) {
		box-sizing: border-box;
	}
	:global(button) {
		font-family: inherit;
		color: inherit;
	}
	:global(::-webkit-scrollbar) {
		width: 8px;
		height: 8px;
	}
	:global(::-webkit-scrollbar-track) {
		background: transparent;
	}
	:global(::-webkit-scrollbar-thumb) {
		background: #222;
		border-radius: 4px;
	}
	:global(::-webkit-scrollbar-thumb:hover) {
		background: #333;
	}
</style>
