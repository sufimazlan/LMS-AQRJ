<script lang="ts">
	import Download from '@lucide/svelte/icons/download';
	import { m } from '#lib/paraglide/messages.js';
	import { install } from '#lib/pwa/install.svelte.js';
</script>

<!-- Android gets a real install button. iPhone has no install prompt, so it gets instructions. -->
{#if !install.installed && (install.canPrompt || install.isIos)}
	<section class="card flex items-start gap-4" aria-labelledby="install-title">
		<span class="rounded-xl bg-brand-50 p-2.5 text-brand-800" aria-hidden="true">
			<Download size={24} />
		</span>
		<div class="min-w-0 flex-1">
			<h2 id="install-title" class="font-semibold">{m.home_install_title()}</h2>
			{#if install.canPrompt}
				<p class="mt-1 text-ink-soft">{m.home_install_body()}</p>
				<button type="button" class="btn btn-secondary mt-3" onclick={() => install.prompt()}>
					{m.home_install_button()}
				</button>
			{:else}
				<p class="mt-1 text-ink-soft">{m.home_install_ios()}</p>
			{/if}
		</div>
	</section>
{/if}
