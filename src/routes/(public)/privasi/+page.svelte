<script lang="ts">
	import { PRIVACY_NOTICE_VERSION } from '#lib/config.js';
	import { m } from '#lib/paraglide/messages.js';
	import Notice from '#lib/ui/Notice.svelte';

	// A draft for AQRJ to review. When the text changes, bump PRIVACY_NOTICE_VERSION
	// in src/lib/config.ts so that new consent records point at the new version.
	const sections = [
		{ title: m.privacy_what_title, body: m.privacy_what_body },
		{ title: m.privacy_why_title, body: m.privacy_why_body },
		{ title: m.privacy_children_title, body: m.privacy_children_body },
		{ title: m.privacy_storage_title, body: m.privacy_storage_body },
		{ title: m.privacy_rights_title, body: m.privacy_rights_body }
	];
</script>

<svelte:head>
	<title>{m.privacy_page_title()}</title>
</svelte:head>

<article class="mx-auto w-full max-w-2xl px-4 py-10">
	<h1 class="text-3xl font-bold">{m.privacy_title()}</h1>
	<p class="mt-1 text-sm text-ink-soft">{m.privacy_version({ version: PRIVACY_NOTICE_VERSION })}</p>

	<div class="mt-5">
		<Notice>{m.privacy_draft()}</Notice>
	</div>

	<p class="mt-6">{m.privacy_intro()}</p>

	{#each sections as section, index (index)}
		<h2 class="mt-8 text-xl font-semibold">{section.title()}</h2>
		<p class="mt-2">{section.body()}</p>
	{/each}
</article>
