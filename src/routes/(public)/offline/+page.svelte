<script lang="ts">
	import WifiOff from '@lucide/svelte/icons/wifi-off';
	import { m } from '#lib/paraglide/messages.js';
</script>

<!-- The service worker serves this page when a navigation fails with no network. -->
<svelte:head>
	<title>{m.offline_page_title()}</title>
</svelte:head>

<section class="mx-auto flex w-full max-w-md flex-col items-center px-4 py-20 text-center">
	<span class="rounded-full bg-sand-100 p-4 text-ink-soft" aria-hidden="true">
		<WifiOff size={32} />
	</span>
	<h1 class="mt-5 text-2xl font-bold">{m.offline_title()}</h1>
	<p class="mt-2 text-ink-soft">{m.offline_body()}</p>
</section>
