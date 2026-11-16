<script lang="ts">
	import Lock from '@lucide/svelte/icons/lock';
	import { PLANS, SYLLABUS, planIncludes, type PlanId } from '#lib/content/site.js';
	import { m } from '#lib/paraglide/messages.js';
	import Notice from '#lib/ui/Notice.svelte';

	// Until payments are live (Milestone 3), every learner is on the free plan.
	// Milestone 1 replaces this list with lessons read from the database.
	const owned: PlanId = 'percuma';

	const planName = (id: PlanId) => PLANS.find((plan) => plan.id === id)?.name ?? id;
</script>

<svelte:head>
	<title>{m.courses_page_title()}</title>
</svelte:head>

<h1 class="text-2xl font-bold">{m.courses_title()}</h1>

<div class="mt-4">
	<Notice>{m.courses_empty()}</Notice>
</div>

<ol class="mt-6 space-y-3">
	{#each SYLLABUS as level (level.number)}
		{@const open = planIncludes(owned, level.plan)}
		<li class={['card flex items-center gap-4', !open && 'opacity-70']}>
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
				<span class="block font-semibold">{level.title}</span>
				<span class="block text-sm text-ink-soft">{level.summary}</span>
			</span>
			{#if !open}
				<span class="flex shrink-0 items-center gap-1 text-sm text-ink-soft">
					<Lock size={16} aria-hidden="true" />
					{planName(level.plan)}
				</span>
			{/if}
		</li>
	{/each}
</ol>
