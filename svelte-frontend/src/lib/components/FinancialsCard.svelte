<script lang="ts">
	let { data } = $props<{ data: Record<string, any> }>();

	function formatNumber(value: unknown, opts: Intl.NumberFormatOptions = {}): string {
		if (typeof value !== 'number') return '-';
		return new Intl.NumberFormat('en-US', opts).format(value);
	}

	function formatCompact(value: unknown): string {
		if (typeof value !== 'number') return '-';
		return new Intl.NumberFormat('en-US', { notation: 'compact', maximumFractionDigits: 2 }).format(value);
	}

	function formatPercent(value: unknown): string {
		if (typeof value !== 'number') return '-';
		const normalized = Math.abs(value) <= 1 ? value * 100 : value;
		return `${normalized.toFixed(2)}%`;
	}

	const rows = $derived([
		['P/E (Trailing)', formatNumber(data.pe_ratio_trailing, { maximumFractionDigits: 2 })],
		['P/E (Forward)', formatNumber(data.pe_ratio_forward, { maximumFractionDigits: 2 })],
		['PEG', formatNumber(data.peg_ratio, { maximumFractionDigits: 2 })],
		['Price/Book', formatNumber(data.price_to_book, { maximumFractionDigits: 2 })],
		['Gross Margin', formatPercent(data.gross_margin)],
		['Operating Margin', formatPercent(data.operating_margin)],
		['ROE', formatPercent(data.return_on_equity)],
		['Debt/Equity', formatNumber(data.debt_to_equity, { maximumFractionDigits: 2 })],
		['Revenue', formatCompact(data.revenue_ttm)],
		['Market Cap', formatCompact(data.market_cap)]
	].filter((row) => row[1] !== '-'));

	function buildCategoryTag(payload: Record<string, any>): string {
		const sector = (payload.sector ?? '').toString().trim();
		const industry = (payload.industry ?? '').toString().trim();
		if (!sector && !industry) return '';
		if (sector && industry && sector.toLowerCase() !== industry.toLowerCase()) {
			return `${sector} · ${industry}`;
		}
		return sector || industry;
	}

	const categoryTag = $derived(buildCategoryTag(data));
</script>

<div class="card">
	{#if data.error}
		<div class="error">{data.error}</div>
	{:else}
		<div class="head">
			<div>
				<div class="ticker">{data.ticker ?? 'Ticker'}</div>
				<div class="company">{data.company_name ?? 'Financial Overview'}</div>
			</div>
			{#if categoryTag}
				<div class="category">{categoryTag}</div>
			{/if}
		</div>
		<div class="table">
			{#if rows.length === 0}
				<div class="empty">No financial metrics available for this ticker.</div>
			{:else}
				{#each rows as row}
					<div class="k">{row[0]}</div>
					<div class="v">{row[1]}</div>
				{/each}
			{/if}
		</div>
	{/if}
</div>

<style>
	.card {
		background: #0a0a0a;
		border: 1px solid #1a1a1a;
		border-left: 4px solid #4a9eff;
		border-radius: 8px;
		padding: 12px;
	}
	.head {
		display: flex;
		justify-content: space-between;
		gap: 10px;
	}
	.ticker {
		font-size: 18px;
		font-weight: 600;
	}
	.company {
		font-size: 13px;
		color: #bababa;
		margin-top: 2px;
	}
	.category {
		font-size: 18px;
		font-weight: 600;
		line-height: 1.1;
		color: #ffffff;
		text-align: right;
		white-space: nowrap;
	}
	.table {
		margin-top: 12px;
		display: grid;
		grid-template-columns: repeat(2, minmax(0, 1fr));
		gap: 8px 14px;
	}
	.k {
		font-size: 12px;
		color: #8f8f8f;
	}
	.v {
		font-size: 12px;
		color: #e2e2e2;
		text-align: right;
	}
	.empty {
		font-size: 12px;
		color: #8f8f8f;
	}
	.error {
		color: #ff6b6b;
		font-size: 13px;
	}
	@media (max-width: 760px) {
		.table {
			grid-template-columns: 1fr;
		}
		.v {
			text-align: left;
		}
	}
</style>
