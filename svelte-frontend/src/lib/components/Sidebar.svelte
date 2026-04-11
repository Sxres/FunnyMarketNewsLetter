<script lang="ts">
	type NavTab = 'chat' | 'watchlist' | 'portfolio' | 'market' | 'settings';
	type Session = { session_id: string; title: string; created_at: string };

	let {
		activeTab,
		sessions = [],
		activeSessionId = null,
		onNewChat = () => {},
		onSelectSession = () => {},
		onDeleteSession = () => {},
		onSignOut = () => {},
		onNavigate = () => {}
	} = $props<{
		activeTab: NavTab;
		sessions?: Session[];
		activeSessionId?: string | null;
		onNewChat?: () => void;
		onSelectSession?: (sessionId: string) => void;
		onDeleteSession?: (sessionId: string, e: MouseEvent) => void;
		onSignOut?: () => void;
		onNavigate?: (tab: NavTab) => void;
	}>();

	const navItems: Array<{ id: NavTab; label: string }> = [
		{ id: 'watchlist', label: 'Watchlist' },
		{ id: 'portfolio', label: 'Portfolio' },
		{ id: 'market', label: 'Market' },
		{ id: 'settings', label: 'Settings' }
	];

	function iconPath(tab: NavTab): string {
		if (tab === 'watchlist') return 'M12 3l2.9 5.88 6.5.94-4.7 4.58 1.1 6.47L12 18l-5.8 3.87 1.1-6.47-4.7-4.58 6.5-.94L12 3z';
		if (tab === 'portfolio') return 'M4 19h16M7 15v-4m5 4V6m5 9v-7';
		if (tab === 'market') return 'M4 16l5-5 4 3 7-8';
		return 'M12 3v2m0 14v2m9-9h-2M5 12H3m15.4 6.4-1.4-1.4M7 7 5.6 5.6m12.8 0L17 7M7 17l-1.4 1.4M12 8a4 4 0 100 8 4 4 0 000-8z';
	}
</script>

<aside class="sidebar">
	<button class="new-chat" onclick={() => { onNewChat(); onNavigate('chat'); }}>
		<span class="plus">+</span> New chat
	</button>

	<div class="sessions-label">Past chats</div>
	<div class="sessions">
		{#each sessions as s (s.session_id)}
			<button
				class="session"
				class:active={s.session_id === activeSessionId}
				onclick={() => onSelectSession(s.session_id)}
			>
				<span class="session-title">{s.title || 'Untitled'}</span>
				<span
					class="del"
					role="button"
					tabindex="0"
					onclick={(e) => onDeleteSession(s.session_id, e)}
					onkeydown={(e) => e.key === 'Enter' && onDeleteSession(s.session_id, e as any)}
					title="Delete chat"
				>
					&times;
				</span>
			</button>
		{/each}
		{#if sessions.length === 0}
			<div class="empty">No past chats</div>
		{/if}
	</div>

	<div class="nav-section">
		{#each navItems as item}
			<button
				class="nav-item"
				class:active={activeTab === item.id}
				onclick={() => onNavigate(item.id)}
			>
				<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
					<path d={iconPath(item.id)}></path>
				</svg>
				<span>{item.label}</span>
			</button>
		{/each}
	</div>

	<button class="signout" onclick={onSignOut}>Sign out</button>
</aside>

<style>
	.sidebar {
		width: 240px;
		flex-shrink: 0;
		border-right: 1px solid #1a1a1a;
		background: #080808;
		display: flex;
		flex-direction: column;
		padding: 14px 10px;
	}

	.new-chat {
		background: transparent;
		border: 1px solid #2a2a2a;
		color: #eaeaea;
		padding: 10px 12px;
		border-radius: 8px;
		text-align: left;
		cursor: pointer;
		font-size: 13px;
		transition: background 0.15s, border-color 0.15s;
	}
	.new-chat:hover {
		background: #141414;
		border-color: #3a3a3a;
	}
	.plus {
		margin-right: 6px;
		opacity: 0.8;
	}

	.sessions-label {
		font-size: 11px;
		text-transform: uppercase;
		letter-spacing: 0.08em;
		color: #666;
		padding: 18px 10px 6px;
	}
	.sessions {
		overflow-y: auto;
		flex: 1;
		display: flex;
		flex-direction: column;
		gap: 2px;
	}
	.session {
		background: transparent;
		border: none;
		color: #bdbdbd;
		text-align: left;
		padding: 9px 10px;
		border-radius: 6px;
		cursor: pointer;
		font-size: 13px;
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 8px;
	}
	.session:hover {
		background: #141414;
		color: #eaeaea;
	}
	.session.active {
		background: #181818;
		color: #eaeaea;
	}
	.session-title {
		flex: 1;
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}
	.del {
		color: #555;
		font-size: 16px;
		line-height: 1;
		padding: 0 4px;
		border-radius: 4px;
		opacity: 0;
		transition: opacity 0.15s, color 0.15s, background 0.15s;
		cursor: pointer;
	}
	.session:hover .del {
		opacity: 1;
	}
	.del:hover {
		color: #eaeaea;
		background: #222;
	}
	.empty {
		color: #555;
		font-size: 12px;
		padding: 10px;
	}

	.nav-section {
		border-top: 1px solid #1a1a1a;
		padding-top: 10px;
		margin-top: 10px;
		display: flex;
		flex-direction: column;
		gap: 2px;
	}
	.nav-item {
		background: transparent;
		border: none;
		color: #777;
		padding: 8px 10px;
		border-radius: 6px;
		cursor: pointer;
		font-size: 13px;
		display: flex;
		align-items: center;
		gap: 10px;
		transition: color 0.15s, background 0.15s;
	}
	.nav-item:hover {
		background: #141414;
		color: #ccc;
	}
	.nav-item.active {
		background: #181818;
		color: #d4af37;
	}
	.nav-item svg {
		width: 16px;
		height: 16px;
		flex-shrink: 0;
	}

	.signout {
		background: transparent;
		border: none;
		color: #555;
		font-size: 12px;
		text-align: left;
		padding: 10px;
		cursor: pointer;
		width: 100%;
		transition: color 0.15s;
		margin-top: 6px;
	}
	.signout:hover {
		color: #eaeaea;
	}

	@media (max-width: 900px) {
		.sidebar {
			width: 100%;
			height: auto;
			max-height: 50vh;
			border-right: none;
			border-bottom: 1px solid #1a1a1a;
		}
	}
</style>
