<script lang="ts">
	let { tool } = $props<{ tool: string }>();

	const colorMap: Record<string, string> = {
		get_price: '#d4af37',
		get_financials: '#4a9eff',
		get_chart_data: '#b44aff',
		get_insider_trades: '#ff8c00',
		get_news: '#00ff41'
	};

	const stripe = $derived(colorMap[tool] ?? '#6b6b6b');
</script>

<div class="card" style={`--stripe: ${stripe};`}>
	{#if tool === 'get_price'}
		<div class="bar lg shimmer"></div>
		<div class="bar md shimmer"></div>
		<div class="row">
			<div class="bar sm shimmer"></div>
			<div class="bar sm shimmer"></div>
			<div class="bar sm shimmer"></div>
		</div>
	{:else if tool === 'get_financials'}
		<div class="bar md shimmer"></div>
		<div class="grid">
			{#each Array(8) as _}
				<div class="bar sm shimmer"></div>
			{/each}
		</div>
	{:else if tool === 'get_chart_data'}
		<div class="row" style="justify-content: space-between;">
			<div class="bar md shimmer" style="width: 30%;"></div>
			<div class="row" style="gap: 4px; width: 40%;"><div class="bar sm shimmer"></div><div class="bar sm shimmer"></div><div class="bar sm shimmer"></div></div>
		</div>
		<div class="chart-skel shimmer"></div>
	{:else if tool === 'get_insider_trades'}
		<div class="bar md shimmer"></div>
		{#each Array(4) as _}
			<div class="bar rowish shimmer"></div>
		{/each}
	{:else if tool === 'get_news'}
		<div class="bar md shimmer"></div>
		{#each Array(3) as _}
			<div class="article shimmer"></div>
		{/each}
	{:else}
		<div class="bar md shimmer"></div>
	{/if}
</div>

<style>
	.card {
		background: #0a0a0a;
		border: 1px solid #1a1a1a;
		border-left: 4px solid var(--stripe);
		border-radius: 8px;
		padding: 12px;
		display: flex;
		flex-direction: column;
		gap: 10px;
	}

	.shimmer {
		background: linear-gradient(90deg, #1a1a1a 0%, #2a2a2a 45%, #1a1a1a 100%);
		background-size: 200% 100%;
		animation: shimmer 1.5s linear infinite;
	}

	.bar {
		height: 10px;
		border-radius: 4px;
	}
	.lg {
		height: 26px;
		width: 42%;
	}
	.md {
		height: 14px;
		width: 56%;
	}
	.sm {
		width: 100%;
	}
	.rowish {
		height: 30px;
		width: 100%;
	}
	.row {
		display: grid;
		grid-template-columns: repeat(3, minmax(0, 1fr));
		gap: 8px;
	}
	.grid {
		display: grid;
		grid-template-columns: repeat(2, minmax(0, 1fr));
		gap: 8px;
	}
	.article {
		height: 40px;
		border-radius: 6px;
	}
	.chart-skel {
		width: 100%;
		aspect-ratio: 3 / 1;
		border-radius: 6px;
	}

	@keyframes shimmer {
		0% {
			background-position: 200% 0;
		}
		100% {
			background-position: -200% 0;
		}
	}
</style>
