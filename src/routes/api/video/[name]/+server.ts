import { read } from '$app/server';
import av1 from '#lib/assets/kelas.av1.mp4';
import h264 from '#lib/assets/kelas.mp4';
import { rangeResponse } from '#lib/server/range.js';
import type { RequestHandler } from './$types';

// The home page video, in two encodings. Why it comes through the Worker and not
// as a plain file: Safari and every browser on iPhone play a video only when the
// server can send parts of the file on request (HTTP 206). Cloudflare's static
// file hosting sends the whole file every time, so this small endpoint does the
// slicing. Each view costs one to three Worker calls out of the free 100,000 a day.
export const prerender = false;

const files = new Map([
	['kelas', h264], // plays everywhere
	['kelas-av1', av1] // about half the size, for browsers that can play it
]);

const loaded = new Map<string, Promise<ArrayBuffer>>();

export const GET: RequestHandler = async ({ params, request }) => {
	const file = files.get(params.name);
	if (!file) return new Response('Not found', { status: 404 });

	// Read once, then keep it in memory for later requests (a few hundred kB).
	let bytes = loaded.get(file);
	if (!bytes) {
		bytes = read(file).arrayBuffer();
		loaded.set(file, bytes);
	}

	return rangeResponse(request, await bytes, {
		'content-type': 'video/mp4',
		'cache-control': 'public, max-age=86400'
	});
};
