// The service worker makes the app installable and keeps it opening when the
// network is slow or gone. It is deliberately small:
//
//   1. On install, copy this build's files and page shells into one cache.
//   2. Serve those build files from the cache (they never change).
//   3. For page loads, prefer the network so a new release shows up at once,
//      but fall back to the cached page when the network is slow or missing.
//
// It never touches: anything that is not a GET, other sites (Supabase, YouTube),
// or /api. Learner data is never stored here.
import { version } from '$app/env';
import { assets, immutable, prerendered } from '$app/manifest';
import { self } from '$app/service-worker';

const CACHE = `aqrj-${version}`;

/** How long a page load may wait for the network before the cached page is used. */
const NAVIGATION_TIMEOUT_MS = 3000;

/** `$app/manifest` paths are relative to where the app is served from. */
function toPathname(path: string): string {
	return new URL(path, self.registration.scope).pathname;
}

// Files with a content hash in their name, plus everything in /static.
// Video is left out: it is streamed when watched, and too big to copy up front.
const buildFiles = [...immutable, ...assets]
	.filter((file) => !/\.(mp4|webm)$/.test(file.path))
	.map((file) => toPathname(file.path));
const buildFileSet = new Set(buildFiles);

// Public pages and the empty shells of the app pages.
const pages = prerendered.map((page) => toPathname(page.path));
const offlinePage = toPathname('offline');

/**
 * A response that arrived through a redirect cannot be used to answer a page
 * load, so store a plain copy instead.
 */
function withoutRedirect(response: Response): Response {
	if (!response.redirected) return response;

	return new Response(response.body, {
		headers: response.headers,
		status: response.status,
		statusText: response.statusText
	});
}

async function precache(): Promise<void> {
	const cache = await caches.open(CACHE);

	// The app cannot run without these, so a failure here fails the install
	// and the browser tries again on the next visit.
	await cache.addAll(buildFiles);

	// One missing page should not stop the app from being installed.
	await Promise.all(
		pages.map(async (pathname) => {
			try {
				const response = await fetch(pathname, { cache: 'no-cache' });
				if (response.ok) await cache.put(pathname, withoutRedirect(response));
			} catch {
				// Offline or blocked: the page is simply not available offline yet.
			}
		})
	);
}

async function deleteOldCaches(): Promise<void> {
	const names = await caches.keys();
	await Promise.all(names.filter((name) => name !== CACHE).map((name) => caches.delete(name)));
}

async function fromCache(pathname: string): Promise<Response | undefined> {
	const cache = await caches.open(CACHE);
	return cache.match(pathname, { ignoreSearch: true });
}

async function buildFile(request: Request, pathname: string): Promise<Response> {
	return (await fromCache(pathname)) ?? fetch(request);
}

async function pageLoad(request: Request, pathname: string): Promise<Response> {
	const cached = await fromCache(pathname);

	try {
		// With a cached copy to fall back on, do not keep the person waiting on a weak signal.
		const signal = cached ? AbortSignal.timeout(NAVIGATION_TIMEOUT_MS) : undefined;
		return await fetch(request, { signal });
	} catch (error) {
		const fallback = cached ?? (await fromCache(offlinePage));
		if (fallback) return fallback;
		throw error;
	}
}

self.addEventListener('install', (event) => {
	event.waitUntil(precache());
});

self.addEventListener('activate', (event) => {
	event.waitUntil(deleteOldCaches());
});

self.addEventListener('fetch', (event) => {
	const { request } = event;
	if (request.method !== 'GET') return;

	const url = new URL(request.url);
	if (url.origin !== self.location.origin) return;
	if (url.pathname.startsWith(toPathname('api/'))) return;

	if (buildFileSet.has(url.pathname)) {
		event.respondWith(buildFile(request, url.pathname));
	} else if (request.mode === 'navigate') {
		event.respondWith(pageLoad(request, url.pathname));
	}
});
