<script lang="ts">
	import { asset, resolve } from '$app/paths';
	import Check from '@lucide/svelte/icons/check';
	import ChevronDown from '@lucide/svelte/icons/chevron-down';
	import Lock from '@lucide/svelte/icons/lock';
	import { PLANS, SYLLABUS, TEACHER, type PlanId } from '#lib/content/site.js';
	import { m } from '#lib/paraglide/messages.js';
	import Logo from '#lib/ui/Logo.svelte';

	const signIn = resolve('/(app)/masuk');

	// The classroom video at the top. See scripts/hero-video/README.md.
	const video = resolve('/api/video/kelas');
	const poster = asset('media/kelas.webp');
	const videoLabel = 'Ilustrasi 3D: seorang ustazah mengajar sepuluh pelajar di dalam kelas';

	const planName = (id: PlanId) => PLANS.find((plan) => plan.id === id)?.name ?? id;

	const steps = [
		{ title: 'Tonton', body: 'Pelajaran video pendek, 5 hingga 10 minit setiap satu.' },
		{ title: 'Rakam', body: 'Rakam bacaan anda terus dari telefon.' },
		{ title: 'Disemak', body: 'Ustazah mendengar dan memberi maklum balas tajwid.' }
	];
</script>

<svelte:head>
	<title>{m.landing_page_title()}</title>
	<meta name="description" content={m.landing_page_description()} />
	<!-- The still picture is the first big thing on the page, so fetch it early. -->
	<link rel="preload" as="image" href={poster} fetchpriority="high" />
</svelte:head>

<!-- Hero -->
<section class="mx-auto w-full max-w-5xl px-4 pt-2 pb-12">
	<!-- A short, silent, looping 3D illustration. It plays without JavaScript.
	     People who ask their device for less motion get the still picture. -->
	<div class="mb-8 aspect-video w-full overflow-hidden rounded-3xl bg-sand-100">
		<video
			class="size-full object-cover motion-reduce:hidden"
			autoplay
			muted
			loop
			playsinline
			disablepictureinpicture
			disableremoteplayback
			preload="metadata"
			{poster}
			width="960"
			height="540"
			aria-label={videoLabel}
		>
			<source src={video} type="video/mp4" />
		</video>
		<img
			class="hidden size-full object-cover motion-reduce:block"
			src={poster}
			alt={videoLabel}
			width="960"
			height="540"
		/>
	</div>
	<p
		class="inline-block rounded-full border border-sand-200 bg-sand-100 px-3 py-1 text-sm text-ink-soft"
	>
		{m.landing_pilot_note()}
	</p>
	<h1 class="mt-5 max-w-3xl text-4xl leading-tight font-bold sm:text-5xl">
		{m.landing_title()}
	</h1>
	<p class="mt-4 max-w-2xl text-lg text-ink-soft sm:text-xl">{m.landing_lead()}</p>
	<div class="mt-8 flex flex-wrap gap-3">
		<a href={signIn} class="btn btn-primary px-7 text-lg">{m.landing_cta()}</a>
		<a href="#silibus" class="btn btn-secondary px-7 text-lg">Lihat silibus</a>
	</div>
	<p class="mt-4 text-sm text-ink-soft">Untuk semua peringkat umur. Tahap 1 dan 2 percuma.</p>
</section>

<!-- Ustazah -->
<section class="bg-white py-12" aria-labelledby="ustazah-title">
	<div class="mx-auto grid w-full max-w-5xl items-center gap-8 px-4 sm:grid-cols-[auto_1fr]">
		{#if TEACHER.photo}
			<img
				src={TEACHER.photo}
				alt={TEACHER.name}
				width="224"
				height="224"
				loading="lazy"
				decoding="async"
				class="mx-auto size-56 rounded-3xl object-cover"
			/>
		{:else}
			<div
				class="mx-auto flex size-40 items-center justify-center rounded-3xl bg-brand-50 sm:size-56"
				aria-hidden="true"
			>
				<Logo size={88} />
			</div>
		{/if}
		<div>
			<p class="text-sm font-semibold tracking-wide text-brand-700 uppercase">Guru anda</p>
			<h2 id="ustazah-title" class="mt-1 text-3xl font-bold">{TEACHER.name}</h2>
			<p class="mt-1 text-ink-soft">{TEACHER.role}</p>
			<p class="mt-4 text-lg">{TEACHER.intro}</p>
			<ul class="mt-4 space-y-2">
				{#each TEACHER.points as point (point)}
					<li class="flex items-start gap-2">
						<Check size={20} class="mt-0.5 shrink-0 text-brand-700" aria-hidden="true" />
						<span>{point}</span>
					</li>
				{/each}
			</ul>
		</div>
	</div>
</section>

<!-- Cara belajar -->
<section class="py-12" aria-labelledby="cara-title">
	<div class="mx-auto w-full max-w-5xl px-4">
		<h2 id="cara-title" class="text-2xl font-bold">Cara belajar</h2>
		<ol class="mt-6 grid gap-4 sm:grid-cols-3">
			{#each steps as step, index (step.title)}
				<li class="card">
					<span
						class="flex size-9 items-center justify-center rounded-full bg-brand-50 font-bold text-brand-800"
						aria-hidden="true"
					>
						{index + 1}
					</span>
					<h3 class="mt-3 text-lg font-semibold">{step.title}</h3>
					<p class="mt-1 text-ink-soft">{step.body}</p>
				</li>
			{/each}
		</ol>
	</div>
</section>

<!-- Silibus: built with <details>, so it opens and closes without JavaScript. -->
<section id="silibus" class="scroll-mt-4 bg-white py-12" aria-labelledby="silibus-title">
	<div class="mx-auto w-full max-w-3xl px-4">
		<h2 id="silibus-title" class="text-2xl font-bold">Silibus</h2>
		<p class="mt-2 text-lg text-ink-soft">
			{SYLLABUS.length} tahap, daripada kenal huruf hingga hafazan. Ketik satu tahap untuk melihat pelajarannya.
		</p>

		<ol class="mt-6 space-y-3">
			{#each SYLLABUS as level (level.number)}
				<li>
					<details class="group card p-0" open={level.number === 1}>
						<summary
							class="flex min-h-16 cursor-pointer list-none items-center gap-3 px-4 py-3 [&::-webkit-details-marker]:hidden"
						>
							<span
								class="flex size-10 shrink-0 items-center justify-center rounded-full bg-brand-700 font-bold text-white"
								aria-hidden="true"
							>
								{level.number}
							</span>
							<span class="min-w-0 flex-1">
								<span class="block text-lg font-semibold">
									<span class="sr-only">Tahap {level.number}:</span>
									{level.title}
								</span>
								<span class="block text-sm text-ink-soft">{level.summary}</span>
							</span>
							<span
								class={[
									'shrink-0 rounded-full px-3 py-1 text-sm font-medium',
									level.plan === 'percuma'
										? 'bg-brand-50 text-brand-800'
										: 'bg-sand-100 text-ink-soft'
								]}
							>
								{planName(level.plan)}
							</span>
							<ChevronDown
								size={20}
								class="shrink-0 text-ink-soft transition-transform group-open:rotate-180"
								aria-hidden="true"
							/>
						</summary>
						<ul class="space-y-2 border-t border-sand-200 px-4 py-4">
							{#each level.lessons as lesson (lesson)}
								<li class="flex items-center gap-3">
									{#if level.plan === 'percuma'}
										<Check size={18} class="shrink-0 text-brand-700" aria-hidden="true" />
									{:else}
										<Lock size={18} class="shrink-0 text-ink-soft" aria-hidden="true" />
									{/if}
									<span>{lesson}</span>
								</li>
							{/each}
						</ul>
					</details>
				</li>
			{/each}
		</ol>

		<div class="mt-8 text-center">
			<a href={signIn} class="btn btn-primary px-7 text-lg">Mula Tahap 1 percuma</a>
		</div>
	</div>
</section>

<!-- Pelan -->
<section id="pelan" class="scroll-mt-4 py-12" aria-labelledby="pelan-title">
	<div class="mx-auto w-full max-w-5xl px-4">
		<h2 id="pelan-title" class="text-2xl font-bold">Pilih pelan</h2>
		<p class="mt-2 text-lg text-ink-soft">
			Harga yang sama untuk semua peringkat umur. Mula percuma dan naik taraf bila bersedia.
		</p>

		<ul class="mt-6 grid gap-4 md:grid-cols-3">
			{#each PLANS as plan (plan.id)}
				<li
					class={['card flex flex-col', plan.highlight && 'border-brand-500 ring-1 ring-brand-500']}
				>
					{#if plan.highlight}
						<span
							class="mb-3 self-start rounded-full bg-brand-700 px-3 py-1 text-sm font-medium text-white"
						>
							Paling lengkap
						</span>
					{/if}
					<h3 class="text-xl font-bold">{plan.name}</h3>
					<p class="mt-2">
						<span class="text-4xl font-bold">RM{plan.priceRm}</span>
						{#if plan.priceRm > 0}
							<span class="text-ink-soft">sebulan</span>
						{/if}
					</p>
					<p class="mt-2 text-ink-soft">{plan.summary}</p>
					<ul class="mt-4 flex-1 space-y-2">
						{#each plan.features as feature (feature)}
							<li class="flex items-start gap-2">
								<Check size={20} class="mt-0.5 shrink-0 text-brand-700" aria-hidden="true" />
								<span>{feature}</span>
							</li>
						{/each}
					</ul>
					<a
						href={signIn}
						class={['btn mt-6 w-full', plan.highlight ? 'btn-primary' : 'btn-secondary']}
					>
						{plan.priceRm === 0 ? m.landing_cta() : `Mula dengan ${plan.name}`}
					</a>
				</li>
			{/each}
		</ul>
		<p class="mt-4 text-sm text-ink-soft">
			Semua orang bermula dengan pelan Percuma. Bayaran dalam talian (FPX) untuk pelan Asas dan
			Penuh akan dibuka tidak lama lagi. Tiada potongan automatik.
		</p>
	</div>
</section>
