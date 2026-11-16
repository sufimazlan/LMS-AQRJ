import { read } from '$app/server';
import video from '#lib/assets/kelas.mp4';
import { rangeResponse } from '#lib/server/range.js';
import type { RequestHandler } from './$types';

// The home page video. Why it comes through the Worker and not as a plain file:
// Safari and every browser on iPhone play a video only when the server can send
// parts of the file on request (HTTP 206). Cloudflare's static file hosting sends
// the whole file every time, so this small endpoint does the slicing.
// Each view costs one to three Worker calls out of the free 100,000 a day.
export const prerender = false;

let bytes: Promise<ArrayBuffer> | undefined;

export const GET: RequestHandler = async ({ request }) => {
	// Read once, then keep it in memory for later requests (about 300 kB).
	bytes ??= read(video).arrayBuffer();

	return rangeResponse(request, await bytes, {
		'content-type': 'video/mp4',
		'cache-control': 'public, max-age=86400'
	});
};
