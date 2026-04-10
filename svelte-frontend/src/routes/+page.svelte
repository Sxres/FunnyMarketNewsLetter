<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { supabase } from '$lib/supabase';

	// If already signed in, skip landing
	onMount(async () => {
		const { data: { session } } = await supabase.auth.getSession();
		if (session) goto('/chat');
	});
</script>

<div class="page">
	<div class="center">
		<div class="badge">AI-powered</div>
		<h1>Market Chat</h1>
		<p class="sub">Real-time stock analysis, news, and market intelligence.<br />Ask anything. Get answers in seconds.</p>

		<div class="features">
			<div class="feature">
				<span class="icon">↑</span>
				<span>Live prices & fundamentals</span>
			</div>
			<div class="feature">
				<span class="icon">◎</span>
				<span>Insider trades & analyst ratings</span>
			</div>
			<div class="feature">
				<span class="icon">⚡</span>
				<span>Professional or WSB mode</span>
			</div>
		</div>

		<div class="actions">
			<a href="/signup" class="btn-primary">Get started</a>
			<a href="/login" class="btn-ghost">Sign in</a>
		</div>
	</div>
</div>

<style>
	.page {
		height: 100vh;
		display: flex;
		align-items: center;
		justify-content: center;
		background: #000;
	}

	.center {
		text-align: center;
		max-width: 480px;
		padding: 0 24px;
	}

	.badge {
		display: inline-block;
		font-size: 11px;
		letter-spacing: 0.1em;
		text-transform: uppercase;
		color: #555;
		border: 1px solid #222;
		border-radius: 999px;
		padding: 4px 12px;
		margin-bottom: 28px;
	}

	h1 {
		font-size: 52px;
		font-weight: 500;
		color: #eaeaea;
		margin: 0 0 16px;
		letter-spacing: -0.02em;
		line-height: 1.1;
	}

	.sub {
		color: #666;
		font-size: 15px;
		line-height: 1.6;
		margin: 0 0 36px;
	}

	.features {
		display: flex;
		flex-direction: column;
		gap: 10px;
		margin-bottom: 40px;
		text-align: left;
		border: 1px solid #1a1a1a;
		border-radius: 12px;
		padding: 16px 20px;
	}

	.feature {
		display: flex;
		align-items: center;
		gap: 12px;
		color: #aaa;
		font-size: 13px;
	}

	.icon {
		color: #555;
		font-size: 14px;
		width: 18px;
		text-align: center;
		flex-shrink: 0;
	}

	.actions {
		display: flex;
		gap: 12px;
		justify-content: center;
	}

	.btn-primary {
		background: #eaeaea;
		color: #000;
		text-decoration: none;
		padding: 10px 28px;
		border-radius: 999px;
		font-size: 14px;
		font-weight: 500;
		transition: background 0.15s;
	}
	.btn-primary:hover {
		background: #fff;
	}

	.btn-ghost {
		background: transparent;
		color: #aaa;
		text-decoration: none;
		padding: 10px 24px;
		border-radius: 999px;
		font-size: 14px;
		border: 1px solid #222;
		transition: color 0.15s, border-color 0.15s;
	}
	.btn-ghost:hover {
		color: #eaeaea;
		border-color: #444;
	}
</style>
