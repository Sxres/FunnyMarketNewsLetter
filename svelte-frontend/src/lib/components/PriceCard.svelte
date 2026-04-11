<script lang="ts">
	let { data } = $props<{ data: Record<string, any> }>();

	const positive = $derived((data.change ?? 0) >= 0);

	function formatCurrency(value: unknown): string {
		if (typeof value !== 'number') return '-';
		return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 2 }).format(value);
	}

	function formatCompact(value: unknown): string {
		if (typeof value !== 'number') return '-';
		return new Intl.NumberFormat('en-US', { notation: 'compact', maximumFractionDigits: 2 }).format(value);
	}
</script>

<div class="card">
	{#if data.error}
		<div class="error">{data.error}</div>
	{:else}
		<div class="head">
			<div>
				<div class="ticker">{data.ticker ?? 'Ticker'}</div>
				<div class="company">Price Snapshot</div>
			</div>
			<div class="asof">As of {data.as_of ?? '-'}</div>
		</div>
		<div class="price">{formatCurrency(data.price)}</div>
		<div class:gain={positive} class:loss={!positive} class="delta">
			{formatCurrency(data.change)} ({typeof data.change_pct === 'number' ? data.change_pct.toFixed(2) : '-'}%)
		</div>
		<div class="meta">
			<span>Volume: {formatCompact(data.volume)}</span>
			<span>Mkt Cap: {formatCompact(data.market_cap)}</span>
			<span>52W: {formatCurrency(data.fifty_two_week_low)} - {formatCurrency(data.fifty_two_week_high)}</span>
		</div>
	{/if}
</div>

<style>
	.card {
		background: #0a0a0a;
		border: 1px solid #1a1a1a;
		border-left: 4px solid #d4af37;
		border-radius: 8px;
		padding: 12px;
	}
	.head {
		display: flex;
		justify-content: space-between;
		gap: 8px;
		align-items: flex-start;
	}
	.ticker {
		font-size: 22px;
		font-weight: 600;
		line-height: 1.1;
	}
	.company {
		font-size: 12px;
		color: #8c8c8c;
		margin-top: 2px;
	}
	.asof {
		font-size: 11px;
		color: #737373;
		padding-top: 2px;
	}
	.price {
		margin-top: 12px;
		font-size: 36px;
		font-weight: 500;
		line-height: 1;
	}
	.delta {
		margin-top: 6px;
		font-size: 14px;
		font-weight: 500;
	}
	.gain {
		color: #00ff41;
	}
	.loss {
		color: #ff4444;
	}
	.meta {
		margin-top: 12px;
		display: grid;
		grid-template-columns: repeat(3, minmax(0, 1fr));
		gap: 8px;
		font-size: 12px;
		color: #a2a2a2;
	}
	.error {
		color: #ff6b6b;
		font-size: 13px;
	}
	@media (max-width: 760px) {
		.meta {
			grid-template-columns: 1fr;
		}
		.price {
			font-size: 30px;
		}
	}
</style>
