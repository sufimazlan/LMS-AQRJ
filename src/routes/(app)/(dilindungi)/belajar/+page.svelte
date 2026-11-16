<script lang="ts">
	import { resolve } from '$app/paths';
	import ArrowRight from '@lucide/svelte/icons/arrow-right';
	import { nextLesson } from '#lib/courses/catalog.js';
	import { courses } from '#lib/courses/store.svelte.js';
	import { learners } from '#lib/learners/store.svelte.js';
	import { m } from '#lib/paraglide/messages.js';
	import InstallPrompt from '#lib/ui/InstallPrompt.svelte';

	const lessonPage = resolve('/(app)/(dilindungi)/belajar/kursus/pelajaran');

	const next = $derived(
		courses.catalog ? nextLesson(courses.catalog, courses.completed, courses.plan) : null
	);
	const hasLessons = $derived(courses.catalog?.some((level) => level.lessons.length > 0) ?? false);
</script>

<svelte:head>
	<title>{m.home_page_title()}</title>
</svelte:head>

<h1 class="text-2xl font-bold">
	{m.home_greeting({ name: learners.active?.display_name ?? '' })}
</h1>

<div class="mt-6 space-y-4">
	<section class="card" aria-labelledby="continue-title">
		<h2 id="continue-title" class="text-lg font-semibold">{m.home_continue_title()}</h2>
		{#if courses.loadFailed}
			<p class="mt-1 text-ink-soft">{m.courses_load_error()}</p>
		{:else if courses.catalog === null}
			<p class="mt-1 text-ink-soft">{m.common_loading()}</p>
		{:else if next}
			<a href="{lessonPage}?id={next.id}" class="btn btn-primary mt-3 w-full text-lg">
				{m.home_continue_button({ title: next.title })}
				<ArrowRight size={20} aria-hidden="true" />
			</a>
		{:else if hasLessons}
			<p class="mt-1 text-ink-soft">{m.home_all_done()}</p>
		{:else}
			<p class="mt-1 text-ink-soft">{m.home_continue_empty()}</p>
		{/if}
	</section>

	<InstallPrompt />
</div>
