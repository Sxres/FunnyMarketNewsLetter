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

	const mockStocks = [
		{ ticker: 'AAPL', name: 'Apple Inc.', price: 198.11, change: +2.34, pct: +1.19 },
		{ ticker: 'NVDA', name: 'NVIDIA Corp.', price: 881.86, change: -12.40, pct: -1.39 },
		{ ticker: 'TSLA', name: 'Tesla Inc.', price: 177.48, change: +5.91, pct: +3.44 },
		{ ticker: 'MSFT', name: 'Microsoft Corp.', price: 428.50, change: +0.72, pct: +0.17 },
		{ ticker: 'AMZN', name: 'Amazon.com Inc.', price: 186.21, change: -1.08, pct: -0.58 },
		{ ticker: 'META', name: 'Meta Platforms', price: 504.79, change: +8.63, pct: +1.74 },
		{ ticker: 'GOOG', name: 'Alphabet Inc.', price: 174.13, change: -0.22, pct: -0.13 },
		{ ticker: 'AMD', name: 'AMD Inc.', price: 162.55, change: +4.10, pct: +2.59 },
	];

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
	<Sidebar activeTab="watchlist" onNavigate={navigateTab} />
	<main class="main">
		<div class="terminal">
			<div class="header">
				<div class="title-block">
					<h1>Watchlist</h1>
					<span class="sub">Track your favorite tickers in real time</span>
				</div>
				<div class="header-actions">
					<div class="search-mock">
						<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>
						<span>Search ticker...</span>
					</div>
				</div>
			</div>

			<div class="table-wrap">
				<div class="table-header">
					<span>Ticker</span>
					<span>Name</span>
					<span class="right">Price</span>
					<span class="right">Change</span>
					<span class="right">%</span>
					<span class="right">Action</span>
				</div>
				{#each mockStocks as stock, i}
					<div class="table-row" style="animation-delay: {i * 60}ms">
						<span class="ticker">{stock.ticker}</span>
						<span class="name">{stock.name}</span>
						<span class="right price">${stock.price.toFixed(2)}</span>
						<span class="right" class:gain={stock.change >= 0} class:loss={stock.change < 0}>
							{stock.change >= 0 ? '+' : ''}{stock.change.toFixed(2)}
						</span>
						<span class="right" class:gain={stock.pct >= 0} class:loss={stock.pct < 0}>
							{stock.pct >= 0 ? '+' : ''}{stock.pct.toFixed(2)}%
						</span>
						<span class="right">
							<button class="remove-btn" tabindex="-1">&times;</button>
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
		display: flex;
		justify-content: space-between;
		align-items: flex-end;
		margin-bottom: 32px;
		gap: 16px;
	}
	.title-block h1 {
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
	.search-mock {
		display: flex;
		align-items: center;
		gap: 8px;
		padding: 8px 14px;
		border: 1px solid #1e1e1e;
		border-radius: 8px;
		color: #4a4a4a;
		font-size: 13px;
		background: #060606;
	}
	.search-mock svg {
		width: 14px;
		height: 14px;
		opacity: 0.5;
	}

	.table-wrap {
		border: 1px solid #141414;
		border-radius: 10px;
		overflow: hidden;
		background: #050505;
	}
	.table-header {
		display: grid;
		grid-template-columns: 80px 1fr 100px 90px 80px 60px;
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
		grid-template-columns: 80px 1fr 100px 90px 80px 60px;
		padding: 12px 16px;
		font-size: 13px;
		border-bottom: 1px solid #0e0e0e;
		animation: fadeSlide 0.4s ease both;
		transition: background 0.15s;
	}
	.table-row:last-child {
		border-bottom: none;
	}
	.table-row:hover {
		background: #0a0a0a;
	}
	.ticker {
		font-weight: 600;
		color: #d4af37;
	}
	.name {
		color: #888;
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}
	.price {
		font-variant-numeric: tabular-nums;
	}
	.right {
		text-align: right;
	}
	.gain { color: #00ff41; }
	.loss { color: #ff4444; }

	.remove-btn {
		background: none;
		border: none;
		color: #333;
		font-size: 16px;
		cursor: default;
		padding: 0 4px;
	}

	@keyframes fadeSlide {
		from { opacity: 0; transform: translateY(6px); }
		to { opacity: 1; transform: translateY(0); }
	}

	@media (max-width: 900px) {
		.app {
			flex-direction: column;
			height: 100dvh;
		}
		.terminal {
			padding: 24px 16px;
		}
		.header {
			flex-direction: column;
			align-items: flex-start;
		}
		.table-header,
		.table-row {
			grid-template-columns: 70px 1fr 90px 70px;
		}
		.table-header span:nth-child(5),
		.table-header span:nth-child(6),
		.table-row span:nth-child(5),
		.table-row span:nth-child(6) {
			display: none;
		}
	}
</style>
