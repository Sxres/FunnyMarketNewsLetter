<script lang="ts">
	let { data } = $props<{ data: Record<string, any> }>();

	function asCurrency(value: unknown): string {
		if (typeof value !== 'number') return '-';
		return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 2 }).format(value);
	}

	const current = $derived(typeof data.current_price === 'number' ? data.current_price : null);
	const mean = $derived(typeof data.target_price_mean === 'number' ? data.target_price_mean : null);
	const upsidePct = $derived(current && mean ? ((mean - current) / current) * 100 : null);
	const recommendation = $derived((data.recommendation ?? 'hold').toString().toLowerCase());
	const badgeClass = $derived(recommendation.includes('buy') ? 'buy' : recommendation.includes('sell') ? 'sell' : 'hold');
	const actions = $derived(Array.isArray(data.recent_actions) ? data.recent_actions.slice(0, 5) : []);
</script>

<div class="card">
	{#if data.error}
		<div class="error">{data.error}</div>
	{:else}
		<div class="head">
			<div class="ticker">{data.ticker ?? 'Ticker'}</div>
			<div class={`badge ${badgeClass}`}>{recommendation.toUpperCase()}</div>
		</div>
		<div class="prices">
			<span>Now {asCurrency(current)}</span>
			<span>Mean {asCurrency(mean)}</span>
		</div>
		{#if upsidePct !== null}
			<div class="bar-wrap">
				<div class="bar-fill" style={`width: ${Math.min(Math.abs(upsidePct), 100)}%;`}></div>
			</div>
			<div class:up={upsidePct >= 0} class:down={upsidePct < 0} class="upside">
				{upsidePct >= 0 ? '+' : ''}{upsidePct.toFixed(2)}% vs current
			</div>
		{/if}
		<div class="range">
			<span>Low {asCurrency(data.target_price_low)}</span>
			<span>High {asCurrency(data.target_price_high)}</span>
		</div>
		{#if actions.length > 0}
			<div class="actions">
				{#each actions as action}
					<div class="action-row">
						<span>{action.date}</span>
						<span>{action.firm}</span>
						<span>{action.action}</span>
					</div>
				{/each}
			</div>
		{/if}
	{/if}
</div>

<style>
	.card {
		background: #0a0a0a;
		border: 1px solid #1a1a1a;
		border-left: 4px solid #b44aff;
		border-radius: 8px;
		padding: 12px;
	}
	.head {
		display: flex;
		justify-content: space-between;
		align-items: center;
	}
	.ticker {
		font-size: 18px;
		font-weight: 600;
	}
	.badge {
		font-size: 11px;
		padding: 3px 8px;
		border-radius: 999px;
		font-weight: 600;
	}
	.badge.buy {
		color: #00ff41;
		background: #102514;
		border: 1px solid #184d26;
	}
	.badge.hold {
		color: #f2c94c;
		background: #262010;
		border: 1px solid #4c3d1a;
	}
	.badge.sell {
		color: #ff6b6b;
		background: #2a1111;
		border: 1px solid #5a1f1f;
	}
	.prices,
	.range {
		display: flex;
		justify-content: space-between;
		font-size: 12px;
		color: #bcbcbc;
		margin-top: 8px;
	}
	.bar-wrap {
		height: 8px;
		background: #171717;
		border: 1px solid #242424;
		border-radius: 999px;
		margin-top: 10px;
		overflow: hidden;
	}
	.bar-fill {
		height: 100%;
		background: linear-gradient(90deg, #7c35d8 0%, #b44aff 100%);
	}
	.upside {
		font-size: 12px;
		margin-top: 6px;
	}
	.up {
		color: #00ff41;
	}
	.down {
		color: #ff4444;
	}
	.actions {
		margin-top: 10px;
		display: flex;
		flex-direction: column;
		gap: 5px;
	}
	.action-row {
		display: grid;
		grid-template-columns: 90px 1fr auto;
		gap: 8px;
		font-size: 11px;
		color: #a9a9a9;
	}
	.error {
		color: #ff6b6b;
		font-size: 13px;
	}
</style>
