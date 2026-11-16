<script lang="ts">
	import Play from '@lucide/svelte/icons/play';
	import { youtubeId } from '#lib/courses/catalog.js';
	import { m } from '#lib/paraglide/messages.js';

	// Shows only a picture until the learner taps play. The YouTube player
	// (about 1 MB) is not downloaded before that, which keeps the page fast.
	let { videoRef, title }: { videoRef: string; title: string } = $props();

	const id = $derived(youtubeId(videoRef));
	let playing = $state(false);

	$effect(() => {
		// A different lesson: go back to the picture.
		void id;
		playing = false;
	});
</script>

<div class="aspect-video w-full overflow-hidden rounded-2xl bg-black">
	{#if id === null}
		<p class="flex h-full items-center justify-center px-6 text-center text-white">
			{m.lesson_video_soon()}
		</p>
	{:else if playing}
		<iframe
			class="size-full"
			src="https://www.youtube-nocookie.com/embed/{id}?autoplay=1&playsinline=1&rel=0"
			{title}
			allow="autoplay; encrypted-media; picture-in-picture; fullscreen"
			referrerpolicy="strict-origin-when-cross-origin"
			allowfullscreen
		></iframe>
	{:else}
		<button
			type="button"
			class="group relative block size-full"
			aria-label={m.lesson_play({ title })}
			onclick={() => (playing = true)}
		>
			<img
				src="https://i.ytimg.com/vi/{id}/hqdefault.jpg"
				alt=""
				loading="lazy"
				decoding="async"
				class="size-full object-cover opacity-90"
			/>
			<span
				class="absolute top-1/2 left-1/2 flex size-16 -translate-1/2 items-center justify-center rounded-full bg-brand-700 text-white shadow-lg transition-transform group-hover:scale-110"
			>
				<Play size={28} aria-hidden="true" />
			</span>
		</button>
	{/if}
</div>
