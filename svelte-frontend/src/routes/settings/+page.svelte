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
		activeTab="settings"
		onNavigate={navigateTab}
		onSignOut={async () => {
			await supabase.auth.signOut();
			goto('/');
		}}
	/>
	<main class="main">
		<div class="terminal">
			<div class="header">
				<h1>Settings</h1>
				<span class="sub">Account preferences and configuration</span>
			</div>

			<div class="sections">
				<div class="section" style="animation-delay: 0ms">
					<div class="section-head">
						<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
						<span>Profile</span>
					</div>
					<div class="field-group">
						<div class="field">
							<span class="field-label">Display Name</span>
							<div class="mock-input">trader_anon</div>
						</div>
						<div class="field">
							<span class="field-label">Email</span>
							<div class="mock-input">user@example.com</div>
						</div>
					</div>
				</div>

				<div class="section" style="animation-delay: 60ms">
					<div class="section-head">
						<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><path d="M4 5h16v11H7l-3 3V5z"/></svg>
						<span>Chat</span>
					</div>
					<div class="field-group">
						<div class="field">
							<span class="field-label">Default Personality</span>
							<div class="toggle-row">
								<button class="toggle active">PRO</button>
								<button class="toggle">WSB</button>
							</div>
						</div>
						<div class="field">
							<span class="field-label">Streaming Responses</span>
							<div class="switch on"><div class="knob"></div></div>
						</div>
					</div>
				</div>

				<div class="section" style="animation-delay: 120ms">
					<div class="section-head">
						<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
						<span>Security</span>
					</div>
					<div class="field-group">
						<div class="field">
							<span class="field-label">Two-Factor Authentication</span>
							<div class="switch off"><div class="knob"></div></div>
						</div>
						<div class="field">
							<span class="field-label">Active Sessions</span>
							<div class="mock-input dim">1 active session</div>
						</div>
					</div>
				</div>

				<div class="section" style="animation-delay: 180ms">
					<div class="section-head">
						<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><path d="M18 8A6 6 0 006 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 01-3.46 0"/></svg>
						<span>Notifications</span>
					</div>
					<div class="field-group">
						<div class="field">
							<span class="field-label">Price Alerts</span>
							<div class="switch off"><div class="knob"></div></div>
						</div>
						<div class="field">
							<span class="field-label">Email Digest</span>
							<div class="toggle-row">
								<button class="toggle">Daily</button>
								<button class="toggle active">Weekly</button>
								<button class="toggle">Off</button>
							</div>
						</div>
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
		max-width: 640px;
		margin: 0 auto;
		padding: 40px 32px;
	}
	.header {
		margin-bottom: 32px;
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

	.sections {
		display: flex;
		flex-direction: column;
		gap: 16px;
	}
	.section {
		background: #060606;
		border: 1px solid #161616;
		border-radius: 10px;
		padding: 18px;
		animation: fadeSlide 0.4s ease both;
	}
	.section-head {
		display: flex;
		align-items: center;
		gap: 10px;
		font-size: 15px;
		font-weight: 500;
		color: #ccc;
		margin-bottom: 16px;
		padding-bottom: 12px;
		border-bottom: 1px solid #141414;
	}
	.section-head svg {
		width: 18px;
		height: 18px;
		color: #ff8c00;
	}

	.field-group {
		display: flex;
		flex-direction: column;
		gap: 14px;
	}
	.field {
		display: flex;
		justify-content: space-between;
		align-items: center;
		gap: 16px;
	}
	.field .field-label {
		font-size: 13px;
		color: #999;
		flex-shrink: 0;
	}
	.mock-input {
		font-size: 13px;
		color: #ccc;
		background: #0c0c0c;
		border: 1px solid #1e1e1e;
		padding: 7px 12px;
		border-radius: 6px;
		min-width: 160px;
		text-align: right;
	}
	.mock-input.dim {
		color: #666;
	}

	.toggle-row {
		display: flex;
		gap: 4px;
	}
	.toggle {
		background: #0c0c0c;
		border: 1px solid #1e1e1e;
		color: #666;
		font-size: 12px;
		padding: 5px 12px;
		border-radius: 6px;
		cursor: default;
		font-family: inherit;
	}
	.toggle.active {
		color: #ff8c00;
		border-color: #ff8c0050;
		background: #ff8c000d;
	}

	.switch {
		width: 40px;
		height: 22px;
		border-radius: 999px;
		position: relative;
		cursor: default;
		flex-shrink: 0;
	}
	.switch.on {
		background: #ff8c0030;
		border: 1px solid #ff8c0050;
	}
	.switch.off {
		background: #1a1a1a;
		border: 1px solid #2a2a2a;
	}
	.knob {
		width: 16px;
		height: 16px;
		border-radius: 50%;
		position: absolute;
		top: 2px;
		transition: left 0.15s;
	}
	.switch.on .knob {
		left: 21px;
		background: #ff8c00;
	}
	.switch.off .knob {
		left: 2px;
		background: #555;
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
		.terminal { padding: 24px 16px; }
		.field {
			flex-direction: column;
			align-items: flex-start;
			gap: 6px;
		}
		.mock-input {
			text-align: left;
			width: 100%;
			min-width: 0;
		}
	}
</style>
