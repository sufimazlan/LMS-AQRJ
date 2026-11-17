# AQRJ LMS

Learning app for **Akademi Quran Raudhatul Jannah**: Kelas Mengaji Al-Quran with short
video lessons, quizzes and recitation review by a teacher. It installs on a phone as a PWA.

**Status: pilot.** Working now: home page (ustazah, syllabus, plans), sign-in with
Google or an email link, learner profiles for a family, levels and lessons with video,
quizzes and progress, and an offline page. Admin screens, payments and tasmik come next
(see [docs/ROADMAP.md](docs/ROADMAP.md)).

## Run it

Needs Node 22.17 or newer.

```sh
npm install
cp .env.example .env    # fill in the two Supabase values, see docs/setup.md
npm run dev             # http://localhost:5173
```

Without the Supabase values the app still runs; the sign-in page says it is not connected.

| Command                           | What it does                               |
| --------------------------------- | ------------------------------------------ |
| `npm run dev`                     | Development server                         |
| `npm run check`                   | Type checks (app and service worker)       |
| `npm run lint` / `npm run format` | Prettier and ESLint                        |
| `npm test`                        | Unit tests                                 |
| `npm run build`                   | Production build for Cloudflare Workers    |
| `npm run check:bundle`            | Fails if pages get heavier than the budget |
| `npm run preview`                 | Run the built Worker locally on port 4173  |
| `npx supabase test db`            | Database access-rule tests (needs Docker)  |

## Where things are

| Path                                   | What                                                             |
| -------------------------------------- | ---------------------------------------------------------------- |
| `src/lib/content/site.ts`              | **Home page words:** ustazah profile, syllabus, plans and prices |
| `messages/ms.json`, `messages/en.json` | App text in Bahasa Melayu and English                            |
| `src/routes/(public)`                  | Home, privacy, offline. Plain HTML, no JavaScript                |
| `src/routes/(app)`                     | Everything behind sign-in. Runs in the browser only              |
| `src/routes/api`                       | Server-only code (secrets, webhooks)                             |
| `src/service-worker`                   | Offline support                                                  |
| `supabase/migrations`                  | Database tables and access rules                                 |
| `docs/`                                | Setup guide, roadmap, plan, decision records                     |

## Before going public

- Confirm or replace the draft syllabus (marked DRAF) in `src/lib/content/site.ts`.
- Have the privacy notice reviewed, then bump `PRIVACY_NOTICE_VERSION` in `src/lib/config.ts`.
- Allow search engines: edit `static/robots.txt` and remove `noindex` from `src/app.html`.

This repository is public. Never commit secrets, learner data or recordings.
