<script lang="ts">
	import { goto } from '$app/navigation';
	import { resolve } from '$app/paths';
	import { auth } from '#lib/auth/session.svelte.js';
	import { m } from '#lib/paraglide/messages.js';
	import { getSupabase } from '#lib/supabase/client.js';
	import Logo from '#lib/ui/Logo.svelte';
	import Notice from '#lib/ui/Notice.svelte';

	type Step = 'form' | 'sending' | 'sent';

	let email = $state('');
	let step = $state<Step>('form');
	let failed = $state(false);
	let googleBusy = $state(false);

	$effect(() => {
		if (auth.status === 'signed-in') {
			void goto(resolve('/(app)/(dilindungi)/belajar'), { replace: true });
		}
	});

	/** Where Supabase sends the person back to after Google or the email link. */
	function returnUrl(): string {
		return new URL(resolve('/(app)/masuk/selesai'), window.location.origin).href;
	}

	async function signInWithGoogle() {
		failed = false;
		googleBusy = true;

		const { error } = await getSupabase().auth.signInWithOAuth({
			provider: 'google',
			options: { redirectTo: returnUrl() }
		});

		// On success the browser leaves for Google, so there is nothing more to do here.
		if (error) {
			failed = true;
			googleBusy = false;
		}
	}

	async function sendLink(event: SubmitEvent) {
		event.preventDefault();
		failed = false;
		step = 'sending';

		const { error } = await getSupabase().auth.signInWithOtp({
			email: email.trim(),
			options: { emailRedirectTo: returnUrl() }
		});

		if (error) {
			failed = true;
			step = 'form';
		} else {
			step = 'sent';
		}
	}
</script>

<svelte:head>
	<title>{m.signin_page_title()}</title>
</svelte:head>

<main class="mx-auto flex min-h-dvh w-full max-w-md flex-col justify-center px-4 py-10">
	<a href={resolve('/(public)')} class="mx-auto" aria-label={m.common_back()}>
		<Logo size={56} />
	</a>
	<h1 class="mt-6 text-center text-3xl font-bold">{m.signin_title()}</h1>
	<p class="mt-2 text-center text-lg text-ink-soft">{m.signin_lead()}</p>

	<div class="mt-8 space-y-5">
		{#if auth.status === 'unconfigured'}
			<Notice title={m.signin_unconfigured_title()}>{m.signin_unconfigured_body()}</Notice>
		{:else if step === 'sent'}
			<Notice tone="success" title={m.signin_email_sent_title()}>
				{m.signin_email_sent_body({ email: email.trim() })}
			</Notice>
		{:else}
			{#if failed}
				<Notice tone="error">{m.signin_error()}</Notice>
			{/if}

			<button
				type="button"
				class="btn btn-primary w-full"
				onclick={signInWithGoogle}
				disabled={googleBusy || step === 'sending'}
			>
				{m.signin_google()}
			</button>

			<div class="flex items-center gap-3 text-sm text-ink-soft" aria-hidden="true">
				<span class="h-px flex-1 bg-sand-300"></span>
				{m.signin_or()}
				<span class="h-px flex-1 bg-sand-300"></span>
			</div>

			<form onsubmit={sendLink} class="space-y-3">
				<div>
					<label for="email" class="label">{m.signin_email_label()}</label>
					<input
						id="email"
						name="email"
						type="email"
						class="field"
						autocomplete="email"
						inputmode="email"
						required
						bind:value={email}
					/>
				</div>
				<button type="submit" class="btn btn-secondary w-full" disabled={step === 'sending'}>
					{step === 'sending' ? m.signin_email_sending() : m.signin_email_submit()}
				</button>
			</form>
		{/if}
	</div>

	<p class="mt-8 text-center text-sm text-ink-soft">
		{m.signin_privacy_note()}
		<a href={resolve('/(public)/privasi')} class="underline underline-offset-4">
			{m.footer_privacy()}</a
		>.
	</p>
</main>
