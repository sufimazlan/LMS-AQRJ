<script lang="ts">
	import { resolve } from '$app/paths';
	import ChevronRight from '@lucide/svelte/icons/chevron-right';
	import Lock from '@lucide/svelte/icons/lock';
	import { PLANS, planIncludes, type PlanId } from '#lib/content/site.js';
	import { countDone } from '#lib/courses/catalog.js';
	import { courses } from '#lib/courses/store.svelte.js';
	import { learners } from '#lib/learners/store.svelte.js';
	import { m } from '#lib/paraglide/messages.js';
	import Notice from '#lib/ui/Notice.svelte';
	import Spinner from '#lib/ui/Spinner.svelte';

	const levelPage = resolve('/(app)/(dilindungi)/belajar/kursus/tahap');
	const planName = (id: PlanId) => PLANS.find((plan) => plan.id === id)?.name ?? id;

	function retry() {
		if (learners.active) void courses.load(learners.active.id, true);
	}
</script>

<svelte:head>
	<title>{m.courses_page_title()}</title>
</svelte:head>

<h1 class="text-2xl font-bold">{m.courses_title()}</h1>

{#if courses.loadFailed}
	<div class="mt-6 space-y-4">
		<Notice tone="error">{m.courses_load_error()}</Notice>
		<button type="button" class="btn btn-secondary" onclick={retry}>{m.common_retry()}</button>
	</div>
{:else if courses.catalog === null}
	<Spinner />
{:else if courses.catalog.length === 0}
	<div class="mt-6"><Notice>{m.courses_empty()}</Notice></div>
{:else}
	<ol class="mt-6 space-y-3">
		{#each courses.catalog as level (level.id)}
			{@const open = planIncludes(courses.plan, level.plan)}
			{@const done = countDone(level, courses.completed)}
			<li>
				<a
					href="{levelPage}?n={level.number}"
					class="card flex items-center gap-4 hover:border-brand-400"
				>
					<span
						class={[
							'flex size-10 shrink-0 items-center justify-center rounded-full font-bold',
							open ? 'bg-brand-700 text-white' : 'bg-sand-200 text-ink-soft'
						]}
						aria-hidden="true"
					>
						{level.number}
					</span>
					<span class="min-w-0 flex-1">
						<span class="block font-semibold">
							<span class="sr-only">{m.courses_level({ number: level.number })}:</span>
							{level.title}
						</span>
						{#if open}
							<span class="block text-sm text-ink-soft">
								{m.courses_progress({ done, total: level.lessons.length })}
							</span>
							<progress
								class="mt-1 block h-1.5 w-full accent-brand-700"
								value={done}
								max={Math.max(level.lessons.length, 1)}
							></progress>
						{:else}
							<span class="flex items-center gap-1 text-sm text-ink-soft">
								<Lock size={14} aria-hidden="true" />
								{m.courses_locked({ plan: planName(level.plan) })}
							</span>
						{/if}
					</span>
					<ChevronRight size={20} class="shrink-0 text-ink-soft" aria-hidden="true" />
				</a>
			</li>
		{/each}
	</ol>
{/if}
