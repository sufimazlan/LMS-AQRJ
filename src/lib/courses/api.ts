import { getSupabase } from '#lib/supabase/client.js';
import type { QuizResult } from '#lib/supabase/database.types.js';
import { buildCatalog, type Level } from './catalog.js';

export type { QuizResult };

export type Question = { id: string; position: number; prompt: string; options: string[] };

export type LessonDetail = {
	summary: string;
	/** Null when no video is uploaded yet, or the level is outside the learner's plan. */
	video: { provider: 'youtube'; ref: string } | null;
	questions: Question[];
};

/** All published levels with their lesson titles. Two small queries, joined here. */
export async function loadCatalog(): Promise<Level[]> {
	const supabase = getSupabase();
	const [levels, lessons] = await Promise.all([
		supabase.from('levels').select('id, number, title, summary, plan').order('number'),
		supabase
			.from('lessons')
			.select('id, level_id, position, title, duration_seconds')
			.order('position')
	]);

	if (levels.error) throw levels.error;
	if (lessons.error) throw lessons.error;
	return buildCatalog(levels.data, lessons.data);
}

/** IDs of the lessons this learner has finished. */
export async function loadCompleted(learnerId: string): Promise<Set<string>> {
	const { data, error } = await getSupabase()
		.from('lesson_progress')
		.select('lesson_id')
		.eq('learner_id', learnerId);

	if (error) throw error;
	return new Set(data.map((row) => row.lesson_id));
}

/** The parts of a lesson that the database gives only to those whose plan covers it. */
export async function loadLessonDetail(lessonId: string): Promise<LessonDetail> {
	const supabase = getSupabase();
	const [lesson, media, questions] = await Promise.all([
		supabase.from('lessons').select('summary').eq('id', lessonId).maybeSingle(),
		supabase.from('lesson_media').select('provider, ref').eq('lesson_id', lessonId).maybeSingle(),
		supabase
			.from('quiz_questions')
			.select('id, position, prompt, options')
			.eq('lesson_id', lessonId)
			.order('position')
	]);

	if (lesson.error) throw lesson.error;
	if (media.error) throw media.error;
	if (questions.error) throw questions.error;

	return {
		summary: lesson.data?.summary ?? '',
		video: media.data,
		questions: questions.data
	};
}

export async function completeLesson(learnerId: string, lessonId: string): Promise<void> {
	const { error } = await getSupabase().rpc('complete_lesson', {
		p_learner: learnerId,
		p_lesson: lessonId
	});
	if (error) throw error;
}

/** `answers` holds the chosen option number for each question, in question order. */
export async function submitQuiz(
	learnerId: string,
	lessonId: string,
	answers: number[]
): Promise<QuizResult> {
	const { data, error } = await getSupabase().rpc('submit_quiz', {
		p_learner: learnerId,
		p_lesson: lessonId,
		p_answers: answers
	});
	if (error) throw error;
	return data;
}
