<script lang="ts">
	import { goto } from '$app/navigation';
	import { resolve } from '$app/paths';
	import LogOut from '@lucide/svelte/icons/log-out';
	import { auth } from '#lib/auth/session.svelte.js';
	import { learners } from '#lib/learners/store.svelte.js';
	import { m } from '#lib/paraglide/messages.js';
	import { getLocale, locales, setLocale, type Locale } from '#lib/paraglide/runtime.js';

	const localeNames: Record<Locale, string> = {
		ms: 'Bahasa Melayu',
		en: 'English'
	};

	let signingOut = $state(false);

	function changeLocale(event: Event) {
		// Paraglide stores the choice in a cookie and reloads the page in the new language.
		void setLocale((event.currentTarget as HTMLSelectElement).value as Locale);
	}

	async function signOut() {
		signingOut = true;
		await auth.signOut();
		learners.reset();
		void goto(resolve('/(app)/masuk'), { replace: true });
	}
</script>

<svelte:head>
	<title>{m.profile_page_title()}</title>
</svelte:head>

<h1 class="text-2xl font-bold">{m.profile_title()}</h1>

<div class="mt-6 space-y-4">
	<section class="card" aria-labelledby="learner-title">
		<h2 id="learner-title" class="text-sm font-semibold text-ink-soft">{m.profile_learner()}</h2>
		<p class="mt-1 text-lg font-semibold">{learners.active?.display_name}</p>
		<a href={resolve('/(app)/(dilindungi)/pilih')} class="btn btn-secondary mt-4">
			{m.profile_switch()}
		</a>
	</section>

	<section class="card" aria-labelledby="account-title">
		<h2 id="account-title" class="text-sm font-semibold text-ink-soft">{m.profile_account()}</h2>
		<p class="mt-1 text-lg break-all">{auth.user?.email}</p>

		<label for="locale" class="label mt-5">{m.profile_language()}</label>
		<select id="locale" class="field" value={getLocale()} onchange={changeLocale}>
			{#each locales as locale (locale)}
				<option value={locale}>{localeNames[locale]}</option>
			{/each}
		</select>
	</section>

	<button type="button" class="btn btn-quiet" onclick={signOut} disabled={signingOut}>
		<LogOut size={20} aria-hidden="true" />
		{m.profile_sign_out()}
	</button>
</div>
