<script lang="ts">
	import type { Component } from 'svelte';

	// For a screen whose feature arrives in a later milestone, or a list with nothing in it yet.
	let { icon: Icon, text }: { icon: Component<{ size?: number }>; text: string } = $props();
</script>

<div class="card mt-6 flex flex-col items-center px-6 py-12 text-center">
	<span class="rounded-full bg-sand-100 p-4 text-ink-soft" aria-hidden="true">
		<Icon size={32} />
	</span>
	<p class="mt-4 max-w-sm text-ink-soft">{text}</p>
</div>
