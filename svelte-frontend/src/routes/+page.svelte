<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import { goto } from '$app/navigation';
	import { supabase } from '$lib/supabase';

	let mode = $state<'professional' | 'wsb'>('professional');
	let loaded = $state(false);
	let tickerOffset = $state(0);
	let tickerFrame: number;

	const tickerItems = [
		'AAPL +2.4%', 'NVDA +5.1%', 'TSLA -1.8%', 'MSFT +0.9%', 'AMZN +3.2%',
		'GME +42.0%', 'META +1.1%', 'GOOG -0.3%', 'SPY +0.7%', 'AMD +4.6%',
		'PLTR +8.2%', 'COIN -2.1%', 'SOFI +3.7%', 'RIVN -4.5%', 'DIS +1.3%'
	];

	const features = [
		{
			title: 'Real-time Pulse',
			desc: 'Live price action and deep fundamentals delivered instantly.',
			pro: 'Institutional-grade data accuracy.',
			wsb: 'WATCH THE CANDLES BLEED OR MOON IN REAL-TIME.',
			icon: '◎'
		},
		{
			title: 'Insider Intel',
			desc: 'Track what the C-suite is doing with their own money.',
			pro: 'Analyze executive sentiment and ownership trends.',
			wsb: 'FOLLOW THE SMART MONEY BEFORE THE ROCKET LAUNCHES.',
			icon: '⬡'
		},
		{
			title: 'Wall St. Consensus',
			desc: 'Aggregated analyst ratings and price targets.',
			pro: 'Sift through consensus to find alpha.',
			wsb: 'SEE WHICH SUITS ARE WRONG ABOUT YOUR STONKS.',
			icon: '△'
		},
		{
			title: 'Agentic RAG',
			desc: 'AI that searches the web and cites its sources.',
			pro: 'Synthesized reports with verifiable citations.',
			wsb: 'A BOT THAT READS THE NEWS SO YOU CAN KEEP GAMBLING.',
			icon: '◇'
		}
	];

	function animateTicker() {
		tickerOffset -= 0.5;
		if (tickerOffset < -2400) tickerOffset = 0;
		tickerFrame = requestAnimationFrame(animateTicker);
	}

	onMount(async () => {
		const { data: { session } } = await supabase.auth.getSession();
		if (session) { goto('/chat'); return; }

		requestAnimationFrame(() => { loaded = true; });
		animateTicker();
	});

	onDestroy(() => {
		if (tickerFrame) cancelAnimationFrame(tickerFrame);
	});
</script>

<div class="page" class:wsb={mode === 'wsb'} class:loaded>

	<!-- Scanlines overlay -->
	<div class="scanlines" aria-hidden="true"></div>

	<!-- Ticker tape -->
	<div class="ticker" aria-hidden="true">
		<div class="ticker-track" style="transform: translateX({tickerOffset}px)">
			{#each [...tickerItems, ...tickerItems, ...tickerItems] as item}
				<span class="ticker-item" class:up={item.includes('+')} class:down={item.includes('-')}>{item}</span>
			{/each}
		</div>
	</div>

	<!-- Hero -->
	<section class="hero">
		<div class="hero-inner">
			<div class="hero-left">
				<div class="tag">
					<span class="tag-dot"></span>
					{mode === 'professional' ? 'LIVE ANALYSIS ENGINE' : 'DEGEN TERMINAL v4.20'}
				</div>

				<h1 class="title">
					<span class="t1">MARKET</span>
					<span class="t2">CHAT</span>
				</h1>

				<p class="subtitle">
					{#if mode === 'professional'}
						Real-time stock analysis powered by agentic AI.
						Fundamentals, insider trades, analyst consensus — cited and verified.
					{:else}
						THE ONLY TERMINAL THAT SPEAKS FLUENT REGARD.
						TENDIES OR ROPE. NO IN BETWEEN.
					{/if}
				</p>

				<div class="actions">
					<a href="/signup" class="btn-main">
						{mode === 'professional' ? 'Get Started' : 'APE IN'}
						<span class="btn-arrow">→</span>
					</a>
					<a href="/login" class="btn-ghost">Sign In</a>
				</div>
			</div>

			<div class="hero-right">
				<!-- Mode toggle card -->
				<div class="mode-card">
					<div class="mode-card-label">PERSONALITY</div>
					<div class="mode-toggle" role="radiogroup" aria-label="Analysis mode">
						<button
							class="mode-opt"
							class:active={mode === 'professional'}
							role="radio"
							aria-checked={mode === 'professional'}
							onclick={() => mode = 'professional'}
						>
							<span class="mode-name">PRO</span>
							<span class="mode-desc">Analytical</span>
						</button>
						<button
							class="mode-opt"
							class:active={mode === 'wsb'}
							role="radio"
							aria-checked={mode === 'wsb'}
							onclick={() => mode = 'wsb'}
						>
							<span class="mode-name">WSB</span>
							<span class="mode-desc">Degenerate</span>
						</button>
					</div>

					<!-- Preview bubble -->
					<div class="preview">
						<div class="preview-label">
							{mode === 'professional' ? '> sample output' : '> sample_output.exe'}
						</div>
						<p class="preview-text">
							{#if mode === 'professional'}
								NVDA trades at 38.2x forward P/E with 94% gross margins on datacenter. Consensus PT $152 implies 18% upside. Insider selling remains minimal.
							{:else}
								NVDA IS LITERALLY PRINTING MONEY. 94% MARGINS?? JENSEN IS A GOD. BEARS ARE FINANCIALLY RUINED. $200 EOW IS NOT A MEME. 🚀🚀🚀
							{/if}
						</p>
					</div>
				</div>
			</div>
		</div>
	</section>

	<!-- Features -->
	<section class="features">
		<div class="features-header">
			<span class="section-tag">
				{mode === 'professional' ? '[ CAPABILITIES ]' : '[ WEAPONS OF MASS GAINS ]'}
			</span>
			<h2 class="features-title">
				{mode === 'professional' ? 'Everything you need to dominate the tape.' : 'STOP LOSING MONEY, START HERE.'}
			</h2>
		</div>

		<div class="grid">
			{#each features as f, i}
				<div class="card" style="--delay: {i * 80}ms">
					<div class="card-icon">{f.icon}</div>
					<h3 class="card-title">{f.title}</h3>
					<p class="card-desc">{f.desc}</p>
					<div class="card-divider"></div>
					<p class="card-mode">
						{mode === 'professional' ? f.pro : f.wsb}
					</p>
				</div>
			{/each}
		</div>
	</section>

	<!-- Footer -->
	<footer class="foot">
		<div class="foot-line"></div>
		<p>© {new Date().getFullYear()} Market Chat — NOT FINANCIAL ADVICE</p>
	</footer>
</div>

<style>
	/* ── Base ─────────────────────────────────────────────── */
	.page {
		min-height: 100vh;
		background: #000;
		color: #eaeaea;
		position: relative;
		overflow-x: hidden;
	}

	/* ── Scanlines ────────────────────────────────────────── */
	.scanlines {
		position: fixed;
		inset: 0;
		pointer-events: none;
		z-index: 50;
		background: repeating-linear-gradient(
			0deg,
			transparent,
			transparent 2px,
			rgba(0, 0, 0, 0.03) 2px,
			rgba(0, 0, 0, 0.03) 4px
		);
	}

	/* ── Ticker ───────────────────────────────────────────── */
	.ticker {
		position: relative;
		z-index: 10;
		border-bottom: 1px solid #1a1a1a;
		padding: 10px 0;
		overflow: hidden;
		background: #050505;
		opacity: 0;
		transition: opacity 0.6s ease 0.1s;
	}
	.loaded .ticker { opacity: 1; }

	.ticker-track {
		display: flex;
		gap: 40px;
		white-space: nowrap;
		will-change: transform;
	}

	.ticker-item {
		font-size: 11px;
		letter-spacing: 0.12em;
		font-weight: 500;
		color: #555;
		font-variant-numeric: tabular-nums;
	}
	.ticker-item.up { color: #22c55e; }
	.ticker-item.down { color: #ef4444; }

	.wsb .ticker { border-bottom-color: #0a2a0a; background: #010a01; }
	.wsb .ticker-item { color: #336633; }
	.wsb .ticker-item.up { color: #00ff41; }
	.wsb .ticker-item.down { color: #ff3333; }

	/* ── Hero ─────────────────────────────────────────────── */
	.hero {
		min-height: calc(100vh - 41px);
		display: flex;
		align-items: center;
		padding: 80px 6% 60px;
	}

	.hero-inner {
		display: flex;
		align-items: center;
		gap: 80px;
		width: 100%;
		max-width: 1240px;
		margin: 0 auto;
	}

	.hero-left {
		flex: 1;
		min-width: 0;
		opacity: 0;
		transform: translateY(24px);
		transition: opacity 0.7s ease 0.15s, transform 0.7s ease 0.15s;
	}
	.loaded .hero-left {
		opacity: 1;
		transform: translateY(0);
	}

	.hero-right {
		flex: 0 0 420px;
		opacity: 0;
		transform: translateY(24px);
		transition: opacity 0.7s ease 0.35s, transform 0.7s ease 0.35s;
	}
	.loaded .hero-right {
		opacity: 1;
		transform: translateY(0);
	}

	.tag {
		display: inline-flex;
		align-items: center;
		gap: 8px;
		font-size: 11px;
		letter-spacing: 0.2em;
		color: #666;
		text-transform: uppercase;
		margin-bottom: 32px;
	}
	.tag-dot {
		width: 6px;
		height: 6px;
		border-radius: 50%;
		background: #d4af37;
		animation: blink-dot 2s infinite;
	}
	.wsb .tag-dot { background: #00ff41; }

	@keyframes blink-dot {
		0%, 100% { opacity: 1; }
		50% { opacity: 0.3; }
	}

	.title {
		font-size: clamp(4.5rem, 9vw, 8rem);
		font-weight: 500;
		line-height: 0.88;
		letter-spacing: -0.04em;
		margin: 0 0 28px;
	}
	.t1 {
		display: block;
		color: #eaeaea;
	}
	.t2 {
		display: block;
		color: #d4af37;
		transition: color 0.4s ease, text-shadow 0.4s ease, transform 0.4s ease;
	}
	.wsb .t2 {
		color: #00ff41;
		text-shadow: 0 0 40px rgba(0, 255, 65, 0.4);
		transform: skewX(-3deg);
	}

	.subtitle {
		font-size: 16px;
		line-height: 1.65;
		color: #777;
		max-width: 460px;
		margin: 0 0 40px;
		transition: color 0.3s ease;
	}
	.wsb .subtitle {
		color: #558855;
		font-weight: 500;
		letter-spacing: 0.02em;
	}

	/* ── Buttons ──────────────────────────────────────────── */
	.actions {
		display: flex;
		gap: 16px;
		align-items: center;
	}

	.btn-main {
		display: inline-flex;
		align-items: center;
		gap: 10px;
		padding: 14px 28px;
		background: #eaeaea;
		color: #000;
		text-decoration: none;
		font-size: 14px;
		font-weight: 500;
		letter-spacing: 0.03em;
		border-radius: 6px;
		transition: background 0.2s ease, transform 0.15s ease, box-shadow 0.2s ease;
	}
	.btn-main:hover {
		background: #fff;
		transform: translateY(-1px);
		box-shadow: 0 4px 20px rgba(255, 255, 255, 0.1);
	}
	.btn-main:active { transform: translateY(0); }
	.btn-arrow {
		transition: transform 0.2s ease;
	}
	.btn-main:hover .btn-arrow { transform: translateX(3px); }

	.wsb .btn-main {
		background: #00ff41;
		color: #000;
		font-weight: 600;
	}
	.wsb .btn-main:hover {
		background: #33ff66;
		box-shadow: 0 4px 30px rgba(0, 255, 65, 0.25);
	}

	.btn-ghost {
		display: inline-flex;
		align-items: center;
		padding: 14px 24px;
		background: transparent;
		color: #666;
		text-decoration: none;
		font-size: 14px;
		font-weight: 500;
		letter-spacing: 0.03em;
		border: 1px solid #222;
		border-radius: 6px;
		transition: color 0.2s ease, border-color 0.2s ease;
	}
	.btn-ghost:hover {
		color: #eaeaea;
		border-color: #444;
	}

	/* ── Mode Card ────────────────────────────────────────── */
	.mode-card {
		background: #080808;
		border: 1px solid #1a1a1a;
		border-radius: 10px;
		padding: 24px;
		transition: border-color 0.3s ease, box-shadow 0.3s ease;
	}
	.mode-card:hover {
		border-color: #2a2a2a;
	}
	.wsb .mode-card {
		border-color: #0a2a0a;
		box-shadow: 0 0 60px rgba(0, 255, 65, 0.03);
	}
	.wsb .mode-card:hover {
		border-color: #1a3a1a;
	}

	.mode-card-label {
		font-size: 10px;
		letter-spacing: 0.2em;
		color: #444;
		margin-bottom: 14px;
	}

	.mode-toggle {
		display: flex;
		gap: 6px;
		margin-bottom: 20px;
	}

	.mode-opt {
		flex: 1;
		background: #0e0e0e;
		border: 1px solid #1a1a1a;
		border-radius: 6px;
		padding: 12px;
		cursor: pointer;
		text-align: center;
		transition: all 0.25s ease;
	}
	.mode-opt:hover {
		border-color: #333;
		background: #111;
	}
	.mode-opt.active {
		background: #eaeaea;
		color: #000;
		border-color: #eaeaea;
	}
	.wsb .mode-opt.active {
		background: #00ff41;
		border-color: #00ff41;
		color: #000;
	}

	.mode-name {
		display: block;
		font-size: 14px;
		font-weight: 600;
		letter-spacing: 0.08em;
	}
	.mode-desc {
		display: block;
		font-size: 10px;
		opacity: 0.6;
		margin-top: 2px;
		letter-spacing: 0.04em;
	}

	/* ── Preview ──────────────────────────────────────────── */
	.preview {
		background: #0a0a0a;
		border: 1px solid #151515;
		border-radius: 6px;
		padding: 16px;
	}
	.preview-label {
		font-size: 10px;
		font-family: 'SF Mono', 'Fira Code', Menlo, Consolas, monospace;
		color: #444;
		margin-bottom: 10px;
		letter-spacing: 0.05em;
	}
	.wsb .preview-label { color: #336633; }

	.preview-text {
		font-size: 12px;
		line-height: 1.7;
		color: #888;
		margin: 0;
		transition: color 0.3s ease;
	}
	.wsb .preview-text {
		color: #66aa66;
		font-weight: 500;
	}

	/* ── Features ─────────────────────────────────────────── */
	.features {
		padding: 100px 6% 80px;
		max-width: 1240px;
		margin: 0 auto;
		opacity: 0;
		transform: translateY(30px);
		transition: opacity 0.8s ease 0.5s, transform 0.8s ease 0.5s;
	}
	.loaded .features {
		opacity: 1;
		transform: translateY(0);
	}

	.features-header {
		margin-bottom: 52px;
	}

	.section-tag {
		font-size: 11px;
		letter-spacing: 0.2em;
		color: #444;
		display: block;
		margin-bottom: 14px;
		font-family: 'SF Mono', 'Fira Code', Menlo, Consolas, monospace;
	}
	.wsb .section-tag { color: #336633; }

	.features-title {
		font-size: clamp(1.8rem, 4vw, 2.8rem);
		font-weight: 500;
		letter-spacing: -0.02em;
		color: #eaeaea;
		margin: 0;
		max-width: 600px;
		line-height: 1.15;
	}

	.grid {
		display: grid;
		grid-template-columns: repeat(4, 1fr);
		gap: 16px;
	}

	.card {
		background: #080808;
		border: 1px solid #1a1a1a;
		border-radius: 8px;
		padding: 28px 24px;
		transition: border-color 0.25s ease, transform 0.25s ease, box-shadow 0.25s ease;
		opacity: 0;
		transform: translateY(16px);
		animation: card-in 0.5s ease forwards;
		animation-delay: calc(0.6s + var(--delay));
	}
	.loaded .card {
		animation-play-state: running;
	}

	@keyframes card-in {
		to {
			opacity: 1;
			transform: translateY(0);
		}
	}

	.card:hover {
		border-color: #2a2a2a;
		transform: translateY(-2px);
		box-shadow: 0 8px 30px rgba(0, 0, 0, 0.4);
	}
	.wsb .card:hover {
		border-color: #1a3a1a;
		box-shadow: 0 8px 30px rgba(0, 255, 65, 0.04);
	}

	.card-icon {
		font-size: 20px;
		color: #d4af37;
		margin-bottom: 16px;
		opacity: 0.8;
		transition: color 0.3s ease;
	}
	.wsb .card-icon { color: #00ff41; }

	.card-title {
		font-size: 16px;
		font-weight: 500;
		letter-spacing: -0.01em;
		margin: 0 0 8px;
		color: #eaeaea;
	}

	.card-desc {
		font-size: 13px;
		line-height: 1.6;
		color: #666;
		margin: 0 0 16px;
	}

	.card-divider {
		height: 1px;
		background: #1a1a1a;
		margin-bottom: 14px;
		transition: background 0.3s ease;
	}
	.wsb .card-divider { background: #0a2a0a; }

	.card-mode {
		font-size: 12px;
		line-height: 1.6;
		color: #d4af37;
		margin: 0;
		font-weight: 500;
		opacity: 0.85;
		transition: color 0.3s ease;
	}
	.wsb .card-mode {
		color: #00ff41;
		text-shadow: 0 0 8px rgba(0, 255, 65, 0.15);
	}

	/* ── Footer ───────────────────────────────────────────── */
	.foot {
		padding: 40px 6%;
		max-width: 1240px;
		margin: 0 auto;
	}

	.foot-line {
		height: 1px;
		background: #1a1a1a;
		margin-bottom: 24px;
	}
	.wsb .foot-line { background: #0a2a0a; }

	.foot p {
		font-size: 11px;
		letter-spacing: 0.12em;
		color: #333;
		margin: 0;
	}

	/* ── Responsive ───────────────────────────────────────── */
	@media (max-width: 1024px) {
		.hero-inner {
			flex-direction: column;
			gap: 48px;
			align-items: stretch;
		}
		.hero-right {
			flex: none;
			max-width: 480px;
		}
		.grid {
			grid-template-columns: repeat(2, 1fr);
		}
	}

	@media (max-width: 640px) {
		.hero {
			padding: 60px 5% 40px;
		}
		.title {
			font-size: clamp(3.2rem, 14vw, 5rem);
		}
		.hero-right {
			max-width: none;
		}
		.grid {
			grid-template-columns: 1fr;
		}
		.actions {
			flex-direction: column;
			align-items: stretch;
		}
		.btn-main, .btn-ghost {
			justify-content: center;
			text-align: center;
		}
	}
</style>
