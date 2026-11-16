# ADR 0001: Stack

Date: 2026-11-16. Status: accepted.

## Decision

- **SvelteKit 3** (Svelte 5, TypeScript) on **Cloudflare Workers** with static assets.
- **Supabase** (Postgres, Auth, row-level security) in Singapore as the only database.
- **Tailwind CSS 4**, **Paraglide** for Bahasa Melayu and English, **Vitest** for tests.

## Why

- Static files on Cloudflare are served free and without limit, so 1,000 or 10,000
  learners cost the same to serve. Only `/api` calls count against the Worker quota.
- Public pages are built to plain HTML with no JavaScript. Pages behind sign-in are
  a client-side app made of static shells, so the same build can go into Capacitor
  for Android and iOS later.
- Row-level security keeps the access rules in one place, next to the data.

## Rules that follow

- No `+page.server.ts`, `+layout.server.ts` or form actions under `src/routes/(app)`.
- Every table has row-level security on. Sensitive writes go through database functions.
- Secrets, payment webhooks and media tokens live only under `src/routes/api`.
- Imports use `#lib/...` with file extensions (SvelteKit 3 convention).

## Left for later

- Zod or Valibot (plain TypeScript validation is enough for now).
- A component library (hand-written components for now).
- Content-Security-Policy (Milestone 5).
- An SPA fallback page, needed once app routes have parameters (Milestone 1).
