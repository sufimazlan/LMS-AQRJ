/** First and last byte to send, both included. */
export type ByteRange = { start: number; end: number };

/**
 * Reads an HTTP `Range` header for a file of `size` bytes.
 *
 * Returns the range to send, `null` when the whole file should be sent
 * (no header, or a form this function does not handle), or `'unsatisfiable'`
 * when the range lies outside the file.
 */
export function parseRange(
	header: string | null,
	size: number
): ByteRange | null | 'unsatisfiable' {
	if (!header) return null;

	const match = /^bytes=(\d*)-(\d*)$/.exec(header.trim());
	if (!match || (match[1] === '' && match[2] === '')) return null;

	// "bytes=-500" asks for the last 500 bytes.
	if (match[1] === '') {
		const length = Number(match[2]);
		if (length === 0) return 'unsatisfiable';
		return { start: Math.max(size - length, 0), end: size - 1 };
	}

	const start = Number(match[1]);
	const end = match[2] === '' ? size - 1 : Math.min(Number(match[2]), size - 1);
	if (start >= size || start > end) return 'unsatisfiable';

	return { start, end };
}

/** Answers a request for a file held in memory, honouring a `Range` header. */
export function rangeResponse(
	request: Request,
	bytes: ArrayBuffer,
	headers: HeadersInit
): Response {
	const size = bytes.byteLength;
	const range = parseRange(request.headers.get('range'), size);
	const responseHeaders = new Headers(headers);
	responseHeaders.set('accept-ranges', 'bytes');

	if (range === 'unsatisfiable') {
		responseHeaders.set('content-range', `bytes */${size}`);
		return new Response(null, { status: 416, headers: responseHeaders });
	}

	if (range === null) {
		responseHeaders.set('content-length', String(size));
		return new Response(bytes, { status: 200, headers: responseHeaders });
	}

	const part = bytes.slice(range.start, range.end + 1);
	responseHeaders.set('content-range', `bytes ${range.start}-${range.end}/${size}`);
	responseHeaders.set('content-length', String(part.byteLength));
	return new Response(part, { status: 206, headers: responseHeaders });
}
