# ADR 0002: Build the Supabase client from auth-js and postgrest-js

Date: 2026-11-16. Status: accepted.

## Decision

`src/lib/supabase/client.ts` builds the browser client from `@supabase/auth-js` and
`@supabase/postgrest-js` instead of calling `createClient` from `@supabase/supabase-js`.

## Why

`@supabase/supabase-js` always loads the Realtime, Storage and Edge Functions clients.
This app uses none of them in the browser (media goes to R2). Measured on this
codebase, minified and gzipped: 58.7 kB for the full client, 30.0 kB for the two parts.
First-load JavaScript on app pages went from about 103 kB to about 77 kB.

## What it costs

About 30 lines of glue that copy what `createClient` does: the project key and the
session token are added to every database request. If Supabase changes how keys are
sent, compare `withSession` with `fetchWithAuth` in supabase-js.

## Switching back

Needed if the browser ever uses Realtime or Supabase Storage. Install
`@supabase/supabase-js`, replace `createBrowserClient` with `createClient<Database>(url, key,
{ auth: { flowType: 'pkce' } })`, and raise the budget in `scripts/check-bundle.mjs`.
Calling code does not change, and people stay signed in (same storage key).
