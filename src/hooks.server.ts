import type { Handle } from '@sveltejs/kit/hooks';
import { getTextDirection } from '#lib/paraglide/runtime.js';
import { paraglideMiddleware } from '#lib/paraglide/server.js';

// Keep in sync with the `_headers` file, which covers static assets and prerendered pages.
const SECURITY_HEADERS: Record<string, string> = {
	'X-Content-Type-Options': 'nosniff',
	'X-Frame-Options': 'DENY',
	'Referrer-Policy': 'strict-origin-when-cross-origin',
	'Permissions-Policy': 'camera=(), geolocation=(), microphone=(self)'
};

export const handle: Handle = ({ event, resolve }) =>
	paraglideMiddleware(event.request, async ({ request, locale }) => {
		const response = await resolve(
			{ ...event, request },
			{
				transformPageChunk: ({ html }) =>
					html
						.replace('%paraglide.lang%', locale)
						.replace('%paraglide.dir%', getTextDirection(locale))
			}
		);

		for (const [name, value] of Object.entries(SECURITY_HEADERS)) {
			if (!response.headers.has(name)) response.headers.set(name, value);
		}

		return response;
	});
