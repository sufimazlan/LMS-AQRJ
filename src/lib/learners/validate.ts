import { ADULT_AGE } from '#lib/config.js';
import type { Gender } from '#lib/supabase/database.types.js';

/** What the "add learner" form holds while the person is typing. */
export type LearnerDraft = {
	displayName: string;
	isSelf: boolean;
	birthYear: number | null;
	gender: Gender | null;
	privacyAccepted: boolean;
	guardianConfirmed: boolean;
};

/** A draft that passed every rule and is ready to send. */
export type LearnerValues = {
	displayName: string;
	isSelf: boolean;
	birthYear: number | null;
	gender: Gender | null;
	guardianConfirmed: boolean;
};

export type LearnerErrorCode =
	| 'name_required'
	| 'name_too_long'
	| 'birth_year_invalid'
	| 'minor_needs_guardian'
	| 'guardian_required'
	| 'privacy_required';

export type LearnerErrors = Partial<
	Record<'displayName' | 'birthYear' | 'guardianConfirmed' | 'privacyAccepted', LearnerErrorCode>
>;

export type LearnerValidation =
	{ ok: true; values: LearnerValues } | { ok: false; errors: LearnerErrors };

export const MAX_NAME_LENGTH = 60;
export const OLDEST_AGE = 100;

/**
 * The same rules are enforced again by the `create_learner` database function.
 * This copy exists to give instant, friendly feedback in the form.
 */
export function validateLearner(draft: LearnerDraft, thisYear: number): LearnerValidation {
	const errors: LearnerErrors = {};
	const displayName = draft.displayName.trim().replace(/\s+/g, ' ');

	if (displayName.length === 0) errors.displayName = 'name_required';
	else if (displayName.length > MAX_NAME_LENGTH) errors.displayName = 'name_too_long';

	if (draft.birthYear !== null) {
		const valid =
			Number.isInteger(draft.birthYear) &&
			draft.birthYear >= thisYear - OLDEST_AGE &&
			draft.birthYear <= thisYear;

		if (!valid) errors.birthYear = 'birth_year_invalid';
		// Judged by year alone, so someone turning 18 this year still counts as under 18.
		else if (draft.isSelf && thisYear - draft.birthYear < ADULT_AGE) {
			errors.birthYear = 'minor_needs_guardian';
		}
	}

	if (!draft.isSelf && !draft.guardianConfirmed) errors.guardianConfirmed = 'guardian_required';
	if (!draft.privacyAccepted) errors.privacyAccepted = 'privacy_required';

	if (Object.keys(errors).length > 0) return { ok: false, errors };

	return {
		ok: true,
		values: {
			displayName,
			isSelf: draft.isSelf,
			birthYear: draft.birthYear,
			gender: draft.gender,
			guardianConfirmed: !draft.isSelf && draft.guardianConfirmed
		}
	};
}

/** Years offered in the birth-year picker, newest first. */
export function birthYearOptions(thisYear: number): number[] {
	return Array.from({ length: OLDEST_AGE + 1 }, (_, index) => thisYear - index);
}
