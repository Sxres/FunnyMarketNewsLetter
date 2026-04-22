<script lang="ts">
	let { children } = $props();
</script>

<svelte:head>
	<title>Moonstack</title>
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

	@font-face {
		font-family: 'Geist Pixel Line';
		src: url('/fonts/GeistPixel-Line.woff2') format('woff2');
		font-weight: 500;
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
	:global(html) {
		scrollbar-width: thin;
		scrollbar-color: rgba(255, 255, 255, 0.12) transparent;
	}
	:global(::-webkit-scrollbar) {
		width: 10px;
		height: 10px;
	}
	:global(::-webkit-scrollbar-track) {
		background: transparent;
	}
	:global(::-webkit-scrollbar-thumb) {
		background: rgba(255, 255, 255, 0.12);
		border-radius: 10px;
		border: 2px solid transparent;
		background-clip: content-box;
		transition: background 0.2s ease;
	}
	:global(::-webkit-scrollbar-thumb:hover) {
		background: rgba(255, 255, 255, 0.28);
		background-clip: content-box;
	}
	:global(::-webkit-scrollbar-corner) {
		background: transparent;
	}
</style>
