<script lang="ts">
	import { goto } from '$app/navigation';
	import { resolve } from '$app/paths';
	import Plus from '@lucide/svelte/icons/plus';
	import { learners } from '#lib/learners/store.svelte.js';
	import { m } from '#lib/paraglide/messages.js';
	import Notice from '#lib/ui/Notice.svelte';
	import Spinner from '#lib/ui/Spinner.svelte';

	$effect(() => {
		void learners.load();
	});

	// With no learners yet there is nothing to pick, so go straight to the form.
	$effect(() => {
		if (learners.list !== null && learners.list.length === 0) {
			void goto(resolve('/(app)/(dilindungi)/pilih/baru'), { replace: true });
		}
	});

	function choose(id: string) {
		learners.choose(id);
		void goto(resolve('/(app)/(dilindungi)/belajar'));
	}

	function initial(name: string): string {
		return name.trim().charAt(0).toUpperCase();
	}
</script>

<svelte:head>
	<title>{m.pick_page_title()}</title>
</svelte:head>

<main class="mx-auto w-full max-w-md px-4 py-10">
	<h1 class="text-3xl font-bold">{m.pick_title()}</h1>
	<p class="mt-2 text-lg text-ink-soft">{m.pick_lead()}</p>

	{#if learners.loadFailed}
		<div class="mt-8 space-y-4">
			<Notice tone="error">{m.pick_load_error()}</Notice>
			<button type="button" class="btn btn-secondary" onclick={() => learners.load(true)}>
				{m.common_retry()}
			</button>
		</div>
	{:else if learners.list === null || learners.list.length === 0}
		<Spinner />
	{:else}
		<ul class="mt-8 space-y-3">
			{#each learners.list as learner (learner.id)}
				<li>
					<button
						type="button"
						class={[
							'card flex w-full items-center gap-4 text-left hover:border-brand-400',
							learner.id === learners.activeId && 'border-brand-500'
						]}
						onclick={() => choose(learner.id)}
					>
						<span
							class="flex size-12 shrink-0 items-center justify-center rounded-full bg-brand-700 text-xl font-bold text-white"
							aria-hidden="true"
						>
							{initial(learner.display_name)}
						</span>
						<span class="min-w-0 flex-1 truncate text-lg font-semibold">
							{learner.display_name}
						</span>
						{#if learner.is_self}
							<span class="rounded-full bg-sand-100 px-3 py-1 text-sm text-ink-soft">
								{m.pick_self_badge()}
							</span>
						{/if}
					</button>
				</li>
			{/each}
		</ul>

		<a href={resolve('/(app)/(dilindungi)/pilih/baru')} class="btn btn-secondary mt-6 w-full">
			<Plus size={20} aria-hidden="true" />
			{m.pick_add()}
		</a>
	{/if}
</main>
