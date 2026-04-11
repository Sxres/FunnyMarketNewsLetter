<script lang="ts">
	let { data } = $props<{ data: Record<string, any> }>();

	const trades = $derived(Array.isArray(data.trades) ? data.trades.slice(0, 8) : []);
	const summary = $derived(data.summary ?? {});

	function compact(value: unknown): string {
		if (typeof value !== 'number') return '-';
		return new Intl.NumberFormat('en-US', { notation: 'compact', maximumFractionDigits: 2 }).format(value);
	}

	function transactionClass(tx: unknown): string {
		const text = (tx ?? '').toString().toLowerCase();
		if (text.includes('buy') || text.includes('purchase')) return 'buy';
		if (text.includes('sell') || text.includes('sale')) return 'sell';
		return '';
	}
</script>

<div class="card">
	{#if data.error}
		<div class="error">{data.error}</div>
	{:else}
		<div class="head">{data.ticker ?? 'Ticker'} Insider Activity</div>
		<div class="summary">
			<span class="buy">Buys: {summary.buys ?? 0}</span>
			<span class="sell">Sells: {summary.sells ?? 0}</span>
			<span>Total: {summary.total ?? trades.length}</span>
		</div>
		{#if trades.length === 0}
			<div class="empty">{data.note ?? 'No recent insider transactions found'}</div>
		{:else}
			<div class="table">
				<div class="th">Insider</div>
				<div class="th">Type</div>
				<div class="th">Shares</div>
				<div class="th">Value</div>
				<div class="th">Date</div>
				{#each trades as t}
					<div class="td">{t.insider}</div>
					<div class={`td ${transactionClass(t.transaction)}`}>{t.transaction}</div>
					<div class="td">{compact(t.shares)}</div>
					<div class="td">{compact(t.value)}</div>
					<div class="td">{t.date?.slice(0, 10)}</div>
				{/each}
			</div>
		{/if}
	{/if}
</div>

<style>
	.card {
		background: #0a0a0a;
		border: 1px solid #1a1a1a;
		border-left: 4px solid #ff8c00;
		border-radius: 8px;
		padding: 12px;
	}
	.head {
		font-size: 16px;
		font-weight: 600;
	}
	.summary {
		display: flex;
		gap: 12px;
		font-size: 12px;
		color: #b8b8b8;
		margin-top: 8px;
	}
	.summary .buy {
		color: #00ff41;
	}
	.summary .sell {
		color: #ff4444;
	}
	.table {
		margin-top: 10px;
		display: grid;
		grid-template-columns: 1.5fr 1fr 1fr 1fr 1fr;
		gap: 6px;
		font-size: 11px;
	}
	.th {
		color: #7e7e7e;
		text-transform: uppercase;
		letter-spacing: 0.04em;
	}
	.td {
		color: #d4d4d4;
		padding: 2px 0;
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
	}
	.td.buy {
		color: #00ff41;
	}
	.td.sell {
		color: #ff4444;
	}
	.empty,
	.error {
		margin-top: 8px;
		font-size: 13px;
		color: #ff6b6b;
	}
	@media (max-width: 900px) {
		.table {
			grid-template-columns: 1fr 1fr;
		}
		.th:nth-child(n + 3),
		.td:nth-child(5n + 3),
		.td:nth-child(5n + 4),
		.td:nth-child(5n + 5) {
			display: none;
		}
	}
</style>
