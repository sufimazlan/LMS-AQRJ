<script lang="ts">
	import { m } from '#lib/paraglide/messages.js';

	let { label = m.common_loading(), fullPage = false }: { label?: string; fullPage?: boolean } =
		$props();
</script>

<div
	role="status"
	class={fullPage ? 'flex min-h-dvh items-center justify-center' : 'flex justify-center py-10'}
>
	<span
		class="size-8 animate-spin rounded-full border-4 border-brand-200 border-t-brand-700 motion-reduce:animate-none"
		aria-hidden="true"
	></span>
	<span class="sr-only">{label}</span>
</div>
