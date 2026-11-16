import { describe, expect, it } from 'vitest';
import { buildCatalog, countDone, findLesson, nextLesson, youtubeId } from './catalog.js';

const levels = [
	{ id: 'L2', number: 2, title: 'Dua', summary: '', plan: 'asas' as const },
	{ id: 'L1', number: 1, title: 'Satu', summary: '', plan: 'percuma' as const },
	{ id: 'L3', number: 3, title: 'Tiga', summary: '', plan: 'percuma' as const }
];
const lesson = (id: string, level_id: string, position: number) => ({
	id,
	level_id,
	position,
	title: id,
	duration_seconds: null
});
const lessons = [
	lesson('b', 'L1', 2),
	lesson('a', 'L1', 1),
	lesson('c', 'L2', 1),
	lesson('d', 'L3', 1)
];
const catalog = buildCatalog(levels, lessons);

describe('buildCatalog', () => {
	it('orders levels and lessons', () => {
		expect(catalog.map((level) => level.number)).toEqual([1, 2, 3]);
		expect(catalog[0].lessons.map((l) => l.id)).toEqual(['a', 'b']);
	});
});

describe('countDone', () => {
	it('counts finished lessons in a level', () => {
		expect(countDone(catalog[0], new Set(['a', 'c']))).toBe(1);
	});
});

describe('nextLesson', () => {
	it('starts at the first lesson', () => {
		expect(nextLesson(catalog, new Set(), 'percuma')?.id).toBe('a');
	});

	it('skips levels outside the plan', () => {
		expect(nextLesson(catalog, new Set(['a', 'b']), 'percuma')?.id).toBe('d');
		expect(nextLesson(catalog, new Set(['a', 'b']), 'asas')?.id).toBe('c');
	});

	it('returns nothing when all open lessons are done', () => {
		expect(nextLesson(catalog, new Set(['a', 'b', 'd']), 'percuma')).toBeNull();
	});
});

describe('findLesson', () => {
	it('gives the next lesson in the same level', () => {
		expect(findLesson(catalog, 'a', 'percuma')?.next?.id).toBe('b');
	});

	it('moves on to the next open level', () => {
		expect(findLesson(catalog, 'b', 'percuma')?.next?.id).toBe('d');
		expect(findLesson(catalog, 'b', 'penuh')?.next?.id).toBe('c');
	});

	it('has no next lesson at the end, and no result for an unknown lesson', () => {
		expect(findLesson(catalog, 'd', 'penuh')?.next).toBeNull();
		expect(findLesson(catalog, 'zzz', 'penuh')).toBeNull();
	});
});

describe('youtubeId', () => {
	it('accepts an 11-character video ID only', () => {
		expect(youtubeId('dQw4w9WgXcQ')).toBe('dQw4w9WgXcQ');
		expect(youtubeId('https://youtu.be/dQw4w9WgXcQ')).toBeNull();
		expect(youtubeId('"><script>')).toBeNull();
	});
});
