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

	const mockHoldings = [
		{ ticker: 'AAPL', shares: 50, avgCost: 172.30, current: 198.11, color: '#d4af37' },
		{ ticker: 'NVDA', shares: 20, avgCost: 450.00, current: 881.86, color: '#00ff41' },
		{ ticker: 'TSLA', shares: 30, avgCost: 210.50, current: 177.48, color: '#ff4444' },
		{ ticker: 'MSFT', shares: 15, avgCost: 380.00, current: 428.50, color: '#4a9eff' },
		{ ticker: 'AMD', shares: 40, avgCost: 120.00, current: 162.55, color: '#b44aff' },
	];

	const totalValue = $derived(mockHoldings.reduce((s, h) => s + h.shares * h.current, 0));
	const totalCost = $derived(mockHoldings.reduce((s, h) => s + h.shares * h.avgCost, 0));
	const totalPnl = $derived(totalValue - totalCost);
	const totalPnlPct = $derived(totalCost > 0 ? (totalPnl / totalCost) * 100 : 0);

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
	<Sidebar
		activeTab="portfolio"
		onNavigate={navigateTab}
		onSignOut={async () => {
			await supabase.auth.signOut();
			goto('/');
		}}
	/>
	<main class="main">
		<div class="terminal">
			<div class="header">
				<h1>Portfolio</h1>
				<span class="sub">Holdings, P&L, and allocation at a glance</span>
			</div>

			<div class="summary-row">
				<div class="summary-card">
					<div class="label">Total Value</div>
					<div class="big-num">${totalValue.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</div>
				</div>
				<div class="summary-card">
					<div class="label">Total P&L</div>
					<div class="big-num" class:gain={totalPnl >= 0} class:loss={totalPnl < 0}>
						{totalPnl >= 0 ? '+' : ''}${Math.abs(totalPnl).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
					</div>
					<div class="pct" class:gain={totalPnlPct >= 0} class:loss={totalPnlPct < 0}>
						{totalPnlPct >= 0 ? '+' : ''}{totalPnlPct.toFixed(2)}%
					</div>
				</div>
				<div class="summary-card">
					<div class="label">Positions</div>
					<div class="big-num">{mockHoldings.length}</div>
				</div>
			</div>

			<div class="alloc-bar">
				{#each mockHoldings as h}
					{@const weight = (h.shares * h.current) / totalValue * 100}
					<div
						class="alloc-seg"
						style="width: {weight}%; background: {h.color};"
						title="{h.ticker}: {weight.toFixed(1)}%"
					></div>
				{/each}
			</div>
			<div class="alloc-legend">
				{#each mockHoldings as h}
					{@const weight = (h.shares * h.current) / totalValue * 100}
					<span><span class="dot" style="background: {h.color};"></span>{h.ticker} {weight.toFixed(1)}%</span>
				{/each}
			</div>

			<div class="table-wrap">
				<div class="table-header">
					<span>Ticker</span>
					<span class="right">Shares</span>
					<span class="right">Avg Cost</span>
					<span class="right">Current</span>
					<span class="right">P&L</span>
				</div>
				{#each mockHoldings as h, i}
					{@const pnl = (h.current - h.avgCost) * h.shares}
					{@const pnlPct = ((h.current - h.avgCost) / h.avgCost) * 100}
					<div class="table-row" style="animation-delay: {i * 60}ms">
						<span class="ticker" style="color: {h.color};">{h.ticker}</span>
						<span class="right">{h.shares}</span>
						<span class="right dim">${h.avgCost.toFixed(2)}</span>
						<span class="right">${h.current.toFixed(2)}</span>
						<span class="right" class:gain={pnl >= 0} class:loss={pnl < 0}>
							{pnl >= 0 ? '+' : ''}${Math.abs(pnl).toFixed(0)} ({pnlPct >= 0 ? '+' : ''}{pnlPct.toFixed(1)}%)
						</span>
					</div>
				{/each}
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

	.summary-row {
		display: grid;
		grid-template-columns: repeat(3, 1fr);
		gap: 14px;
		margin-bottom: 28px;
	}
	.summary-card {
		background: #060606;
		border: 1px solid #161616;
		border-radius: 10px;
		padding: 16px;
	}
	.label {
		font-size: 11px;
		text-transform: uppercase;
		letter-spacing: 0.06em;
		color: #555;
		margin-bottom: 6px;
	}
	.big-num {
		font-size: 24px;
		font-weight: 500;
		font-variant-numeric: tabular-nums;
		line-height: 1.1;
	}
	.pct {
		font-size: 13px;
		margin-top: 4px;
	}
	.gain { color: #00ff41; }
	.loss { color: #ff4444; }

	.alloc-bar {
		display: flex;
		height: 8px;
		border-radius: 999px;
		overflow: hidden;
		gap: 2px;
		margin-bottom: 10px;
	}
	.alloc-seg {
		border-radius: 999px;
		opacity: 0.85;
		transition: opacity 0.15s;
	}
	.alloc-legend {
		display: flex;
		flex-wrap: wrap;
		gap: 12px;
		font-size: 11px;
		color: #777;
		margin-bottom: 28px;
	}
	.dot {
		display: inline-block;
		width: 8px;
		height: 8px;
		border-radius: 50%;
		margin-right: 5px;
		vertical-align: middle;
	}

	.table-wrap {
		border: 1px solid #141414;
		border-radius: 10px;
		overflow: hidden;
		background: #050505;
	}
	.table-header {
		display: grid;
		grid-template-columns: 80px repeat(4, 1fr);
		padding: 10px 16px;
		font-size: 11px;
		text-transform: uppercase;
		letter-spacing: 0.06em;
		color: #4a4a4a;
		border-bottom: 1px solid #141414;
		background: #080808;
	}
	.table-row {
		display: grid;
		grid-template-columns: 80px repeat(4, 1fr);
		padding: 12px 16px;
		font-size: 13px;
		border-bottom: 1px solid #0e0e0e;
		animation: fadeSlide 0.4s ease both;
	}
	.table-row:last-child { border-bottom: none; }
	.ticker { font-weight: 600; }
	.right { text-align: right; }
	.dim { color: #666; }

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
		.summary-row { grid-template-columns: 1fr; }
		.table-header, .table-row {
			grid-template-columns: 70px 1fr 1fr;
		}
		.table-header span:nth-child(3),
		.table-header span:nth-child(4),
		.table-row span:nth-child(3),
		.table-row span:nth-child(4) {
			display: none;
		}
	}
</style>
