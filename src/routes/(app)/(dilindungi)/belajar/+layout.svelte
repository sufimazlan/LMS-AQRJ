<script lang="ts">
	import { goto } from '$app/navigation';
	import { resolve } from '$app/paths';
	import { learners } from '#lib/learners/store.svelte.js';
	import { m } from '#lib/paraglide/messages.js';
	import Notice from '#lib/ui/Notice.svelte';
	import Spinner from '#lib/ui/Spinner.svelte';
	import TabBar from '#lib/ui/TabBar.svelte';
	import type { LayoutProps } from './$types';

	let { children }: LayoutProps = $props();

	$effect(() => {
		void learners.load();
	});

	// The learning area always needs to know who is learning.
	$effect(() => {
		if (learners.list === null) return;

		if (learners.list.length === 0) {
			void goto(resolve('/(app)/(dilindungi)/pilih/baru'), { replace: true });
		} else if (learners.active === null) {
			void goto(resolve('/(app)/(dilindungi)/pilih'), { replace: true });
		}
	});
</script>

{#if learners.active}
	<div class="md:flex">
		<TabBar />
		<main class="mx-auto w-full max-w-2xl px-4 pt-6 pb-28 md:px-8 md:pb-10">
			{@render children()}
		</main>
	</div>
{:else if learners.loadFailed}
	<main class="mx-auto flex min-h-dvh w-full max-w-md flex-col justify-center gap-4 px-4">
		<Notice tone="error">{m.pick_load_error()}</Notice>
		<button type="button" class="btn btn-secondary" onclick={() => learners.load(true)}>
			{m.common_retry()}
		</button>
	</main>
{:else}
	<Spinner fullPage />
{/if}
