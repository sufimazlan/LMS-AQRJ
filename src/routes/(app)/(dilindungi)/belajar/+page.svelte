<script lang="ts">
	import { learners } from '#lib/learners/store.svelte.js';
	import { m } from '#lib/paraglide/messages.js';
	import InstallPrompt from '#lib/ui/InstallPrompt.svelte';
</script>

<svelte:head>
	<title>{m.home_page_title()}</title>
</svelte:head>

<h1 class="text-2xl font-bold">
	{m.home_greeting({ name: learners.active?.display_name ?? '' })}
</h1>

<div class="mt-6 space-y-4">
	<!-- Milestone 1 turns this into the single big "continue where you stopped" button. -->
	<section class="card" aria-labelledby="continue-title">
		<h2 id="continue-title" class="text-lg font-semibold">{m.home_continue_title()}</h2>
		<p class="mt-1 text-ink-soft">{m.home_continue_empty()}</p>
	</section>

	<InstallPrompt />
</div>
