import { describe, expect, it } from 'vitest';
import { parseRange, rangeResponse } from './range.js';

describe('parseRange', () => {
	it('sends the whole file when there is no usable header', () => {
		expect(parseRange(null, 100)).toBeNull();
		expect(parseRange('bytes=-', 100)).toBeNull();
		expect(parseRange('bytes=0-1,5-9', 100)).toBeNull();
		expect(parseRange('items=0-1', 100)).toBeNull();
	});

	it('reads the probe Safari sends first', () => {
		expect(parseRange('bytes=0-1', 100)).toEqual({ start: 0, end: 1 });
	});

	it('reads an open-ended range', () => {
		expect(parseRange('bytes=40-', 100)).toEqual({ start: 40, end: 99 });
	});

	it('reads a suffix range', () => {
		expect(parseRange('bytes=-10', 100)).toEqual({ start: 90, end: 99 });
		expect(parseRange('bytes=-500', 100)).toEqual({ start: 0, end: 99 });
	});

	it('trims a range that runs past the end', () => {
		expect(parseRange('bytes=90-500', 100)).toEqual({ start: 90, end: 99 });
	});

	it('refuses a range outside the file', () => {
		expect(parseRange('bytes=100-', 100)).toBe('unsatisfiable');
		expect(parseRange('bytes=50-40', 100)).toBe('unsatisfiable');
		expect(parseRange('bytes=-0', 100)).toBe('unsatisfiable');
	});
});

describe('rangeResponse', () => {
	const bytes = new Uint8Array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9]).buffer;
	const ask = (range?: string) =>
		rangeResponse(
			new Request('https://example.test/video', { headers: range ? { range } : {} }),
			bytes,
			{ 'content-type': 'video/mp4' }
		);

	it('answers a range with 206 and the right bytes', async () => {
		const response = ask('bytes=2-5');
		expect(response.status).toBe(206);
		expect(response.headers.get('content-range')).toBe('bytes 2-5/10');
		expect(response.headers.get('content-length')).toBe('4');
		expect([...new Uint8Array(await response.arrayBuffer())]).toEqual([2, 3, 4, 5]);
	});

	it('answers without a range with 200 and everything', async () => {
		const response = ask();
		expect(response.status).toBe(200);
		expect(response.headers.get('accept-ranges')).toBe('bytes');
		expect((await response.arrayBuffer()).byteLength).toBe(10);
	});

	it('answers an impossible range with 416', () => {
		const response = ask('bytes=20-');
		expect(response.status).toBe(416);
		expect(response.headers.get('content-range')).toBe('bytes */10');
	});
});
