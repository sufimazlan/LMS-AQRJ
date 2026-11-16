/**
 * Database types for the tables in supabase/migrations.
 *
 * Written by hand for Milestone 0 because no Supabase project existed yet.
 * Once a project is linked, replace this file with the generated output:
 *
 *   npx supabase gen types typescript --linked > src/lib/supabase/database.types.ts
 */

export type UserRole = 'admin' | 'guru';
export type Gender = 'L' | 'P';
export type PlanId = 'percuma' | 'asas' | 'penuh';
export type ConsentKind = 'privacy_notice' | 'guardian_consent' | 'recording';

type AccountRow = {
	id: string;
	full_name: string;
	phone: string | null;
	locale: 'ms' | 'en';
	created_at: string;
	updated_at: string;
};

type UserRoleRow = {
	account_id: string;
	role: UserRole;
	granted_at: string;
};

type LearnerRow = {
	id: string;
	account_id: string;
	display_name: string;
	birth_year: number | null;
	gender: Gender | null;
	is_self: boolean;
	created_at: string;
	archived_at: string | null;
};

type ConsentRow = {
	id: string;
	account_id: string;
	learner_id: string | null;
	kind: ConsentKind;
	version: string;
	accepted_at: string;
};

type LevelRow = {
	id: string;
	number: number;
	title: string;
	summary: string;
	plan: PlanId;
	published: boolean;
	created_at: string;
};

type LessonRow = {
	id: string;
	level_id: string;
	position: number;
	title: string;
	summary: string;
	duration_seconds: number | null;
	published: boolean;
	created_at: string;
};

type LessonMediaRow = { lesson_id: string; provider: 'youtube'; ref: string };

/** `correct_index` exists in the table but the browser may not read it. */
type QuizQuestionRow = {
	id: string;
	lesson_id: string;
	position: number;
	prompt: string;
	options: string[];
};

type LessonProgressRow = { learner_id: string; lesson_id: string; completed_at: string };

type QuizAttemptRow = {
	id: string;
	learner_id: string;
	lesson_id: string;
	score: number;
	total: number;
	passed: boolean;
	created_at: string;
};

export type QuizResult = { score: number; total: number; passed: boolean; correct: number[] };

type ReadOnly<Row> = { Row: Row; Insert: never; Update: never; Relationships: [] };

export type Database = {
	public: {
		Tables: {
			accounts: {
				Row: AccountRow;
				Insert: never;
				Update: Partial<Pick<AccountRow, 'full_name' | 'phone' | 'locale'>>;
				Relationships: [];
			};
			user_roles: {
				Row: UserRoleRow;
				Insert: never;
				Update: never;
				Relationships: [];
			};
			learners: {
				Row: LearnerRow;
				/** Learners are created through the `create_learner` function, never by direct insert. */
				Insert: never;
				Update: Partial<Pick<LearnerRow, 'display_name' | 'birth_year' | 'gender' | 'archived_at'>>;
				Relationships: [];
			};
			consents: {
				Row: ConsentRow;
				Insert: never;
				Update: never;
				Relationships: [];
			};
			levels: ReadOnly<LevelRow>;
			lessons: ReadOnly<LessonRow>;
			lesson_media: ReadOnly<LessonMediaRow>;
			quiz_questions: ReadOnly<QuizQuestionRow>;
			/** Written only by `complete_lesson` and `submit_quiz`. */
			lesson_progress: ReadOnly<LessonProgressRow>;
			quiz_attempts: ReadOnly<QuizAttemptRow>;
		};
		Views: { [_ in never]: never };
		Functions: {
			create_learner: {
				Args: {
					p_display_name: string;
					p_is_self: boolean;
					p_birth_year?: number | null;
					p_gender?: Gender | null;
					p_privacy_version: string;
					p_guardian_confirmed?: boolean;
				};
				Returns: LearnerRow;
			};
			complete_lesson: {
				Args: { p_learner: string; p_lesson: string };
				Returns: undefined;
			};
			submit_quiz: {
				Args: { p_learner: string; p_lesson: string; p_answers: number[] };
				Returns: QuizResult;
			};
		};
		Enums: {
			user_role: UserRole;
			plan_id: PlanId;
		};
		CompositeTypes: { [_ in never]: never };
	};
};
