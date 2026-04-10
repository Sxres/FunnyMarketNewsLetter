<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { supabase } from '$lib/supabase';

	type Message = { role: 'user' | 'assistant'; content: string };
	type Session = { session_id: string; title: string; created_at: string };

	const API = 'http://localhost:8000';

	let sessions = $state<Session[]>([]);
	let activeSessionId = $state<string | null>(null);
	let messages = $state<Message[]>([]);
	let loadingHistory = $state(false);
	let sending = $state(false);

	let input = $state('');
	let personality = $state<'professional' | 'wsb'>('professional');
	let modeOpen = $state(false);

	let messagesEl: HTMLDivElement | null = $state(null);

	// ── Minimal markdown renderer ─────────────────────────────────────────
	function escapeHtml(s: string): string {
		return s
			.replace(/&/g, '&amp;')
			.replace(/</g, '&lt;')
			.replace(/>/g, '&gt;')
			.replace(/"/g, '&quot;')
			.replace(/'/g, '&#39;');
	}

	function renderInline(s: string): string {
		// Order matters: code first so ** inside code isn't parsed
		s = s.replace(/`([^`]+)`/g, '<code>$1</code>');

		// Extract markdown links to placeholders so their URLs don't collide with bold/italic regex
		const links: string[] = [];
		s = s.replace(/\[([^\]]+)\]\(([^)\s]+)\)/g, (_m, text, url) => {
			const safeUrl = url.replace(/"/g, '%22');
			const i = links.length;
			links.push(
				`<a href="${safeUrl}" target="_blank" rel="noopener noreferrer">${text}</a>`
			);
			return `\u0000LINK${i}\u0000`;
		});

		s = s.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
		s = s.replace(/(^|[\s(])\*([^*\n]+)\*(?=[\s).,!?]|$)/g, '$1<em>$2</em>');
		s = s.replace(/(^|[\s(])_([^_\n]+)_(?=[\s).,!?]|$)/g, '$1<em>$2</em>');

		// Restore links
		s = s.replace(/\u0000LINK(\d+)\u0000/g, (_m, i) => links[Number(i)]);
		return s;
	}

	function renderMarkdown(src: string): string {
		if (!src) return '';
		const lines = escapeHtml(src).split('\n');
		const out: string[] = [];
		let inList = false;
		let paraBuf: string[] = [];

		const flushPara = () => {
			if (paraBuf.length) {
				out.push('<p>' + renderInline(paraBuf.join(' ')) + '</p>');
				paraBuf = [];
			}
		};
		const closeList = () => {
			if (inList) {
				out.push('</ul>');
				inList = false;
			}
		};

		for (const raw of lines) {
			const line = raw.trimEnd();
			// Horizontal rule — skip entirely per requirement
			if (/^\s*-{3,}\s*$/.test(line)) {
				flushPara();
				closeList();
				continue;
			}
			if (!line.trim()) {
				flushPara();
				closeList();
				continue;
			}
			// Headings
			const h = line.match(/^(#{1,6})\s+(.*)$/);
			if (h) {
				flushPara();
				closeList();
				const level = h[1].length;
				out.push(`<h${level}>${renderInline(h[2])}</h${level}>`);
				continue;
			}
			// List items
			const li = line.match(/^\s*[-*]\s+(.*)$/);
			if (li) {
				flushPara();
				if (!inList) {
					out.push('<ul>');
					inList = true;
				}
				out.push('<li>' + renderInline(li[1]) + '</li>');
				continue;
			}
			closeList();
			paraBuf.push(line);
		}
		flushPara();
		closeList();
		return out.join('');
	}

	function uuid(): string {
		if (typeof crypto !== 'undefined' && 'randomUUID' in crypto) return crypto.randomUUID();
		return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
			const r = (Math.random() * 16) | 0;
			return (c === 'x' ? r : (r & 0x3) | 0x8).toString(16);
		});
	}

	async function loadSessions() {
		try {
			const r = await fetch(`${API}/api/sessions`);
			if (!r.ok) return;
			const data = await r.json();
			sessions = data.sessions ?? [];
		} catch (e) {
			console.error('loadSessions failed', e);
		}
	}

	async function loadHistory(id: string) {
		loadingHistory = true;
		try {
			const r = await fetch(`${API}/api/history/${id}`);
			if (!r.ok) {
				messages = [];
				return;
			}
			const data = await r.json();
			messages = (data.messages ?? []).map((m: any) => ({
				role: m.role,
				content: m.content
			}));
		} catch (e) {
			console.error('loadHistory failed', e);
			messages = [];
		} finally {
			loadingHistory = false;
			scrollToBottom();
		}
	}

	function newChat() {
		activeSessionId = uuid();
		messages = [];
		input = '';
	}

	async function selectSession(id: string) {
		if (id === activeSessionId) return;
		activeSessionId = id;
		await loadHistory(id);
	}

	async function deleteSession(id: string, e: MouseEvent) {
		e.stopPropagation();
		try {
			await fetch(`${API}/api/sessions/${id}`, { method: 'DELETE' });
		} catch (err) {
			console.error('deleteSession failed', err);
		}
		sessions = sessions.filter((s) => s.session_id !== id);
		if (activeSessionId === id) {
			activeSessionId = null;
			messages = [];
		}
	}

	function scrollToBottom() {
		queueMicrotask(() => {
			if (messagesEl) messagesEl.scrollTop = messagesEl.scrollHeight;
		});
	}

	async function send() {
		const text = input.trim();
		if (!text || sending) return;

		// Ensure we have a session id
		if (!activeSessionId) activeSessionId = uuid();
		const sid = activeSessionId;
		const isNewSession = !sessions.some((s) => s.session_id === sid);

		messages = [...messages, { role: 'user', content: text }, { role: 'assistant', content: '' }];
		const assistantIdx = messages.length - 1;
		input = '';
		sending = true;
		scrollToBottom();

		try {
			const r = await fetch(`${API}/api/chat/stream`, {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ message: text, session_id: sid, personality })
			});

			if (!r.ok || !r.body) {
				messages[assistantIdx].content = `Error: ${r.status} ${r.statusText}`;
				return;
			}

			const reader = r.body.getReader();
			const decoder = new TextDecoder();
			let buffer = '';

			while (true) {
				const { value, done } = await reader.read();
				if (done) break;
				buffer += decoder.decode(value, { stream: true });

				// SSE frames are separated by blank lines
				const parts = buffer.split('\n\n');
				buffer = parts.pop() ?? '';

				for (const part of parts) {
					const line = part.split('\n').find((l) => l.startsWith('data: '));
					if (!line) continue;
					try {
						const evt = JSON.parse(line.slice(6));
						if (evt.type === 'token') {
							messages[assistantIdx].content += evt.text;
							scrollToBottom();
						} else if (evt.type === 'error') {
							messages[assistantIdx].content = `Error: ${evt.text}`;
						}
					} catch {}
				}
			}
		} catch (e) {
			messages[assistantIdx].content = `Error: ${(e as Error).message}`;
		} finally {
			sending = false;
			// If this was a brand-new chat, prepend to sidebar
			if (isNewSession) {
				sessions = [
					{ session_id: sid, title: text.slice(0, 60), created_at: new Date().toISOString() },
					...sessions
				];
			}
		}
	}

	function onKey(e: KeyboardEvent) {
		if (e.key === 'Enter' && !e.shiftKey) {
			e.preventDefault();
			send();
		}
	}

	onMount(async () => {
		const { data: { session } } = await supabase.auth.getSession();
		if (!session) {
			goto('/login');
			return;
		}
		loadSessions();
		newChat();
	});
</script>

<div class="app">
	<!-- ── Sidebar ─────────────────────────────────────────────────── -->
	<aside class="sidebar">
		<button class="new-chat" onclick={newChat}>
			<span class="plus">+</span> New chat
		</button>
		<div class="sessions-label">Past chats</div>
		<div class="sessions">
			{#each sessions as s (s.session_id)}
				<button
					class="session"
					class:active={s.session_id === activeSessionId}
					onclick={() => selectSession(s.session_id)}
				>
					<span class="session-title">{s.title || 'Untitled'}</span>
					<span
						class="del"
						role="button"
						tabindex="0"
						onclick={(e) => deleteSession(s.session_id, e)}
						onkeydown={(e) => e.key === 'Enter' && deleteSession(s.session_id, e as any)}
						title="Delete chat"
					>
						×
					</span>
				</button>
			{/each}
			{#if sessions.length === 0}
				<div class="empty">No past chats</div>
			{/if}
		</div>
		<button class="signout" onclick={async () => { await supabase.auth.signOut(); goto('/'); }}>
			Sign out
		</button>
	</aside>

	<!-- ── Main chat ───────────────────────────────────────────────── -->
	<main class="main">
		<div class="messages" bind:this={messagesEl}>
			{#if loadingHistory}
				<div class="welcome"><p>Loading...</p></div>
			{:else if messages.length === 0}
				<div class="welcome">
					<h1>Market Chat</h1>
					<p>Ask about any stock — price, news, sentiment.</p>
				</div>
			{:else}
				{#each messages as m, i (i)}
					<div class="msg {m.role}">
						<div class="bubble">
							{#if m.content}
								{#if m.role === 'assistant'}
									{@html renderMarkdown(m.content)}
								{:else}
									{m.content}
								{/if}
							{:else if m.role === 'assistant' && sending && i === messages.length - 1}
								<span class="dots"><span></span><span></span><span></span></span>
							{/if}
						</div>
					</div>
				{/each}
			{/if}
		</div>

		<!-- ── Input bar ──────────────────────────────────────────── -->
		<div class="input-wrap">
			<div class="input-box">
				<textarea
					bind:value={input}
					onkeydown={onKey}
					placeholder="Ask about a stock..."
					rows="1"
					disabled={sending}
				></textarea>
				<div class="input-actions">
					<div class="mode">
						<button class="mode-btn" onclick={() => (modeOpen = !modeOpen)}>
							{personality === 'professional' ? 'Professional' : 'WSB'}
							<span class="caret">▾</span>
						</button>
						{#if modeOpen}
							<div class="mode-menu">
								<button
									onclick={() => {
										personality = 'professional';
										modeOpen = false;
									}}
									class:sel={personality === 'professional'}
								>
									Professional
								</button>
								<button
									onclick={() => {
										personality = 'wsb';
										modeOpen = false;
									}}
									class:sel={personality === 'wsb'}
								>
									WSB
								</button>
							</div>
						{/if}
					</div>
					<button class="send" onclick={send} disabled={!input.trim() || sending}>
						{sending ? '...' : 'Send'}
					</button>
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
		font-family: 'Overused Grotesk', -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui,
			sans-serif;
	}

	/* ── Sidebar ──────────────────────────────────────────────── */
	.sidebar {
		width: 260px;
		flex-shrink: 0;
		border-right: 1px solid #1a1a1a;
		display: flex;
		flex-direction: column;
		padding: 14px 10px;
		background: #080808;
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
	}
	.signout:hover {
		color: #eaeaea;
	}

	/* ── Main ─────────────────────────────────────────────────── */
	.main {
		flex: 1;
		display: flex;
		flex-direction: column;
		min-width: 0;
	}
	.messages {
		flex: 1;
		overflow-y: auto;
		padding: 32px 10%;
		display: flex;
		flex-direction: column;
		gap: 18px;
	}
	.welcome {
		margin: auto;
		text-align: center;
		color: #888;
	}
	.welcome h1 {
		font-size: 28px;
		font-weight: 500;
		color: #eaeaea;
		margin: 0 0 8px;
	}
	.welcome p {
		margin: 0;
		font-size: 14px;
	}

	.msg {
		display: flex;
	}
	.msg.user {
		justify-content: flex-end;
	}
	.msg.assistant {
		justify-content: flex-start;
	}
	.bubble {
		max-width: 75%;
		padding: 12px 16px;
		border-radius: 14px;
		line-height: 1.55;
		white-space: pre-wrap;
		word-wrap: break-word;
	}
	.msg.user .bubble {
		background: #1a1a1a;
		color: #eaeaea;
		border: 1px solid #242424;
	}
	.msg.assistant .bubble {
		background: transparent;
		color: #eaeaea;
		border: 1px solid #1c1c1c;
	}
	.msg.assistant .bubble :global(p) {
		margin: 0 0 10px;
	}
	.msg.assistant .bubble :global(p:last-child) {
		margin-bottom: 0;
	}
	.msg.assistant .bubble :global(h1),
	.msg.assistant .bubble :global(h2),
	.msg.assistant .bubble :global(h3),
	.msg.assistant .bubble :global(h4) {
		font-size: 14px;
		font-weight: 600;
		margin: 14px 0 6px;
		color: #fff;
	}
	.msg.assistant .bubble :global(h1:first-child),
	.msg.assistant .bubble :global(h2:first-child),
	.msg.assistant .bubble :global(h3:first-child) {
		margin-top: 0;
	}
	.msg.assistant .bubble :global(ul) {
		margin: 6px 0 10px;
		padding-left: 20px;
	}
	.msg.assistant .bubble :global(li) {
		margin: 3px 0;
	}
	.msg.assistant .bubble :global(strong) {
		color: #fff;
		font-weight: 600;
	}
	.msg.assistant .bubble :global(em) {
		color: #cfcfcf;
		font-style: italic;
	}
	.msg.assistant .bubble :global(a) {
		color: #9cc4ff;
		text-decoration: none;
		border-bottom: 1px solid #2a4a7a;
		transition: color 0.15s, border-color 0.15s;
	}
	.msg.assistant .bubble :global(a:hover) {
		color: #cfe0ff;
		border-bottom-color: #5a7ab0;
	}
	.msg.assistant .bubble :global(code) {
		background: #1a1a1a;
		border: 1px solid #262626;
		border-radius: 4px;
		padding: 1px 5px;
		font-family: 'SF Mono', Menlo, Consolas, monospace;
		font-size: 12px;
	}

	.dots {
		display: inline-flex;
		gap: 4px;
		align-items: center;
	}
	.dots span {
		width: 6px;
		height: 6px;
		background: #666;
		border-radius: 50%;
		animation: blink 1.4s infinite both;
	}
	.dots span:nth-child(2) {
		animation-delay: 0.2s;
	}
	.dots span:nth-child(3) {
		animation-delay: 0.4s;
	}
	@keyframes blink {
		0%, 80%, 100% { opacity: 0.2; }
		40% { opacity: 1; }
	}

	/* ── Input ────────────────────────────────────────────────── */
	.input-wrap {
		padding: 16px 10% 24px;
	}
	.input-box {
		background: #0e0e0e;
		border: 1px solid #262626;
		border-radius: 16px;
		padding: 12px 14px 10px;
		transition: border-color 0.15s;
	}
	.input-box:focus-within {
		border-color: #3a3a3a;
	}
	.input-box textarea {
		width: 100%;
		background: transparent;
		border: none;
		outline: none;
		color: #eaeaea;
		font-family: inherit;
		font-size: 14px;
		resize: none;
		line-height: 1.5;
		max-height: 200px;
	}
	.input-box textarea::placeholder {
		color: #555;
	}
	.input-actions {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-top: 8px;
	}

	.mode {
		position: relative;
	}
	.mode-btn {
		background: #151515;
		border: 1px solid #262626;
		color: #cfcfcf;
		padding: 6px 10px;
		border-radius: 999px;
		font-size: 12px;
		cursor: pointer;
		display: inline-flex;
		align-items: center;
		gap: 6px;
	}
	.mode-btn:hover {
		background: #1c1c1c;
		border-color: #333;
	}
	.caret {
		font-size: 10px;
		opacity: 0.7;
	}
	.mode-menu {
		position: absolute;
		bottom: calc(100% + 6px);
		left: 0;
		background: #111;
		border: 1px solid #262626;
		border-radius: 10px;
		overflow: hidden;
		min-width: 140px;
		box-shadow: 0 10px 30px rgba(0, 0, 0, 0.6);
		z-index: 10;
	}
	.mode-menu button {
		display: block;
		width: 100%;
		background: transparent;
		border: none;
		text-align: left;
		padding: 9px 12px;
		color: #cfcfcf;
		font-size: 13px;
		cursor: pointer;
	}
	.mode-menu button:hover {
		background: #1a1a1a;
	}
	.mode-menu button.sel {
		color: #fff;
	}

	.send {
		background: #eaeaea;
		color: #000;
		border: none;
		padding: 7px 16px;
		border-radius: 999px;
		font-size: 13px;
		font-weight: 500;
		cursor: pointer;
	}
	.send:hover:not(:disabled) {
		background: #fff;
	}
	.send:disabled {
		background: #2a2a2a;
		color: #555;
		cursor: not-allowed;
	}
</style>
