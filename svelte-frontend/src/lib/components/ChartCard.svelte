<script lang="ts">
	type Candle = { t: number; c: number; v?: number; o?: number; h?: number; l?: number };
	type Range = '1D' | '1W' | '1M' | '6M' | '1Y' | 'ALL';

	let { data } = $props<{ data: Record<string, any> }>();

	let range = $state<Range>('1M');
	let hoverIdx = $state<number | null>(null);

	const ranges: Range[] = ['1D', '1W', '1M', '6M', '1Y', 'ALL'];

	const daily = $derived<Candle[]>(Array.isArray(data.daily) ? data.daily : []);
	const intraday = $derived<Candle[]>(Array.isArray(data.intraday) ? data.intraday : []);

	function slicePoints(r: Range, d: Candle[], intra: Candle[]): Candle[] {
		const now = Math.floor(Date.now() / 1000);
		if (r === '1D') return intra.length > 0 ? intra : d.slice(-1);
		if (r === '1W') return d.filter((c) => c.t >= now - 7 * 86400);
		if (r === '1M') return d.filter((c) => c.t >= now - 30 * 86400);
		if (r === '6M') return d.filter((c) => c.t >= now - 180 * 86400);
		if (r === '1Y') return d.filter((c) => c.t >= now - 365 * 86400);
		return d;
	}

	const points = $derived(slicePoints(range, daily, intraday));

	const firstPrice = $derived(points.length > 0 ? points[0].c : 0);
	const lastPrice = $derived(points.length > 0 ? points[points.length - 1].c : 0);
	const isUp = $derived(lastPrice >= firstPrice);
	const changePct = $derived(firstPrice > 0 ? ((lastPrice - firstPrice) / firstPrice) * 100 : 0);

	const minPrice = $derived(points.length > 0 ? Math.min(...points.map((p: Candle) => p.c)) : 0);
	const maxPrice = $derived(points.length > 0 ? Math.max(...points.map((p: Candle) => p.c)) : 0);
	const priceRange = $derived(maxPrice - minPrice || 1);

	const W = 600;
	const H = 200;
	const PAD = 4;

	function buildSvgPath(pts: Candle[], min: number, pRange: number): string {
		if (pts.length < 2) return '';
		return pts
			.map((p, i) => {
				const x = PAD + (i / (pts.length - 1)) * (W - PAD * 2);
				const y = PAD + (1 - (p.c - min) / pRange) * (H - PAD * 2);
				return `${i === 0 ? 'M' : 'L'}${x.toFixed(1)},${y.toFixed(1)}`;
			})
			.join(' ');
	}

	function buildFillPath(pts: Candle[], min: number, pRange: number): string {
		if (pts.length < 2) return '';
		const baseline = H;
		const first = `M${PAD},${baseline}`;
		const line = pts
			.map((p, i) => {
				const x = PAD + (i / (pts.length - 1)) * (W - PAD * 2);
				const y = PAD + (1 - (p.c - min) / pRange) * (H - PAD * 2);
				return `L${x.toFixed(1)},${y.toFixed(1)}`;
			})
			.join(' ');
		const lastX = PAD + ((pts.length - 1) / (pts.length - 1)) * (W - PAD * 2);
		return `${first} ${line} L${lastX},${baseline} Z`;
	}

	const svgPath = $derived(buildSvgPath(points, minPrice, priceRange));
	const fillPath = $derived(buildFillPath(points, minPrice, priceRange));

	const hoverPoint = $derived(hoverIdx !== null && hoverIdx < points.length ? points[hoverIdx] : null);
	const hoverX = $derived(hoverIdx !== null ? PAD + (hoverIdx / (points.length - 1)) * (W - PAD * 2) : 0);
	const hoverY = $derived(
		hoverPoint ? PAD + (1 - (hoverPoint.c - minPrice) / priceRange) * (H - PAD * 2) : 0
	);

	function formatPrice(v: number): string {
		return v.toLocaleString('en-US', { style: 'currency', currency: 'USD', minimumFractionDigits: 2 });
	}

	function formatDate(ts: number, r: Range): string {
		const d = new Date(ts * 1000);
		if (r === '1D') return d.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' });
		if (r === '1W' || r === '1M') return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
		return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: '2-digit' });
	}

	function onMouseMove(e: MouseEvent) {
		const svg = (e.currentTarget as SVGElement).getBoundingClientRect();
		const relX = e.clientX - svg.left;
		const ratio = relX / svg.width;
		const idx = Math.round(ratio * (points.length - 1));
		hoverIdx = Math.max(0, Math.min(points.length - 1, idx));
	}

	function onMouseLeave() {
		hoverIdx = null;
	}
</script>

<div class="card" class:up={isUp} class:down={!isUp}>
	{#if data.error}
		<div class="error">{data.error}</div>
	{:else}
		<div class="head">
			<div class="left">
				<span class="ticker">{data.ticker ?? 'Ticker'}</span>
				<span class="price">{formatPrice(hoverPoint ? hoverPoint.c : lastPrice)}</span>
				{#if hoverPoint}
					<span class="date-label">{formatDate(hoverPoint.t, range)}</span>
				{:else}
					<span class="delta" class:gain={isUp} class:loss={!isUp}>
						{isUp ? '+' : ''}{changePct.toFixed(2)}% {range}
					</span>
				{/if}
			</div>
			<div class="ranges">
				{#each ranges as r}
					<button
						class="range-btn"
						class:active={range === r}
						class:up-active={range === r && isUp}
						class:down-active={range === r && !isUp}
						onclick={() => (range = r)}
					>{r}</button>
				{/each}
			</div>
		</div>

		<div class="chart-wrap">
			{#if points.length >= 2}
				<svg
					viewBox="0 0 {W} {H}"
					preserveAspectRatio="none"
					class="chart-svg"
					onmousemove={onMouseMove}
					onmouseleave={onMouseLeave}
					role="img"
				>
					<defs>
						<linearGradient id="fill-{data.ticker}-{range}" x1="0" y1="0" x2="0" y2="1">
							<stop offset="0%" stop-color={isUp ? '#00ff41' : '#ff4444'} stop-opacity="0.18" />
							<stop offset="100%" stop-color={isUp ? '#00ff41' : '#ff4444'} stop-opacity="0" />
						</linearGradient>
					</defs>
					<path d={fillPath} fill="url(#fill-{data.ticker}-{range})" />
					<path d={svgPath} fill="none" stroke={isUp ? '#00ff41' : '#ff4444'} stroke-width="2" stroke-linejoin="round" stroke-linecap="round" />
					{#if hoverIdx !== null}
						<line x1={hoverX} y1="0" x2={hoverX} y2={H} stroke="#ffffff20" stroke-width="1" />
						<circle cx={hoverX} cy={hoverY} r="4" fill={isUp ? '#00ff41' : '#ff4444'} stroke="#000" stroke-width="2" />
					{/if}
				</svg>
			{:else}
				<div class="no-data">No chart data for this range</div>
			{/if}
		</div>
	{/if}
</div>

<style>
	.card {
		background: #0a0a0a;
		border: 1px solid #1a1a1a;
		border-radius: 10px;
		padding: 14px;
		--accent: #888;
	}
	.card.up { --accent: #00ff41; }
	.card.down { --accent: #ff4444; }

	.head {
		display: flex;
		justify-content: space-between;
		align-items: flex-start;
		gap: 10px;
		margin-bottom: 10px;
	}
	.left {
		display: flex;
		align-items: baseline;
		gap: 10px;
		flex-wrap: wrap;
	}
	.ticker {
		font-size: 18px;
		font-weight: 600;
	}
	.price {
		font-size: 18px;
		font-weight: 500;
		font-variant-numeric: tabular-nums;
	}
	.delta {
		font-size: 13px;
		font-weight: 500;
	}
	.date-label {
		font-size: 12px;
		color: #888;
	}
	.gain { color: #00ff41; }
	.loss { color: #ff4444; }

	.ranges {
		display: flex;
		gap: 2px;
		flex-shrink: 0;
	}
	.range-btn {
		background: transparent;
		border: 1px solid transparent;
		color: #666;
		font-size: 11px;
		font-weight: 600;
		padding: 4px 8px;
		border-radius: 6px;
		cursor: pointer;
		font-family: inherit;
		transition: color 0.12s, background 0.12s, border-color 0.12s;
	}
	.range-btn:hover {
		color: #aaa;
		background: #151515;
	}
	.range-btn.active {
		color: var(--accent);
		background: #111;
		border-color: #222;
	}
	.range-btn.up-active {
		background: #00ff4108;
		border-color: #00ff4125;
	}
	.range-btn.down-active {
		background: #ff444408;
		border-color: #ff444425;
	}

	.chart-wrap {
		width: 100%;
		aspect-ratio: 3 / 1;
		position: relative;
	}
	.chart-svg {
		width: 100%;
		height: 100%;
		display: block;
		cursor: crosshair;
	}
	.no-data {
		display: grid;
		place-content: center;
		height: 100%;
		font-size: 13px;
		color: #555;
	}
	.error {
		color: #ff6b6b;
		font-size: 13px;
	}
</style>
