<script lang="ts">
	import { resolve } from '$app/paths';
	import { APP_FULL_NAME, APP_NAME } from '#lib/config.js';
	import { m } from '#lib/paraglide/messages.js';
	import Logo from '#lib/ui/Logo.svelte';
	import type { LayoutProps } from './$types';

	let { children }: LayoutProps = $props();
</script>

<div class="flex min-h-dvh flex-col">
	<header class="mx-auto flex w-full max-w-5xl items-center justify-between px-4 py-4">
		<a href={resolve('/(public)')} class="flex items-center gap-3">
			<Logo size={40} />
			<span class="leading-tight">
				<span class="block text-lg font-bold">{APP_NAME}</span>
				<span class="hidden text-sm text-ink-soft sm:block">{APP_FULL_NAME}</span>
			</span>
		</a>
		<a href={resolve('/(app)/masuk')} class="btn btn-secondary">{m.landing_sign_in()}</a>
	</header>

	<main class="flex-1">
		{@render children()}
	</main>

	<footer class="border-t border-sand-200">
		<div
			class="mx-auto flex w-full max-w-5xl flex-wrap items-center justify-between gap-3 px-4 py-6 text-sm text-ink-soft"
		>
			<span>© {APP_FULL_NAME}</span>
			<a href={resolve('/(public)/privasi')} class="underline underline-offset-4">
				{m.footer_privacy()}
			</a>
		</div>
	</footer>
</div>
