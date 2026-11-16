# Roadmap and feature list

Version 0.2, 16 November 2026. This page takes priority over `AQRJ-LMS-PLAN.md`
(version 0.1) wherever the two differ.

## What changed since the plan

| Topic         | Plan 0.1                       | Now                                                                                                                              |
| ------------- | ------------------------------ | -------------------------------------------------------------------------------------------------------------------------------- |
| Size          | 200 learners                   | 1,000 now, ready for 10,000                                                                                                      |
| Plans         | Free and one Premium pass      | **Percuma RM0**, **Asas RM29 a month** (first half of the syllabus), **Penuh RM49 a month** (all of it). Same price for all ages |
| Premium video | Unlisted YouTube for the pilot | Unchanged. Move to R2 before public launch, because an unlisted link can be shared                                               |
| Framework     | SvelteKit                      | SvelteKit 3 (see `adr/0001-stack.md`)                                                                                            |

"RM29 a month" is built as a 30-day pass bought by FPX. FPX cannot charge
automatically, so the app reminds the learner before the pass ends. Card
subscriptions that renew by themselves are under Advanced.

## Features

### Must have (launch)

| Feature                                                   | Milestone | State                                                     |
| --------------------------------------------------------- | --------- | --------------------------------------------------------- |
| Home page: ustazah, syllabus, plans                       | M0        | Done, with 3D classroom video (syllabus text still draft) |
| Sign-in with Google or email link                         | M0        | Done, needs your Supabase project                         |
| Family account with learner profiles, guardian consent    | M0        | Done                                                      |
| Installable app (PWA), offline page                       | M0        | Done                                                      |
| Levels and lessons from the database, video player        | M1        | Done                                                      |
| Progress per learner, continue where you stopped          | M1        | Done (per lesson, not per second of video)                |
| Quiz at the end of a lesson                               | M1        | Done                                                      |
| Admin: add levels, lessons, videos                        | M1        | Supabase Table Editor for now; screens are next           |
| Plan gates: Percuma, Asas, Penuh enforced in the database | M2        | Gate is live; everyone is on Percuma until payment exists |
| FPX payment, receipts, pass expiry and reminders          | M2        |                                                           |
| Tasmik: record, upload, ustazah review and feedback       | M3        |                                                           |
| Privacy notice reviewed, data export and delete           | M5        | Draft notice only                                         |

### Nice to have (soon after launch)

Live class schedule with meeting links · sijil (certificate) per level · Web Push and
email reminders · streak and badges · teacher dashboard with gender routing ·
sponsored seats (tajaan) · coupons and family discount · English interface on public pages.

### Advanced (when there is demand)

Android and iOS apps with Capacitor · offline lesson downloads · premium video on R2
with signed links · card subscriptions with automatic renewal · reports for parents ·
several teachers with workload balancing · AI help that marks likely tajwid slips for
the ustazah to confirm.

## Scale and cost

|                              | Up to about 1,000 learners                                                                                                                        | About 10,000 learners                                                               |
| ---------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------- |
| Hosting (Cloudflare Workers) | RM0. Pages and files are served free without a cap                                                                                                | RM0 to about RM21 a month (Workers Paid, US$5) if `/api` passes 100,000 calls a day |
| Database (Supabase)          | RM0 on Free for the pilot. **Move to Pro, about RM103 a month (US$25), before taking payments:** Free has no backups and pauses after 7 idle days | Pro. Add a larger compute size only if the dashboard shows strain                   |
| Video                        | RM0 (YouTube)                                                                                                                                     | RM0 on YouTube, or R2 at US$0.015 per GB a month after the free 10 GB               |
| Tasmik audio (R2)            | Inside the free 10 GB                                                                                                                             | A few ringgit a month. Recordings are deleted 90 days after review                  |
| Email                        | RM0 (3,000 a month free)                                                                                                                          | About RM82 a month (US$20) if reminders pass the free limit                         |
| Domain                       | About RM46 a year (.com) or RM120 a year (.my)                                                                                                    | Same                                                                                |
| FPX fee                      | About RM1 per payment                                                                                                                             | Same                                                                                |

What makes 10,000 possible without a rebuild: pages are static files; the browser talks
to the database directly, so the server does almost nothing; every list is paged and
indexed; access rules use `(select auth.uid())` so they are evaluated once per query;
video and audio never pass through the app server.

Checks to do on the way up: load-test the lesson and progress queries at 10,000 learners
(M1), turn on Supabase connection pooling for `/api` (M2), and watch database size
(progress rows grow fastest).
