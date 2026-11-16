/** App-wide constants. No secrets here: this file ships to the browser. */

export const APP_NAME = 'AQRJ';
export const APP_FULL_NAME = 'Akademi Quran Raudhatul Jannah';

/**
 * Version of the privacy notice a person agrees to. It is stored with every
 * consent record, so changing the notice means bumping this and asking again.
 */
export const PRIVACY_NOTICE_VERSION = 'v0-draf';

/** A learner profile for oneself must belong to an adult; younger learners need a guardian. */
export const ADULT_AGE = 18;

export const STORAGE_KEYS = {
	activeLearner: 'aqrj.activeLearner'
} as const;
