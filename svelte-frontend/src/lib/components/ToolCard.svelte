<script lang="ts">
	import SkeletonCard from './SkeletonCard.svelte';
	import PriceCard from './PriceCard.svelte';
	import FinancialsCard from '$lib/components/FinancialsCard.svelte';
	import ChartCard from '$lib/components/ChartCard.svelte';
	import InsiderCard from '$lib/components/InsiderCard.svelte';
	import NewsCard from '$lib/components/NewsCard.svelte';

	type ToolCall = {
		tool: string;
		input: Record<string, any>;
		status: 'loading' | 'done' | 'error';
		result?: Record<string, any>;
	};

	let { toolCall } = $props<{ toolCall: ToolCall }>();
</script>

{#if toolCall.status === 'loading'}
	<SkeletonCard tool={toolCall.tool} />
{:else if toolCall.tool === 'get_price'}
	<PriceCard data={toolCall.result ?? {}} />
{:else if toolCall.tool === 'get_financials'}
	<FinancialsCard data={toolCall.result ?? {}} />
{:else if toolCall.tool === 'get_chart_data'}
	<ChartCard data={toolCall.result ?? {}} />
{:else if toolCall.tool === 'get_insider_trades'}
	<InsiderCard data={toolCall.result ?? {}} />
{:else if toolCall.tool === 'get_news'}
	<NewsCard data={toolCall.result ?? {}} />
{:else}
	<div class="tool-fallback">
		<div class="head">{toolCall.tool}</div>
		{#if toolCall.result?.error}
			<div class="error">{toolCall.result.error}</div>
		{:else}
			<pre>{JSON.stringify(toolCall.result ?? {}, null, 2)}</pre>
		{/if}
	</div>
{/if}

<style>
	.tool-fallback {
		background: #0a0a0a;
		border: 1px solid #1a1a1a;
		border-left: 4px solid #6b6b6b;
		border-radius: 8px;
		padding: 12px;
	}
	.head {
		font-size: 12px;
		letter-spacing: 0.04em;
		text-transform: uppercase;
		color: #9b9b9b;
		margin-bottom: 8px;
	}
	.error {
		color: #ff6b6b;
	}
	pre {
		margin: 0;
		white-space: pre-wrap;
		font-size: 12px;
		color: #cdcdcd;
	}
</style>
