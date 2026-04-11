<script lang="ts">
	let { data } = $props<{ data: Record<string, any> }>();
	let expanded = $state(false);
	const DEFAULT_VISIBLE = 3;

	const allArticles = $derived(Array.isArray(data.articles) ? data.articles : []);
	const visibleArticles = $derived(expanded ? allArticles : allArticles.slice(0, DEFAULT_VISIBLE));
</script>

<div class="card">
	{#if data.error}
		<div class="error">{data.error}</div>
	{:else}
		<div class="head">
			<div class="ticker">{data.ticker ?? 'Ticker'} News</div>
			<div class="count">{allArticles.length} articles</div>
		</div>
		{#if allArticles.length === 0}
			<div class="empty">{data.note ?? 'No recent news found'}</div>
		{:else}
			<div class="list">
				{#each visibleArticles as article}
					<article>
						<a href={article.url} target="_blank" rel="noopener noreferrer">{article.headline}</a>
						<div class="meta">{article.source} · {article.published}</div>
						<div class="summary">{article.summary}</div>
					</article>
				{/each}
			</div>
			{#if allArticles.length > DEFAULT_VISIBLE}
				<button class="more" onclick={() => (expanded = !expanded)}>
					{expanded ? 'Show less' : `Show ${allArticles.length - DEFAULT_VISIBLE} more`}
				</button>
			{/if}
		{/if}
	{/if}
</div>

<style>
	.card {
		background: #0a0a0a;
		border: 1px solid #1a1a1a;
		border-left: 4px solid #00ff41;
		border-radius: 8px;
		padding: 12px;
	}
	.head {
		display: flex;
		justify-content: space-between;
		align-items: center;
	}
	.ticker {
		font-size: 16px;
		font-weight: 600;
	}
	.count {
		font-size: 11px;
		color: #7f7f7f;
	}
	.list {
		margin-top: 10px;
		display: flex;
		flex-direction: column;
		gap: 10px;
	}
	article {
		padding-bottom: 10px;
		border-bottom: 1px solid #171717;
	}
	article:last-child {
		border-bottom: none;
		padding-bottom: 0;
	}
	a {
		color: #dfffe9;
		font-size: 13px;
		text-decoration: none;
	}
	a:hover {
		text-decoration: underline;
	}
	.meta {
		font-size: 11px;
		color: #7f7f7f;
		margin-top: 3px;
	}
	.summary {
		font-size: 12px;
		color: #acacac;
		margin-top: 4px;
		display: -webkit-box;
		-webkit-line-clamp: 1;
		line-clamp: 1;
		-webkit-box-orient: vertical;
		overflow: hidden;
	}
	.more {
		margin-top: 10px;
		background: transparent;
		border: 1px solid #214029;
		color: #9dddaa;
		font-size: 11px;
		padding: 5px 10px;
		border-radius: 999px;
		cursor: pointer;
	}
	.more:hover {
		background: #102014;
	}
	.error,
	.empty {
		margin-top: 8px;
		font-size: 13px;
		color: #ff6b6b;
	}
</style>
