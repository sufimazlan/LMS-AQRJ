<script lang="ts">
	import { resolve } from '$app/paths';
	import { page } from '$app/state';
	import BookOpen from '@lucide/svelte/icons/book-open';
	import CalendarDays from '@lucide/svelte/icons/calendar-days';
	import House from '@lucide/svelte/icons/house';
	import Mic from '@lucide/svelte/icons/mic';
	import User from '@lucide/svelte/icons/user';
	import { m } from '#lib/paraglide/messages.js';

	const tabs = [
		{ href: resolve('/(app)/(dilindungi)/belajar'), label: m.nav_home, icon: House, exact: true },
		{
			href: resolve('/(app)/(dilindungi)/belajar/kursus'),
			label: m.nav_courses,
			icon: BookOpen,
			exact: false
		},
		{
			href: resolve('/(app)/(dilindungi)/belajar/tasmik'),
			label: m.nav_tasmik,
			icon: Mic,
			exact: false
		},
		{
			href: resolve('/(app)/(dilindungi)/belajar/jadual'),
			label: m.nav_schedule,
			icon: CalendarDays,
			exact: false
		},
		{
			href: resolve('/(app)/(dilindungi)/belajar/profil'),
			label: m.nav_profile,
			icon: User,
			exact: false
		}
	];

	function isActive(href: string, exact: boolean): boolean {
		const path = page.url.pathname.replace(/\/$/, '');
		return exact ? path === href : path === href || path.startsWith(`${href}/`);
	}
</script>

<!-- Bottom bar on phones, side rail from tablet width up. -->
<nav
	aria-label={m.nav_main_label()}
	class="fixed inset-x-0 bottom-0 z-10 border-t border-sand-200 bg-white/95 pb-[env(safe-area-inset-bottom)] backdrop-blur md:static md:min-h-dvh md:w-56 md:shrink-0 md:border-t-0 md:border-r md:pb-0"
>
	<ul class="grid grid-cols-5 md:flex md:flex-col md:gap-1 md:p-3">
		{#each tabs as tab (tab.href)}
			{@const active = isActive(tab.href, tab.exact)}
			<li>
				<a
					href={tab.href}
					aria-current={active ? 'page' : undefined}
					class={[
						'flex min-h-14 flex-col items-center justify-center gap-0.5 text-xs font-medium md:min-h-12 md:flex-row md:justify-start md:gap-3 md:rounded-xl md:px-3 md:text-base',
						active ? 'text-brand-800 md:bg-brand-50' : 'text-ink-soft hover:text-ink'
					]}
				>
					<tab.icon aria-hidden="true" size={24} strokeWidth={active ? 2.4 : 2} />
					<span>{tab.label()}</span>
				</a>
			</li>
		{/each}
	</ul>
</nav>
