import { defineEnvVars } from '@sveltejs/kit/env';

/**
 * A missing value means "not connected yet". The app still builds and the
 * sign-in page explains what is missing, so CI and first-time setups work.
 */
function optionalUrl(value: string | undefined): string {
	const url = (value ?? '').trim().replace(/\/+$/, '');
	if (url === '') return '';
	if (!/^https:\/\/|^http:\/\/(localhost|127\.0\.0\.1)(:|$)/.test(url)) {
		throw new Error(
			'PUBLIC_SUPABASE_URL must start with https:// (or http://localhost for local Supabase)'
		);
	}
	return url;
}

function optionalText(value: string | undefined): string {
	return (value ?? '').trim();
}

// `static: true` compiles the value into the bundle. The learner app is served as
// static files, so there is no server at runtime to hand these values to the browser.
export const variables = defineEnvVars({
	PUBLIC_SUPABASE_URL: {
		public: true,
		static: true,
		description: 'Supabase project URL, for example https://abcdefghijkl.supabase.co',
		schema: optionalUrl
	},
	PUBLIC_SUPABASE_PUBLISHABLE_KEY: {
		public: true,
		static: true,
		description: 'Supabase publishable (anon) key. Safe in browsers; RLS protects the data.',
		schema: optionalText
	}
});
