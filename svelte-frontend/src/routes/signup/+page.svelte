<script lang="ts">
	import { goto } from '$app/navigation';
	import { supabase } from '$lib/supabase';

	let email = $state('');
	let password = $state('');
	let confirm = $state('');
	let error = $state('');
	let loading = $state(false);
	let success = $state(false);

	async function signup() {
		error = '';
		if (password !== confirm) {
			error = 'Passwords do not match.';
			return;
		}
		if (password.length < 6) {
			error = 'Password must be at least 6 characters.';
			return;
		}
		loading = true;
		const { error: err } = await supabase.auth.signUp({ email, password });
		loading = false;
		if (err) {
			error = err.message;
		} else {
			// Supabase may auto-confirm or require email verification depending on project settings
			const { data: { session } } = await supabase.auth.getSession();
			if (session) {
				goto('/chat');
			} else {
				success = true;
			}
		}
	}

	function onKey(e: KeyboardEvent) {
		if (e.key === 'Enter') signup();
	}
</script>

<div class="page">
	<a href="/" class="back">← Market Chat</a>
	<div class="card">
		{#if success}
			<h1>Check your email</h1>
			<p class="sub">We sent a confirmation link to <strong>{email}</strong>. Click it to activate your account.</p>
			<a href="/login" class="btn" style="display:block;text-align:center;text-decoration:none;margin-top:24px;">Back to sign in</a>
		{:else}
			<h1>Create account</h1>
			<p class="sub">Start analyzing markets in seconds</p>

			<div class="fields">
				<div class="field">
					<label for="email">Email</label>
					<input
						id="email"
						type="email"
						bind:value={email}
						onkeydown={onKey}
						placeholder="you@example.com"
						autocomplete="email"
					/>
				</div>
				<div class="field">
					<label for="password">Password</label>
					<input
						id="password"
						type="password"
						bind:value={password}
						onkeydown={onKey}
						placeholder="••••••••"
						autocomplete="new-password"
					/>
				</div>
				<div class="field">
					<label for="confirm">Confirm password</label>
					<input
						id="confirm"
						type="password"
						bind:value={confirm}
						onkeydown={onKey}
						placeholder="••••••••"
						autocomplete="new-password"
					/>
				</div>
			</div>

			{#if error}
				<div class="error">{error}</div>
			{/if}

			<button class="btn" onclick={signup} disabled={loading || !email || !password || !confirm}>
				{loading ? 'Creating account...' : 'Create account'}
			</button>

			<p class="switch">Already have an account? <a href="/login">Sign in</a></p>
		{/if}
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

	.back {
		position: fixed;
		top: 24px;
		left: 24px;
		color: #555;
		text-decoration: none;
		font-size: 13px;
		transition: color 0.15s;
	}
	.back:hover {
		color: #eaeaea;
	}

	.card {
		width: 100%;
		max-width: 380px;
		padding: 0 24px;
	}

	h1 {
		font-size: 28px;
		font-weight: 500;
		color: #eaeaea;
		margin: 0 0 8px;
		letter-spacing: -0.01em;
	}

	.sub {
		color: #666;
		font-size: 14px;
		margin: 0 0 32px;
		line-height: 1.5;
	}
	.sub strong {
		color: #aaa;
	}

	.fields {
		display: flex;
		flex-direction: column;
		gap: 16px;
		margin-bottom: 12px;
	}

	.field {
		display: flex;
		flex-direction: column;
		gap: 6px;
	}

	label {
		font-size: 12px;
		color: #888;
		letter-spacing: 0.02em;
	}

	input {
		background: #0e0e0e;
		border: 1px solid #262626;
		border-radius: 8px;
		padding: 10px 12px;
		color: #eaeaea;
		font-family: inherit;
		font-size: 14px;
		outline: none;
		transition: border-color 0.15s;
		width: 100%;
	}
	input:focus {
		border-color: #444;
	}
	input::placeholder {
		color: #444;
	}

	.error {
		color: #f87171;
		font-size: 13px;
		margin-bottom: 12px;
	}

	.btn {
		width: 100%;
		background: #eaeaea;
		color: #000;
		border: none;
		padding: 11px;
		border-radius: 8px;
		font-size: 14px;
		font-weight: 500;
		cursor: pointer;
		margin-top: 8px;
		font-family: inherit;
		transition: background 0.15s;
	}
	.btn:hover:not(:disabled) {
		background: #fff;
	}
	.btn:disabled {
		background: #1a1a1a;
		color: #555;
		cursor: not-allowed;
	}

	.switch {
		text-align: center;
		font-size: 13px;
		color: #555;
		margin-top: 20px;
	}
	.switch a {
		color: #aaa;
		text-decoration: none;
	}
	.switch a:hover {
		color: #eaeaea;
	}
</style>
