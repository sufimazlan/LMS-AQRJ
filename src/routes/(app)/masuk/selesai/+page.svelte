<script lang="ts">
	import { goto } from '$app/navigation';
	import { resolve } from '$app/paths';
	import { page } from '$app/state';
	import { auth } from '#lib/auth/session.svelte.js';
	import { m } from '#lib/paraglide/messages.js';
	import Notice from '#lib/ui/Notice.svelte';
	import Spinner from '#lib/ui/Spinner.svelte';

	// Google and the email link both land here. The Supabase client finishes the
	// sign-in from the address by itself; this page only waits for the result.
	// A failed or expired link is reported in the query string or the hash.
	const linkError = page.url.searchParams.has('error') || page.url.hash.includes('error=');

	const failed = $derived(auth.status !== 'signed-in' && (linkError || auth.status !== 'loading'));

	$effect(() => {
		if (auth.status === 'signed-in') {
			void goto(resolve('/(app)/(dilindungi)/belajar'), { replace: true });
		}
	});
</script>

<svelte:head>
	<title>{m.signin_page_title()}</title>
</svelte:head>

{#if failed}
	<main class="mx-auto flex min-h-dvh w-full max-w-md flex-col justify-center gap-5 px-4 py-10">
		<Notice tone="error" title={m.callback_failed_title()}>{m.callback_failed_body()}</Notice>
		<a href={resolve('/(app)/masuk')} class="btn btn-primary">{m.callback_back()}</a>
	</main>
{:else}
	<Spinner fullPage label={m.callback_working()} />
{/if}
