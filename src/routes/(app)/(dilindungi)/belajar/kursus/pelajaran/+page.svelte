<script lang="ts">
	import { resolve } from '$app/paths';
	import { page } from '$app/state';
	import ArrowLeft from '@lucide/svelte/icons/arrow-left';
	import ArrowRight from '@lucide/svelte/icons/arrow-right';
	import CircleCheck from '@lucide/svelte/icons/circle-check';
	import { planIncludes } from '#lib/content/site.js';
	import { completeLesson, loadLessonDetail, type LessonDetail } from '#lib/courses/api.js';
	import { findLesson } from '#lib/courses/catalog.js';
	import { courses } from '#lib/courses/store.svelte.js';
	import { learners } from '#lib/learners/store.svelte.js';
	import { m } from '#lib/paraglide/messages.js';
	import Notice from '#lib/ui/Notice.svelte';
	import Quiz from '#lib/ui/Quiz.svelte';
	import Spinner from '#lib/ui/Spinner.svelte';
	import VideoPlayer from '#lib/ui/VideoPlayer.svelte';

	const lessonId = $derived(page.url.searchParams.get('id') ?? '');
	const place = $derived(
		courses.catalog ? findLesson(courses.catalog, lessonId, courses.plan) : null
	);
	const open = $derived(place ? planIncludes(courses.plan, place.level.plan) : false);
	const done = $derived(courses.completed.has(lessonId));

	let detail = $state<LessonDetail | null>(null);
	let detailFailed = $state(false);
	let saving = $state(false);
	let saveFailed = $state(false);

	// Fetch the video link and quiz whenever the lesson changes.
	$effect(() => {
		const id = lessonId;
		detail = null;
		detailFailed = false;
		saveFailed = false;
		if (!place || !open) return;

		loadLessonDetail(id)
			.then((loaded) => {
				if (id === lessonId) detail = loaded;
			})
			.catch(() => {
				if (id === lessonId) detailFailed = true;
			});
	});

	async function markDone() {
		if (!learners.active) return;
		saving = true;
		saveFailed = false;
		try {
			await completeLesson(learners.active.id, lessonId);
			courses.markCompleted(lessonId);
		} catch {
			saveFailed = true;
		}
		saving = false;
	}

	const levelPage = resolve('/(app)/(dilindungi)/belajar/kursus/tahap');
	const lessonPage = resolve('/(app)/(dilindungi)/belajar/kursus/pelajaran');
</script>

<svelte:head>
	<title>{place?.lesson.title ?? m.lesson_page_title()} · AQRJ</title>
</svelte:head>

{#if courses.loadFailed}
	<Notice tone="error">{m.courses_load_error()}</Notice>
{:else if courses.catalog === null}
	<Spinner />
{:else if !place || !open}
	<Notice>{m.courses_not_found()}</Notice>
{:else}
	<a
		href="{levelPage}?n={place.level.number}"
		class="inline-flex min-h-11 items-center gap-2 text-ink-soft"
	>
		<ArrowLeft size={18} aria-hidden="true" />
		{m.courses_level({ number: place.level.number })}: {place.level.title}
	</a>

	<h1 class="mt-2 flex items-start gap-2 text-2xl font-bold">
		<span class="flex-1">{place.lesson.title}</span>
		{#if done}
			<span
				class="mt-1 inline-flex shrink-0 items-center gap-1 rounded-full bg-brand-50 px-3 py-1 text-sm font-medium text-brand-800"
			>
				<CircleCheck size={16} aria-hidden="true" />
				{m.lesson_done()}
			</span>
		{/if}
	</h1>

	{#if detailFailed}
		<div class="mt-4"><Notice tone="error">{m.courses_load_error()}</Notice></div>
	{:else if detail === null}
		<Spinner />
	{:else}
		<div class="mt-4">
			<VideoPlayer videoRef={detail.video?.ref ?? ''} title={place.lesson.title} />
		</div>

		{#if detail.summary}
			<p class="mt-4">{detail.summary}</p>
		{/if}

		{#if detail.questions.length > 0 && learners.active}
			{#key lessonId}
				<Quiz
					learnerId={learners.active.id}
					{lessonId}
					questions={detail.questions}
					onpassed={() => courses.markCompleted(lessonId)}
				/>
			{/key}
		{:else if !done}
			{#if saveFailed}
				<div class="mt-4"><Notice tone="error">{m.common_error_generic()}</Notice></div>
			{/if}
			<button
				type="button"
				class="btn btn-primary mt-6 w-full"
				onclick={markDone}
				disabled={saving}
			>
				<CircleCheck size={20} aria-hidden="true" />
				{m.lesson_mark_done()}
			</button>
		{/if}

		{#if done}
			{#if place.next}
				<a href="{lessonPage}?id={place.next.id}" class="btn btn-primary mt-6 w-full">
					{m.lesson_next()}: {place.next.title}
					<ArrowRight size={20} aria-hidden="true" />
				</a>
			{:else}
				<a href="{levelPage}?n={place.level.number}" class="btn btn-secondary mt-6 w-full">
					{m.lesson_back_to_level()}
				</a>
			{/if}
		{/if}
	{/if}
{/if}
