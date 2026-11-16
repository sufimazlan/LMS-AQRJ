<script lang="ts">
	import CalendarDays from '@lucide/svelte/icons/calendar-days';
	import { m } from '#lib/paraglide/messages.js';
	import EmptyState from '#lib/ui/EmptyState.svelte';
</script>

<svelte:head>
	<title>{m.schedule_page_title()}</title>
</svelte:head>

<h1 class="text-2xl font-bold">{m.schedule_title()}</h1>
<EmptyState icon={CalendarDays} text={m.schedule_empty()} />
