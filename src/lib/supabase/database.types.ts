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
		};
		Enums: {
			user_role: UserRole;
		};
		CompositeTypes: { [_ in never]: never };
	};
};
