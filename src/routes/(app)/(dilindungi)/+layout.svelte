<script lang="ts">
	import { goto } from '$app/navigation';
	import { resolve } from '$app/paths';
	import { auth } from '#lib/auth/session.svelte.js';
	import { learners } from '#lib/learners/store.svelte.js';
	import Spinner from '#lib/ui/Spinner.svelte';
	import type { LayoutProps } from './$types';

	let { children }: LayoutProps = $props();

	// "dilindungi" = protected. Pages in this group need a signed-in account.
	// This guard is a convenience for the person, not the security boundary:
	// row-level security in the database is what protects the data.
	$effect(() => {
		if (auth.status === 'signed-out' || auth.status === 'unconfigured') {
			learners.reset();
			void goto(resolve('/(app)/masuk'), { replace: true });
		}
	});
</script>

{#if auth.status === 'signed-in'}
	{@render children()}
{:else}
	<Spinner fullPage />
{/if}
