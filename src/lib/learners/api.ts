import { PRIVACY_NOTICE_VERSION } from '#lib/config.js';
import { getSupabase } from '#lib/supabase/client.js';
import type { Database } from '#lib/supabase/database.types.js';
import type { LearnerValues } from './validate.js';

type LearnerRow = Database['public']['Tables']['learners']['Row'];

/** The learner fields the app shows. */
export type Learner = Pick<LearnerRow, 'id' | 'display_name' | 'birth_year' | 'gender' | 'is_self'>;

const LEARNER_COLUMNS = 'id, display_name, birth_year, gender, is_self';

export type CreateLearnerFailure = 'self_exists' | 'limit_reached' | 'rejected' | 'unknown';

export type CreateLearnerResult =
	{ ok: true; learner: Learner } | { ok: false; reason: CreateLearnerFailure };

/** Learners of the signed-in account. RLS returns nobody else's. */
export async function listLearners(): Promise<Learner[]> {
	const { data, error } = await getSupabase()
		.from('learners')
		.select(LEARNER_COLUMNS)
		.is('archived_at', null)
		.order('created_at', { ascending: true });

	if (error) throw error;
	return data;
}

/**
 * Creates the learner and its consent records in one database transaction,
 * through the `create_learner` function. The function re-checks every rule.
 */
export async function createLearner(values: LearnerValues): Promise<CreateLearnerResult> {
	const { data, error } = await getSupabase().rpc('create_learner', {
		p_display_name: values.displayName,
		p_is_self: values.isSelf,
		p_birth_year: values.birthYear,
		p_gender: values.gender,
		p_privacy_version: PRIVACY_NOTICE_VERSION,
		p_guardian_confirmed: values.guardianConfirmed
	});

	if (error) return { ok: false, reason: failureFromCode(error.code) };

	return {
		ok: true,
		learner: {
			id: data.id,
			display_name: data.display_name,
			birth_year: data.birth_year,
			gender: data.gender,
			is_self: data.is_self
		}
	};
}

/** Maps the Postgres error codes raised by `create_learner` to something the form can explain. */
export function failureFromCode(code: string | undefined): CreateLearnerFailure {
	switch (code) {
		case '23505':
			return 'self_exists';
		case '54000':
			return 'limit_reached';
		case '22023':
		case '23514':
			return 'rejected';
		default:
			return 'unknown';
	}
}
