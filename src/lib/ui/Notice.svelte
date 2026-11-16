<script lang="ts">
	import type { Snippet } from 'svelte';

	type Tone = 'info' | 'success' | 'error';

	let {
		tone = 'info',
		title,
		children
	}: { tone?: Tone; title?: string; children: Snippet } = $props();

	const tones: Record<Tone, string> = {
		info: 'border-sand-300 bg-sand-100 text-ink',
		success: 'border-brand-200 bg-brand-50 text-brand-900',
		error: 'border-red-200 bg-red-50 text-red-900'
	};
</script>

<div
	role={tone === 'error' ? 'alert' : 'status'}
	class={['rounded-xl border px-4 py-3 text-base', tones[tone]]}
>
	{#if title}
		<p class="font-semibold">{title}</p>
	{/if}
	<div class={title ? 'mt-1' : ''}>{@render children()}</div>
</div>
