import { describe, expect, it } from 'vitest';
import { birthYearOptions, validateLearner, type LearnerDraft } from './validate.js';

const YEAR = 2026;

function draft(overrides: Partial<LearnerDraft> = {}): LearnerDraft {
	return {
		displayName: 'Aisyah',
		isSelf: true,
		birthYear: 1990,
		gender: 'P',
		privacyAccepted: true,
		guardianConfirmed: false,
		...overrides
	};
}

describe('validateLearner', () => {
	it('accepts an adult registering themselves', () => {
		const result = validateLearner(draft(), YEAR);
		expect(result).toEqual({
			ok: true,
			values: {
				displayName: 'Aisyah',
				isSelf: true,
				birthYear: 1990,
				gender: 'P',
				guardianConfirmed: false
			}
		});
	});

	it('trims the name and collapses inner spaces', () => {
		const result = validateLearner(draft({ displayName: '  Nur   Aisyah ' }), YEAR);
		expect(result.ok && result.values.displayName).toBe('Nur Aisyah');
	});

	it('requires a name', () => {
		const result = validateLearner(draft({ displayName: '   ' }), YEAR);
		expect(result).toEqual({ ok: false, errors: { displayName: 'name_required' } });
	});

	it('rejects a name over 60 characters', () => {
		const result = validateLearner(draft({ displayName: 'a'.repeat(61) }), YEAR);
		expect(result).toEqual({ ok: false, errors: { displayName: 'name_too_long' } });
	});

	it('allows the birth year and gender to be left out', () => {
		const result = validateLearner(draft({ birthYear: null, gender: null }), YEAR);
		expect(result.ok).toBe(true);
	});

	it.each([1925, 2027, 1990.5])('rejects birth year %s', (birthYear) => {
		const result = validateLearner(draft({ birthYear }), YEAR);
		expect(result).toEqual({ ok: false, errors: { birthYear: 'birth_year_invalid' } });
	});

	it('sends a learner under 18 to a guardian instead of self-registration', () => {
		const result = validateLearner(draft({ birthYear: 2012 }), YEAR);
		expect(result).toEqual({ ok: false, errors: { birthYear: 'minor_needs_guardian' } });
	});

	it('treats someone turning 18 this year as under 18', () => {
		expect(validateLearner(draft({ birthYear: YEAR - 17 }), YEAR).ok).toBe(false);
		expect(validateLearner(draft({ birthYear: YEAR - 18 }), YEAR).ok).toBe(true);
	});

	it('requires guardian confirmation for a child profile', () => {
		const result = validateLearner(draft({ isSelf: false, birthYear: 2016 }), YEAR);
		expect(result).toEqual({ ok: false, errors: { guardianConfirmed: 'guardian_required' } });
	});

	it('accepts a child profile once the guardian confirms', () => {
		const result = validateLearner(
			draft({ isSelf: false, birthYear: 2016, guardianConfirmed: true }),
			YEAR
		);
		expect(result.ok && result.values.guardianConfirmed).toBe(true);
	});

	it('never records guardian confirmation on a self profile', () => {
		const result = validateLearner(draft({ guardianConfirmed: true }), YEAR);
		expect(result.ok && result.values.guardianConfirmed).toBe(false);
	});

	it('requires the privacy notice to be accepted', () => {
		const result = validateLearner(draft({ privacyAccepted: false }), YEAR);
		expect(result).toEqual({ ok: false, errors: { privacyAccepted: 'privacy_required' } });
	});

	it('reports every problem at once', () => {
		const result = validateLearner(
			draft({ displayName: '', isSelf: false, birthYear: 1800, privacyAccepted: false }),
			YEAR
		);
		expect(result).toEqual({
			ok: false,
			errors: {
				displayName: 'name_required',
				birthYear: 'birth_year_invalid',
				guardianConfirmed: 'guardian_required',
				privacyAccepted: 'privacy_required'
			}
		});
	});
});

describe('birthYearOptions', () => {
	it('lists the last 101 years, newest first', () => {
		const years = birthYearOptions(YEAR);
		expect(years).toHaveLength(101);
		expect(years[0]).toBe(2026);
		expect(years.at(-1)).toBe(1926);
	});
});
