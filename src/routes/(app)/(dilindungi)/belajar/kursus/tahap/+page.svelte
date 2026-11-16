<script lang="ts">
	import { resolve } from '$app/paths';
	import { page } from '$app/state';
	import ArrowLeft from '@lucide/svelte/icons/arrow-left';
	import CircleCheck from '@lucide/svelte/icons/circle-check';
	import Circle from '@lucide/svelte/icons/circle';
	import Lock from '@lucide/svelte/icons/lock';
	import { PLANS, planIncludes } from '#lib/content/site.js';
	import { courses } from '#lib/courses/store.svelte.js';
	import { m } from '#lib/paraglide/messages.js';
	import Notice from '#lib/ui/Notice.svelte';
	import Spinner from '#lib/ui/Spinner.svelte';

	// The level is chosen with ?n=1 rather than /tahap/1, so this page is one
	// static file that also opens offline.
	const number = $derived(Number(page.url.searchParams.get('n')));
	const level = $derived(courses.catalog?.find((candidate) => candidate.number === number));
	const open = $derived(level ? planIncludes(courses.plan, level.plan) : false);

	const allLevels = resolve('/(app)/(dilindungi)/belajar/kursus');
	const lessonPage = resolve('/(app)/(dilindungi)/belajar/kursus/pelajaran');
</script>

<svelte:head>
	<title>{level?.title ?? m.courses_title()} · AQRJ</title>
</svelte:head>

<a href={allLevels} class="inline-flex min-h-11 items-center gap-2 text-ink-soft">
	<ArrowLeft size={18} aria-hidden="true" />
	{m.courses_back_to_all()}
</a>

{#if courses.loadFailed}
	<div class="mt-4"><Notice tone="error">{m.courses_load_error()}</Notice></div>
{:else if courses.catalog === null}
	<Spinner />
{:else if !level}
	<div class="mt-4"><Notice>{m.courses_not_found()}</Notice></div>
{:else}
	<p class="mt-2 text-sm font-semibold text-brand-700">
		{m.courses_level({ number: level.number })}
	</p>
	<h1 class="text-2xl font-bold">{level.title}</h1>
	<p class="mt-1 text-ink-soft">{level.summary}</p>

	{#if !open}
		{@const plan = PLANS.find((candidate) => candidate.id === level.plan)?.name ?? level.plan}
		<div class="mt-5">
			<Notice title={m.courses_locked({ plan })}>{m.courses_locked_body({ plan })}</Notice>
		</div>
	{/if}

	<ol class="mt-6 space-y-2">
		{#each level.lessons as lesson (lesson.id)}
			{@const done = courses.completed.has(lesson.id)}
			<li>
				{#if open}
					<a
						href="{lessonPage}?id={lesson.id}"
						class="card flex min-h-14 items-center gap-3 py-3 hover:border-brand-400"
					>
						{#if done}
							<CircleCheck size={22} class="shrink-0 text-brand-700" aria-hidden="true" />
							<span class="sr-only">{m.lesson_done()}:</span>
						{:else}
							<Circle size={22} class="shrink-0 text-sand-300" aria-hidden="true" />
						{/if}
						<span class="flex-1">{lesson.title}</span>
					</a>
				{:else}
					<div class="card flex min-h-14 items-center gap-3 py-3 text-ink-soft">
						<Lock size={20} class="shrink-0" aria-hidden="true" />
						<span class="flex-1">{lesson.title}</span>
					</div>
				{/if}
			</li>
		{/each}
	</ol>
{/if}
