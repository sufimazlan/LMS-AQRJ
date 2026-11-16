import type { Session, User } from '@supabase/auth-js';
import { getSupabase, isSupabaseConfigured } from '#lib/supabase/client.js';

export type AuthStatus = 'loading' | 'signed-in' | 'signed-out' | 'unconfigured';

/**
 * Reactive sign-in state for the app area. There is no server session: the
 * browser holds the Supabase session and RLS decides what it may read.
 */
class AuthState {
	status = $state<AuthStatus>('loading');
	session = $state<Session | null>(null);
	#started = false;

	get user(): User | null {
		return this.session?.user ?? null;
	}

	/** Begin listening for sign-in changes. Safe to call from more than one layout. */
	start(): void {
		if (this.#started) return;
		this.#started = true;

		if (!isSupabaseConfigured) {
			this.status = 'unconfigured';
			return;
		}

		const supabase = getSupabase();

		supabase.auth.onAuthStateChange((_event, session) => {
			this.#apply(session);
		});

		supabase.auth
			.getSession()
			.then(({ data }) => this.#apply(data.session))
			.catch(() => this.#apply(null));
	}

	async signOut(): Promise<void> {
		if (!isSupabaseConfigured) return;
		await getSupabase().auth.signOut();
		this.#apply(null);
	}

	#apply(session: Session | null): void {
		this.session = session;
		this.status = session ? 'signed-in' : 'signed-out';
	}
}

export const auth = new AuthState();
