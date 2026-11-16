# Notes for AI coding agents and new developers

Read `docs/adr/` first. Then keep to these rules.

1. **SvelteKit 3.** Config is in `vite.config.ts`. Import from `#lib/...` with file
   extensions (`.js` for TypeScript files, `.svelte`, `.svelte.js`). Use `resolve()` from
   `$app/paths` for links, `page` from `$app/state`, env values from `src/env.ts`.
   Do not use SvelteKit 2 patterns (`$lib`, `$app/stores`, `svelte.config.js`).
2. **Two areas.** `(public)` pages ship no JavaScript. `(app)` pages never use
   `+page.server.ts`, `+layout.server.ts` or form actions.
3. **Database.** Every new table gets row-level security and a test in `supabase/tests`.
   Grant the browser the least it needs. Money, quotas and consent go through
   `security definer` functions with `set search_path = ''`.
4. **Text.** App text goes in `messages/*.json` (both languages). Home page content
   goes in `src/lib/content/site.ts`.
5. **Weight.** Heavy modules (video player, recorder, PDF) are dynamic imports.
   Do not raise a budget in `scripts/check-bundle.mjs` without a decision record.
6. **Quran content.** Show references only. No Quran text and no scanned pages until
   AQRJ confirms the source and approval.
7. **Public repository.** No secrets, no real learner data, no recordings.
8. Before a pull request: `npm run check && npm run lint && npm test && npm run build && npm run check:bundle`.
