import { describe, expect, it, vi } from 'vitest';

// The module under test imports the Supabase client, which needs browser env values.
vi.mock('#lib/supabase/client.js', () => ({ getSupabase: vi.fn() }));

const { failureFromCode } = await import('./api.js');

describe('failureFromCode', () => {
	it('maps the unique-violation raised for a second self profile', () => {
		expect(failureFromCode('23505')).toBe('self_exists');
	});

	it('maps the learner limit', () => {
		expect(failureFromCode('54000')).toBe('limit_reached');
	});

	it.each(['22023', '23514'])('maps rule violation %s to a rejection', (code) => {
		expect(failureFromCode(code)).toBe('rejected');
	});

	it.each(['42501', 'PGRST301', undefined])('treats %s as unknown', (code) => {
		expect(failureFromCode(code)).toBe('unknown');
	});
});
