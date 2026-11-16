import type { RequestHandler } from './$types';

// A dynamic route, so it proves the Worker itself is running after a deploy.
// Everything secret (payment webhooks, media tokens) will live beside it under /api.
export const prerender = false;

export const GET: RequestHandler = () =>
	Response.json(
		{ ok: true, service: 'aqrj-lms', time: new Date().toISOString() },
		{ headers: { 'cache-control': 'no-store' } }
	);
