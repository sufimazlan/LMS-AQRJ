import { AuthClient } from '@supabase/auth-js';
import { PostgrestClient } from '@supabase/postgrest-js';
import { PUBLIC_SUPABASE_PUBLISHABLE_KEY, PUBLIC_SUPABASE_URL } from '$app/env/public';
import type { Database } from './database.types.js';

// Why not `createClient` from @supabase/supabase-js? That package always loads
// the Realtime, Storage and Edge Functions clients too, which this app does not
// use (media goes to R2). Building the client from the same two official parts
// it is made of saves about 29 kB of gzipped JavaScript on every app page.
// Calling code looks the same: supabase.auth, supabase.from(), supabase.rpc().
// To switch back, see docs/adr/0002-supabase-client.md.

type Auth = InstanceType<typeof AuthClient>;

/** Sign-in plus database access. The shape matches the standard Supabase client for these parts. */
export type AppSupabaseClient = PostgrestClient<Database> & { auth: Auth };

/** False until both public env values are set at build time (see docs/setup.md). */
export const isSupabaseConfigured =
	PUBLIC_SUPABASE_URL !== '' && PUBLIC_SUPABASE_PUBLISHABLE_KEY !== '';

/**
 * Sends the project key with every database request, and the signed-in
 * person's token when there is one. Row-level security reads that token.
 */
function withSession(auth: Auth, key: string): typeof fetch {
	return async (input, init) => {
		// Also renews the token first when it is about to expire.
		const { data } = await auth.getSession();
		const headers = new Headers(init?.headers);

		if (!headers.has('apikey')) headers.set('apikey', key);
		if (!headers.has('Authorization')) {
			headers.set('Authorization', `Bearer ${data.session?.access_token ?? key}`);
		}

		return fetch(input, { ...init, headers });
	};
}

function createBrowserClient(url: string, key: string): AppSupabaseClient {
	const projectUrl = new URL(url);

	const auth = new AuthClient({
		url: new URL('auth/v1', projectUrl).href,
		headers: { apikey: key, Authorization: `Bearer ${key}` },
		// The same storage key the standard client uses, so switching clients keeps people signed in.
		storageKey: `sb-${projectUrl.hostname.split('.')[0]}-auth-token`,
		flowType: 'pkce',
		persistSession: true,
		autoRefreshToken: true,
		// Finishes Google and email-link sign-ins when the person lands on /masuk/selesai.
		detectSessionInUrl: true
	});

	const database = new PostgrestClient<Database>(new URL('rest/v1', projectUrl).href, {
		fetch: withSession(auth, key)
	});

	return Object.assign(database, { auth });
}

let client: AppSupabaseClient | undefined;

/**
 * The one browser client. Import this only from the app area: public pages
 * must not pull the Supabase code in.
 */
export function getSupabase(): AppSupabaseClient {
	if (!isSupabaseConfigured) {
		throw new Error('Supabase is not configured. See docs/setup.md.');
	}

	client ??= createBrowserClient(PUBLIC_SUPABASE_URL, PUBLIC_SUPABASE_PUBLISHABLE_KEY);
	return client;
}
