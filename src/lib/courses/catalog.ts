import { planIncludes, type PlanId } from '#lib/content/site.js';

export type LessonSummary = {
	id: string;
	level_id: string;
	position: number;
	title: string;
	duration_seconds: number | null;
};

export type Level = {
	id: string;
	number: number;
	title: string;
	summary: string;
	plan: PlanId;
	lessons: LessonSummary[];
};

/** Puts each lesson under its level, both in teaching order. */
export function buildCatalog(levels: Omit<Level, 'lessons'>[], lessons: LessonSummary[]): Level[] {
	return [...levels]
		.sort((a, b) => a.number - b.number)
		.map((level) => ({
			...level,
			lessons: lessons
				.filter((lesson) => lesson.level_id === level.id)
				.sort((a, b) => a.position - b.position)
		}));
}

export function countDone(level: Level, completed: ReadonlySet<string>): number {
	return level.lessons.filter((lesson) => completed.has(lesson.id)).length;
}

export type LessonPlace = { level: Level; lesson: LessonSummary; next: LessonSummary | null };

/** Finds a lesson and the one after it. The next lesson may be in the next open level. */
export function findLesson(catalog: Level[], lessonId: string, owned: PlanId): LessonPlace | null {
	const open = catalog.filter((level) => planIncludes(owned, level.plan));

	for (const level of catalog) {
		const index = level.lessons.findIndex((lesson) => lesson.id === lessonId);
		if (index === -1) continue;

		const later = open.filter((other) => other.number > level.number);
		const next = level.lessons[index + 1] ?? later.find((l) => l.lessons.length > 0)?.lessons[0];
		return { level, lesson: level.lessons[index], next: next ?? null };
	}

	return null;
}

/** The first lesson, in order, that the learner may open and has not finished. */
export function nextLesson(
	catalog: Level[],
	completed: ReadonlySet<string>,
	owned: PlanId
): LessonSummary | null {
	for (const level of catalog) {
		if (!planIncludes(owned, level.plan)) continue;
		const lesson = level.lessons.find((candidate) => !completed.has(candidate.id));
		if (lesson) return lesson;
	}
	return null;
}

/** Accepts only a plain YouTube video ID, never a full address or markup. */
export function youtubeId(ref: string): string | null {
	return /^[A-Za-z0-9_-]{11}$/.test(ref) ? ref : null;
}
