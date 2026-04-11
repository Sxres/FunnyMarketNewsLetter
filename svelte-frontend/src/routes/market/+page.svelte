<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import { goto } from '$app/navigation';
	import { supabase } from '$lib/supabase';
	import Sidebar from '$lib/components/Sidebar.svelte';

	type NavTab = 'chat' | 'watchlist' | 'portfolio' | 'market' | 'settings';

	function navigateTab(tab: NavTab) {
		const route: Record<NavTab, string> = {
			chat: '/chat',
			watchlist: '/watchlist',
			portfolio: '/portfolio',
			market: '/market',
			settings: '/settings'
		};
		goto(route[tab]);
	}

	const indices = [
		{ name: 'S&P 500', value: '5,248.49', change: '+0.58%', up: true },
		{ name: 'NASDAQ', value: '16,399.52', change: '-0.23%', up: false },
		{ name: 'DOW', value: '39,170.35', change: '+0.34%', up: true },
		{ name: 'Russell 2000', value: '2,072.84', change: '-0.91%', up: false },
	];

	const sectors = [
		{ name: 'Technology', pct: +1.42, width: 72 },
		{ name: 'Healthcare', pct: -0.38, width: 19 },
		{ name: 'Financials', pct: +0.91, width: 46 },
		{ name: 'Energy', pct: -1.24, width: 62 },
		{ name: 'Consumer Disc.', pct: +0.67, width: 34 },
		{ name: 'Industrials', pct: +0.22, width: 11 },
	];

	const movers = [
		{ ticker: 'SMCI', pct: +12.4, up: true },
		{ ticker: 'RIVN', pct: +8.7, up: true },
		{ ticker: 'PLTR', pct: +6.1, up: true },
		{ ticker: 'COIN', pct: -7.3, up: false },
		{ ticker: 'SNAP', pct: -5.8, up: false },
		{ ticker: 'BABA', pct: -4.2, up: false },
	];

	// Generate mock sparkline SVG path
	function sparkPath(seed: number): string {
		const pts: number[] = [];
		let y = 20 + (seed % 10);
		for (let i = 0; i < 20; i++) {
			y += (Math.sin(seed * 0.7 + i * 0.8) * 4) + (Math.cos(i * 1.3) * 2);
			y = Math.max(4, Math.min(36, y));
			pts.push(y);
		}
		return 'M' + pts.map((v, i) => `${i * (80 / 19)},${v}`).join(' L');
	}

	let authUnsub: (() => void) | null = null;
	onMount(async () => {
		const { data: { session } } = await supabase.auth.getSession();
		if (!session) {
			goto('/login');
			return;
		}
		const { data } = supabase.auth.onAuthStateChange((_event, s) => {
			if (!s?.access_token) goto('/login');
		});
		authUnsub = () => data.subscription.unsubscribe();
	});
	onDestroy(() => authUnsub?.());
</script>

<div class="app">
	<Sidebar activeTab="market" onNavigate={navigateTab} />
	<main class="main">
		<div class="terminal">
			<div class="header">
				<h1>Market</h1>
				<span class="sub">Indices, sectors, and top movers</span>
			</div>

			<div class="indices-grid">
				{#each indices as idx, i}
					<div class="index-card" style="animation-delay: {i * 50}ms">
						<div class="idx-head">
							<span class="idx-name">{idx.name}</span>
							<svg class="spark" viewBox="0 0 80 40">
								<path d={sparkPath(i * 7 + 3)} fill="none" stroke={idx.up ? '#00ff41' : '#ff4444'} stroke-width="1.5" stroke-linecap="round"/>
							</svg>
						</div>
						<div class="idx-value">{idx.value}</div>
						<div class="idx-change" class:gain={idx.up} class:loss={!idx.up}>{idx.change}</div>
					</div>
				{/each}
			</div>

			<div class="two-col">
				<div class="panel">
					<div class="panel-title">Sector Performance</div>
					<div class="sectors">
						{#each sectors as sec, i}
							<div class="sector-row" style="animation-delay: {i * 40 + 200}ms">
								<span class="sec-name">{sec.name}</span>
								<div class="sec-bar-wrap">
									<div
										class="sec-bar"
										class:up={sec.pct >= 0}
										class:down={sec.pct < 0}
										style="width: {sec.width}%;"
									></div>
								</div>
								<span class="sec-pct" class:gain={sec.pct >= 0} class:loss={sec.pct < 0}>
									{sec.pct >= 0 ? '+' : ''}{sec.pct.toFixed(2)}%
								</span>
							</div>
						{/each}
					</div>
				</div>

				<div class="panel">
					<div class="panel-title">Top Movers</div>
					<div class="movers">
						{#each movers as m, i}
							<div class="mover" style="animation-delay: {i * 40 + 200}ms">
								<span class="m-ticker">{m.ticker}</span>
								<span class:gain={m.up} class:loss={!m.up}>
									{m.up ? '+' : ''}{m.pct.toFixed(1)}%
								</span>
							</div>
						{/each}
					</div>
				</div>
			</div>

		</div>
	</main>
</div>

<style>
	.app {
		display: flex;
		height: 100vh;
		background: #000;
		color: #eaeaea;
		font-family: 'Overused Grotesk', 'Segoe UI', system-ui, sans-serif;
	}
	.main {
		flex: 1;
		overflow-y: auto;
		position: relative;
	}
	.terminal {
		max-width: 960px;
		margin: 0 auto;
		padding: 40px 32px;
	}
	.header {
		margin-bottom: 28px;
	}
	.header h1 {
		margin: 0;
		font-size: 28px;
		font-weight: 500;
		letter-spacing: -0.02em;
	}
	.sub {
		font-size: 13px;
		color: #6b6b6b;
		margin-top: 4px;
		display: block;
	}

	.indices-grid {
		display: grid;
		grid-template-columns: repeat(4, 1fr);
		gap: 12px;
		margin-bottom: 28px;
	}
	.index-card {
		background: #060606;
		border: 1px solid #161616;
		border-radius: 10px;
		padding: 14px;
		animation: fadeSlide 0.4s ease both;
	}
	.idx-head {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 8px;
	}
	.idx-name {
		font-size: 12px;
		color: #777;
		font-weight: 500;
	}
	.spark {
		width: 60px;
		height: 28px;
	}
	.idx-value {
		font-size: 20px;
		font-weight: 500;
		font-variant-numeric: tabular-nums;
	}
	.idx-change {
		font-size: 13px;
		margin-top: 2px;
	}

	.two-col {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 14px;
	}
	.panel {
		background: #060606;
		border: 1px solid #161616;
		border-radius: 10px;
		padding: 16px;
	}
	.panel-title {
		font-size: 13px;
		font-weight: 500;
		color: #999;
		margin-bottom: 14px;
	}

	.sectors {
		display: flex;
		flex-direction: column;
		gap: 10px;
	}
	.sector-row {
		display: grid;
		grid-template-columns: 110px 1fr 60px;
		align-items: center;
		gap: 10px;
		animation: fadeSlide 0.35s ease both;
	}
	.sec-name {
		font-size: 12px;
		color: #aaa;
	}
	.sec-bar-wrap {
		height: 6px;
		background: #111;
		border-radius: 999px;
		overflow: hidden;
	}
	.sec-bar {
		height: 100%;
		border-radius: 999px;
		transition: width 0.6s ease;
	}
	.sec-bar.up { background: #00ff41; }
	.sec-bar.down { background: #ff4444; }
	.sec-pct {
		font-size: 12px;
		text-align: right;
		font-variant-numeric: tabular-nums;
	}

	.movers {
		display: flex;
		flex-direction: column;
		gap: 8px;
	}
	.mover {
		display: flex;
		justify-content: space-between;
		padding: 8px 10px;
		border-radius: 6px;
		background: #0a0a0a;
		font-size: 13px;
		animation: fadeSlide 0.35s ease both;
	}
	.m-ticker {
		font-weight: 600;
		color: #ccc;
	}
	.gain { color: #00ff41; }
	.loss { color: #ff4444; }

	@keyframes fadeSlide {
		from { opacity: 0; transform: translateY(6px); }
		to { opacity: 1; transform: translateY(0); }
	}

	@media (max-width: 900px) {
		.app {
			flex-direction: column;
			height: 100dvh;
		}
		.terminal { padding: 24px 16px; }
		.indices-grid { grid-template-columns: repeat(2, 1fr); }
		.two-col { grid-template-columns: 1fr; }
		.sector-row { grid-template-columns: 90px 1fr 50px; }
	}
</style>
