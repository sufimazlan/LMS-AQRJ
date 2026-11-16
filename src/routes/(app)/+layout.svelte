<script lang="ts">
	import { auth } from '#lib/auth/session.svelte.js';
	import { install } from '#lib/pwa/install.svelte.js';
	import type { LayoutProps } from './$types';

	let { children }: LayoutProps = $props();

	// This layout only ever runs in the browser (ssr = false).
	auth.start();
	install.start();
</script>

{@render children()}
