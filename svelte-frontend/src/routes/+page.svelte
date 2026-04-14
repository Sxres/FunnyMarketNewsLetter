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

	const steps = [
		{
			num: '01',
			title: 'ASK',
			desc: 'Type a question about any ticker. Price, fundamentals, news, insider activity, or everything at once.'
		},
		{
			num: '02',
			title: 'EXECUTE',
			desc: 'Claude picks the right tools, pulls live data from Finnhub and Yahoo, and streams the result in real time.'
		},
		{
			num: '03',
			title: 'GET THE TAKE',
			desc: 'A cited, source-linked verdict in your chosen voice. Professional, or degenerate. Both grounded in fact.'
		}
	];

	let statsLive = $state(false);
	let statTools = $state(0);
	let statSources = $state(0);
	let statLatency = $state(0);
	let statCited = $state(0);

	function reveal(node: HTMLElement, delay: number = 0) {
		node.classList.add('reveal-init');
		const obs = new IntersectionObserver(
			(entries) => {
				entries.forEach((e) => {
					if (e.isIntersecting) {
						setTimeout(() => node.classList.add('reveal-in'), delay);
						obs.unobserve(node);
					}
				});
			},
			{ threshold: 0.12, rootMargin: '0px 0px -60px 0px' }
		);
		obs.observe(node);
		return {
			destroy() {
				obs.disconnect();
			}
		};
	}

	function countUp(node: HTMLElement) {
		const obs = new IntersectionObserver(
			(entries) => {
				entries.forEach((e) => {
					if (e.isIntersecting && !statsLive) {
						statsLive = true;
						const targets = { tools: 4, sources: 6, latency: 280, cited: 100 };
						const duration = 1600;
						const start = performance.now();
						const tick = (now: number) => {
							const t = Math.min((now - start) / duration, 1);
							const eased = 1 - Math.pow(1 - t, 3);
							statTools = Math.round(targets.tools * eased);
							statSources = Math.round(targets.sources * eased);
							statLatency = Math.round(targets.latency * eased);
							statCited = Math.round(targets.cited * eased);
							if (t < 1) requestAnimationFrame(tick);
						};
						requestAnimationFrame(tick);
						obs.unobserve(node);
					}
				});
			},
			{ threshold: 0.3 }
		);
		obs.observe(node);
		return {
			destroy() {
				obs.disconnect();
			}
		};
	}

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

<svelte:head>
	<link rel="preload" href="/fonts/OverusedGrotesk-Book.otf" as="font" type="font/otf" crossorigin="anonymous" />
	<link rel="preload" href="/fonts/OverusedGrotesk-Medium.otf" as="font" type="font/otf" crossorigin="anonymous" />
</svelte:head>

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
				<h1 class="title">
					<span class="t1">MARKET</span>
					<span class="t2">CHAT</span>
				</h1>

				<p class="subtitle">
					{#if mode === 'professional'}
						Real-time market intelligence powered by agentic AI.
						Price action, fundamentals, insider activity, and analyst consensus with cited sources you can trust.
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
							{mode === 'professional' ? 'sample output' : 'sample output'}
						</div>
						<p class="preview-text">
							{#if mode === 'professional'}
								NVDA trades at 38.2x forward P/E with 94% gross margins on datacenter. Consensus PT $152 implies 18% upside. Insider selling remains minimal.
							{:else}
								NVDA IS LITERALLY PRINTING MONEY. 94% MARGINS?? JENSEN IS A GOD. BEARS ARE FINANCIALLY RUINED. $200 EOW IS NOT A MEME.
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
				{mode === 'professional' ? '' : ''}
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

	<!-- Bento: About / Mission -->
	<section class="about-section">
		<div class="sect-head" use:reveal>
			<h2 class="sect-title">
				{#if mode === 'professional'}
					Built by <span class="sect-emph">one.</span><br />
					Armed for <span class="sect-emph">many.</span>
				{:else}
					Blew the <span class="sect-emph">port.</span><br />
					Picked up another <span class="sect-emph">Wendy's shift.</span>
				{/if}
			</h2>
		</div>

		<div class="bento">
			<div class="cell cell-about" use:reveal>
				<div class="about-head">
					<div class="avatar">
						<img src="/team-avatar.svg" alt="Market Chat team avatar" />
					</div>
					<div class="about-id">
						<div class="about-name">{mode === 'professional' ? 'ABOUT US' : 'ABOUT THE DEGEN DESK'}</div>
						<div class="about-role">{mode === 'professional' ? 'Market Chat Team' : 'Certified Chart Goblins'}</div>
					</div>
				</div>
				<p class="about-bio">
					{#if mode === 'professional'}
						We build at the intersection of markets, data, and machine learning.
						Our focus is turning raw information into instant clarity for retail investors.
						Every feature is designed to deliver fast, cited analysis you can act on.
					{:else}
						We live in pre-market panic, intraday chaos, and after-hours copium.
						This terminal turns headline noise into tradable signal before your coffee gets cold.
						If the chart looks cursed, we still bring receipts and a battle plan.
					{/if}
				</p>
			</div>

			<div class="cell cell-stats" use:reveal={120} use:countUp>
				<div class="stats-grid">
					<div class="stat">
						<div class="stat-val">{statTools}</div>
						<div class="stat-sub">TOOLS WIRED</div>
					</div>
					<div class="stat">
						<div class="stat-val">{statSources}</div>
						<div class="stat-sub">DATA SOURCES</div>
					</div>
					<div class="stat">
						<div class="stat-val">{statLatency}<span class="stat-unit">ms</span></div>
						<div class="stat-sub">AVG LATENCY</div>
					</div>
					<div class="stat">
						<div class="stat-val">{statCited}<span class="stat-unit">%</span></div>
						<div class="stat-sub">SOURCED</div>
					</div>
				</div>
			</div>

			<div class="cell cell-mission" use:reveal={60}>
				<p class="mission-text">
					{mode === 'professional' ? 'Retail investors deserve institutional-grade intelligence.' : 'Blown account yesterday. Fresh setup today.'}
				</p>
				<p class="mission-italic">
					{mode === 'professional' ? 'Built to cut through noise and hand you the signal, raw and cited.' : 'Scan fast. Strike first. Keep your risk tighter than your paycheck.'}
				</p>
			</div>

			<div class="cell cell-stack" use:reveal={140}>
				<div class="stack-list">
					<div class="stack-row"><span class="stack-k">LLM</span><span class="stack-v">Claude Sonnet 4.6</span></div>
					<div class="stack-row"><span class="stack-k">API</span><span class="stack-v">FastAPI + SSE</span></div>
					<div class="stack-row"><span class="stack-k">UI</span><span class="stack-v">SvelteKit</span></div>
					<div class="stack-row"><span class="stack-k">DB</span><span class="stack-v">Supabase</span></div>
					<div class="stack-row"><span class="stack-k">DATA</span><span class="stack-v">Finnhub, yfinance</span></div>
				</div>
			</div>

			<div class="cell cell-now" use:reveal={200}>
				<div class="now-led"><span></span>LIVE BUILD</div>
				<p class="now-text">
					Streaming tool calls, multi-session history, personality switching.
				</p>
				<div class="now-footer">NEXT: OPTIONS FLOW + EARNINGS CAL</div>
			</div>
		</div>
	</section>

	<!-- Process -->
	<section class="process">
		<div class="sect-head" use:reveal>
			<h2 class="sect-title">
				Three steps between you<br />
				and the <span class="sect-emph">tape.</span>
			</h2>
		</div>
		<div class="steps">
			{#each steps as step, i}
				<div class="step" use:reveal={i * 120}>
					<div class="step-line"></div>
					<h3 class="step-title">{step.title}</h3>
					<p class="step-desc">{step.desc}</p>
				</div>
			{/each}
		</div>
	</section>

	<!-- Final CTA -->
	<section class="final-cta-wrap">
		<div class="final-cta" use:reveal>
			<div class="cta-gridlines" aria-hidden="true"></div>
			<div class="cta-inner">
				<h2 class="cta-title">
					The market doesn't wait.<br />
					<span class="cta-emph">Neither should you.</span>
				</h2>
				<a href="/signup" class="cta-btn">
					ENTER THE TERMINAL
					<span class="cta-arrow">→</span>
				</a>
			</div>
		</div>
	</section>

	<!-- Footer -->
	<footer class="foot">
		<div class="foot-line"></div>
		<p>© {new Date().getFullYear()} Market Chat — NOT FINANCIAL ADVICE</p>
	</footer>
</div>

<style>
	/* ── Fonts ────────────────────────────────────────────── */
	@font-face {
		font-family: 'Overused Grotesk';
		src: url('/fonts/OverusedGrotesk-Book.otf') format('opentype');
		font-weight: 400;
		font-style: normal;
		font-display: swap;
	}
	@font-face {
		font-family: 'Overused Grotesk';
		src: url('/fonts/OverusedGrotesk-Medium.otf') format('opentype');
		font-weight: 500;
		font-style: normal;
		font-display: swap;
	}

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
		font-weight: 500;
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
		font-weight: 400;
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
		color: #888;
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
		color: #7ace7a;
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

	/* ── Reveal-on-scroll (applied by use:reveal action) ─── */
	:global(.reveal-init) {
		opacity: 0;
		transform: translateY(36px);
		transition:
			opacity 0.9s cubic-bezier(0.22, 1, 0.36, 1),
			transform 0.9s cubic-bezier(0.22, 1, 0.36, 1),
			border-color 0.3s ease,
			box-shadow 0.3s ease;
		will-change: opacity, transform;
	}
	:global(.reveal-init.reveal-in) {
		opacity: 1;
		transform: translateY(0);
	}

	/* ── Shared section headings ─────────────────────────── */
	.sect-head {
		margin-bottom: 56px;
	}
	.sect-title {
		font-family: 'Overused Grotesk', 'Helvetica Neue', sans-serif;
		font-size: clamp(2.2rem, 5.4vw, 4.2rem);
		font-weight: 500;
		letter-spacing: -0.03em;
		color: #eaeaea;
		line-height: 1.02;
		margin: 14px 0 0;
		max-width: 900px;
	}
	.sect-emph {
		color: #d4af37;
		font-weight: 500;
		transition: color 0.4s ease;
	}
	.wsb .sect-emph {
		color: #00ff41;
		text-shadow: 0 0 24px rgba(0, 255, 65, 0.25);
	}

	/* ── Bento: About / Mission ──────────────────────────── */
	.about-section {
		padding: 120px 6% 80px;
		max-width: 1240px;
		margin: 0 auto;
	}

	.bento {
		display: grid;
		grid-template-columns: 1.45fr 1fr 1fr;
		grid-template-rows: 300px 240px;
		gap: 14px;
		grid-template-areas:
			'about stats mission'
			'about stack now';
	}

	.cell {
		background: #080808;
		border: 1px solid #1a1a1a;
		border-radius: 12px;
		padding: 26px 26px 24px;
		position: relative;
		overflow: hidden;
		transition:
			border-color 0.35s ease,
			box-shadow 0.35s ease,
			transform 0.35s ease;
	}
	.cell::before {
		content: '';
		position: absolute;
		inset: 0;
		background: radial-gradient(
			600px circle at var(--mx, 50%) var(--my, 0%),
			rgba(212, 175, 55, 0.04),
			transparent 40%
		);
		pointer-events: none;
		opacity: 0;
		transition: opacity 0.4s ease;
	}
	.cell:hover::before {
		opacity: 1;
	}
	.cell:hover {
		border-color: #2a2a2a;
	}
	.wsb .cell {
		border-color: #0a2a0a;
	}
	.wsb .cell::before {
		background: radial-gradient(
			600px circle at var(--mx, 50%) var(--my, 0%),
			rgba(0, 255, 65, 0.06),
			transparent 40%
		);
	}
	.wsb .cell:hover {
		border-color: #1a3a1a;
	}

	.cell-about {
		grid-area: about;
	}
	.cell-stats {
		grid-area: stats;
	}
	.cell-mission {
		grid-area: mission;
	}
	.cell-stack {
		grid-area: stack;
	}
	.cell-now {
		grid-area: now;
		display: flex;
		flex-direction: column;
	}

	/* About cell */
	.about-head {
		display: flex;
		align-items: center;
		gap: 16px;
		margin-bottom: 26px;
	}
	.avatar {
		width: 60px;
		height: 60px;
		border-radius: 50%;
		background: linear-gradient(135deg, #e6c354 0%, #8b6914 100%);
		overflow: hidden;
		box-shadow:
			0 0 0 1px #1a1a1a,
			0 10px 40px rgba(212, 175, 55, 0.18);
		flex-shrink: 0;
		transition: all 0.4s ease;
	}
	.avatar img {
		display: block;
		width: 100%;
		height: 100%;
		object-fit: cover;
	}
	.wsb .avatar {
		background: linear-gradient(135deg, #33ff66 0%, #006619 100%);
		box-shadow:
			0 0 0 1px #0a2a0a,
			0 10px 40px rgba(0, 255, 65, 0.25);
	}
	.about-name {
		font-family: 'Overused Grotesk', 'Helvetica Neue', sans-serif;
		font-size: 24px;
		font-weight: 500;
		letter-spacing: 0.02em;
		color: #eaeaea;
		margin-bottom: 4px;
		line-height: 1;
	}
	.about-role {
		font-size: 11.5px;
		color: #666;
		letter-spacing: 0.08em;
		font-family: 'SF Mono', monospace;
		text-transform: uppercase;
	}
	.about-bio {
		font-size: 13.5px;
		line-height: 1.72;
		color: #8a8a8a;
		margin: 0 0 24px;
		max-width: 440px;
	}

	/* Stats cell */
	.stats-grid {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 22px 16px;
	}
	.stat {
		display: flex;
		flex-direction: column;
		gap: 6px;
	}
	.stat-val {
		font-family: 'Overused Grotesk', 'Helvetica Neue', sans-serif;
		font-size: 32px;
		font-weight: 500;
		color: #d4af37;
		font-variant-numeric: tabular-nums;
		letter-spacing: -0.03em;
		line-height: 1;
		transition: color 0.3s ease;
	}
	.wsb .stat-val {
		color: #00ff41;
		text-shadow: 0 0 20px rgba(0, 255, 65, 0.2);
	}
	.stat-unit {
		font-family: 'SF Mono', monospace;
		font-size: 13px;
		color: #555;
		margin-left: 2px;
		font-weight: 500;
	}
	.wsb .stat-unit {
		color: #446644;
	}
	/* Mission cell */
	.mission-text {
		font-size: 13px;
		line-height: 1.6;
		color: #777;
		margin: 0 0 14px;
	}
	.mission-italic {
		font-family: 'Overused Grotesk', 'Helvetica Neue', sans-serif;
		font-size: 16px;
		font-weight: 500;
		line-height: 1.4;
		color: #d4af37;
		margin: 0;
		letter-spacing: -0.015em;
		transition: color 0.3s ease;
	}
	.wsb .mission-italic {
		color: #00ff41;
		text-shadow: 0 0 20px rgba(0, 255, 65, 0.2);
	}

	/* Stack cell */
	.stack-list {
		display: flex;
		flex-direction: column;
		gap: 11px;
	}
	.stack-row {
		display: flex;
		align-items: baseline;
		gap: 14px;
		padding-bottom: 9px;
		border-bottom: 1px dashed #141414;
	}
	.stack-row:last-child {
		border-bottom: none;
		padding-bottom: 0;
	}
	.wsb .stack-row {
		border-bottom-color: #0a1a0a;
	}
	.stack-k {
		font-family: 'SF Mono', monospace;
		font-size: 9px;
		letter-spacing: 0.18em;
		color: #d4af37;
		width: 42px;
		flex-shrink: 0;
		transition: color 0.3s ease;
	}
	.wsb .stack-k {
		color: #00ff41;
	}
	.stack-v {
		font-size: 12.5px;
		color: #aaa;
		font-weight: 400;
	}

	/* Now cell */
	.now-led {
		display: inline-flex;
		align-items: center;
		gap: 10px;
		font-size: 10px;
		font-family: 'SF Mono', monospace;
		letter-spacing: 0.18em;
		color: #d4af37;
		margin-bottom: 16px;
		transition: color 0.3s ease;
	}
	.wsb .now-led {
		color: #00ff41;
	}
	.now-led span {
		width: 7px;
		height: 7px;
		border-radius: 50%;
		background: #d4af37;
		box-shadow: 0 0 10px #d4af37;
		animation: blink-dot 1.4s infinite;
	}
	.wsb .now-led span {
		background: #00ff41;
		box-shadow: 0 0 10px #00ff41;
	}
	.now-text {
		font-size: 13px;
		line-height: 1.62;
		color: #8a8a8a;
		margin: 0;
		flex: 1;
	}
	.now-footer {
		margin-top: 16px;
		padding-top: 14px;
		border-top: 1px dashed #141414;
		font-family: 'SF Mono', monospace;
		font-size: 9px;
		letter-spacing: 0.14em;
		color: #555;
	}
	.wsb .now-footer {
		border-top-color: #0a1a0a;
		color: #446644;
	}

	/* ── Process / How it works ──────────────────────────── */
	.process {
		padding: 100px 6% 80px;
		max-width: 1240px;
		margin: 0 auto;
	}
	.steps {
		display: grid;
		grid-template-columns: repeat(3, 1fr);
		gap: 16px;
	}
	.step {
		position: relative;
		padding: 34px 28px 32px;
		background: #080808;
		border: 1px solid #1a1a1a;
		border-radius: 12px;
		transition:
			border-color 0.35s ease,
			box-shadow 0.35s ease,
			transform 0.35s ease;
	}
	.step:hover {
		border-color: #2a2a2a;
		transform: translateY(-2px);
		box-shadow: 0 12px 40px rgba(0, 0, 0, 0.45);
	}
	.wsb .step {
		border-color: #0a2a0a;
	}
	.wsb .step:hover {
		border-color: #1a3a1a;
		box-shadow: 0 12px 40px rgba(0, 255, 65, 0.05);
	}
	.step-line {
		height: 1px;
		background: linear-gradient(90deg, #d4af37 0%, transparent 100%);
		margin-bottom: 26px;
		opacity: 0.5;
		transition: background 0.3s ease;
	}
	.wsb .step-line {
		background: linear-gradient(90deg, #00ff41 0%, transparent 100%);
	}
	.step-title {
		font-family: 'Overused Grotesk', 'Helvetica Neue', sans-serif;
		font-size: 22px;
		font-weight: 500;
		letter-spacing: -0.02em;
		color: #eaeaea;
		margin: 0 0 14px;
		line-height: 1.1;
	}
	.step-desc {
		font-size: 13.5px;
		line-height: 1.7;
		color: #777;
		margin: 0;
	}

	/* ── Final CTA ───────────────────────────────────────── */
	.final-cta-wrap {
		padding: 40px 6% 60px;
		max-width: 1240px;
		margin: 0 auto;
	}
	.final-cta {
		position: relative;
		padding: 110px 6%;
		overflow: hidden;
		border: 1px solid #1a1a1a;
		border-radius: 14px;
		background:
			radial-gradient(ellipse at 50% 100%, rgba(212, 175, 55, 0.09), transparent 60%),
			#060606;
		transition: border-color 0.4s ease, background 0.4s ease;
	}
	.wsb .final-cta {
		border-color: #0a2a0a;
		background:
			radial-gradient(ellipse at 50% 100%, rgba(0, 255, 65, 0.1), transparent 60%),
			#020602;
	}
	.cta-gridlines {
		position: absolute;
		inset: 0;
		background-image:
			linear-gradient(rgba(212, 175, 55, 0.045) 1px, transparent 1px),
			linear-gradient(90deg, rgba(212, 175, 55, 0.045) 1px, transparent 1px);
		background-size: 52px 52px;
		pointer-events: none;
		mask-image: radial-gradient(ellipse at center, black 10%, transparent 75%);
		-webkit-mask-image: radial-gradient(ellipse at center, black 10%, transparent 75%);
	}
	.wsb .cta-gridlines {
		background-image:
			linear-gradient(rgba(0, 255, 65, 0.05) 1px, transparent 1px),
			linear-gradient(90deg, rgba(0, 255, 65, 0.05) 1px, transparent 1px);
	}
	.cta-inner {
		position: relative;
		z-index: 1;
		max-width: 820px;
		margin: 0 auto;
		text-align: center;
	}
	.cta-title {
		font-family: 'Overused Grotesk', 'Helvetica Neue', sans-serif;
		font-size: clamp(2.4rem, 6.2vw, 4.8rem);
		font-weight: 500;
		letter-spacing: -0.04em;
		line-height: 1;
		color: #eaeaea;
		margin: 0 0 48px;
	}
	.cta-emph {
		color: #d4af37;
		font-weight: 500;
		transition: color 0.4s ease;
	}
	.wsb .cta-emph {
		color: #00ff41;
		text-shadow: 0 0 32px rgba(0, 255, 65, 0.35);
	}
	.cta-btn {
		display: inline-flex;
		align-items: center;
		gap: 14px;
		padding: 20px 44px;
		background: #eaeaea;
		color: #000;
		text-decoration: none;
		font-size: 13px;
		font-weight: 600;
		letter-spacing: 0.2em;
		border-radius: 8px;
		transition:
			background 0.2s ease,
			transform 0.18s ease,
			box-shadow 0.3s ease;
	}
	.cta-btn:hover {
		background: #fff;
		transform: translateY(-2px);
		box-shadow: 0 16px 48px rgba(255, 255, 255, 0.12);
	}
	.wsb .cta-btn {
		background: #00ff41;
	}
	.wsb .cta-btn:hover {
		background: #33ff66;
		box-shadow: 0 16px 48px rgba(0, 255, 65, 0.3);
	}
	.cta-arrow {
		transition: transform 0.22s ease;
	}
	.cta-btn:hover .cta-arrow {
		transform: translateX(6px);
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
		.bento {
			grid-template-columns: 1fr 1fr;
			grid-template-rows: auto auto auto;
			grid-template-areas:
				'about about'
				'stats mission'
				'stack now';
		}
		.cell-about {
			min-height: 340px;
		}
		.steps {
			grid-template-columns: 1fr;
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
		.bento {
			grid-template-columns: 1fr;
			grid-template-rows: auto;
			grid-template-areas:
				'about'
				'stats'
				'mission'
				'stack'
				'now';
		}
		.cell-about {
			min-height: auto;
		}
		.about-section {
			padding: 80px 5% 60px;
		}
		.process {
			padding: 60px 5%;
		}
		.final-cta {
			padding: 80px 6%;
		}
		.final-cta-wrap {
			padding: 20px 5% 40px;
		}
	}
</style>
