import { describe, expect, it } from 'vitest';
import { PLANS, PLAN_ORDER, SYLLABUS, planIncludes } from './site.js';

describe('plans', () => {
	it('lists every plan once, cheapest first', () => {
		expect(PLANS.map((plan) => plan.id)).toEqual([...PLAN_ORDER]);
		const prices = PLANS.map((plan) => plan.priceRm);
		expect(prices).toEqual([...prices].sort((a, b) => a - b));
	});

	it('lets a higher plan open everything a lower plan opens', () => {
		expect(planIncludes('penuh', 'asas')).toBe(true);
		expect(planIncludes('asas', 'percuma')).toBe(true);
		expect(planIncludes('asas', 'asas')).toBe(true);
		expect(planIncludes('percuma', 'asas')).toBe(false);
		expect(planIncludes('asas', 'penuh')).toBe(false);
	});
});

describe('syllabus', () => {
	it('numbers the levels 1, 2, 3 and so on', () => {
		expect(SYLLABUS.map((level) => level.number)).toEqual(SYLLABUS.map((_, index) => index + 1));
	});

	it('never asks for a cheaper plan at a later level', () => {
		const ranks = SYLLABUS.map((level) => PLAN_ORDER.indexOf(level.plan));
		expect(ranks).toEqual([...ranks].sort((a, b) => a - b));
	});

	it('gives the Asas plan half of the syllabus', () => {
		const open = SYLLABUS.filter((level) => planIncludes('asas', level.plan));
		expect(open.length).toBe(SYLLABUS.length / 2);
	});

	it('gives the free plan at least one level', () => {
		expect(SYLLABUS.some((level) => level.plan === 'percuma')).toBe(true);
	});
});
