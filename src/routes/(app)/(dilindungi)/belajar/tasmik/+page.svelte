<script lang="ts">
	import Mic from '@lucide/svelte/icons/mic';
	import { m } from '#lib/paraglide/messages.js';
	import EmptyState from '#lib/ui/EmptyState.svelte';
</script>

<svelte:head>
	<title>{m.tasmik_page_title()}</title>
</svelte:head>

<h1 class="text-2xl font-bold">{m.tasmik_title()}</h1>
<EmptyState icon={Mic} text={m.tasmik_empty()} />
