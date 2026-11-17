# Setup: from this repository to a live site

You do these steps in your own accounts. Nobody else needs your passwords.

## 1. Supabase (database and sign-in)

1. Create a project at supabase.com. Region: **Southeast Asia (Singapore)**.
2. SQL Editor: paste and run each file in `supabase/migrations/`, oldest first.
   (Or with the CLI: `npx supabase link` then `npx supabase db push`.)
   Then run `supabase/seed.sql` once to load the draft syllabus.
3. Project Settings, API Keys: copy the **Project URL** and the **publishable key**.
   The publishable key is safe in the browser. Never use the secret key in this app's browser code.
4. Authentication, URL Configuration:
   - Site URL: your site address, for example `https://aqrj.example`
   - Redirect URLs: `https://<your-site>/masuk/selesai` and `http://localhost:5173/masuk/selesai`
5. Authentication, Providers, Google: follow Supabase's guide. In Google Cloud, the
   redirect URI is `https://<project-ref>.supabase.co/auth/v1/callback`.

## 2. Cloudflare (hosting)

1. Workers & Pages, Create, import this GitHub repository.
2. Build command `npm run build`, deploy command `npx wrangler deploy`.
3. Build variables: `PUBLIC_SUPABASE_URL` and `PUBLIC_SUPABASE_PUBLISHABLE_KEY`.
   They are read at build time, so redeploy after changing them.
4. Check `https://<worker-address>/api/health` returns `{"ok":true,...}`.

## 3. Your domain

1. Buy the domain anywhere. Add it to Cloudflare (free plan) and change the
   nameservers at the registrar to the two Cloudflare gives you.
2. In the Worker: Settings, Domains & Routes, add the custom domain.
3. Update the Supabase Site URL and Redirect URLs to the new address.

## 4. Local development

Copy `.env.example` to `.env`, fill in the two values, run `npm run dev`.

## Replacing the logo or the ustazah photo

- Logo: `static/icons/logo.webp` (192 px, clear background) is shown in the page header.
  The app icons beside it are the same emblem on white: `icon-192.png`, `icon-512.png`,
  `icon-maskable-512.png` (emblem inside the middle 60%) and `apple-touch-icon.png` (180 px).
- Ustazah photo: `static/images/ustazah.webp`, square, about 450 px. Her name and
  details are in `src/lib/content/site.ts`.
- Home page video: see `scripts/hero-video/README.md`.

## Adding lessons and videos

Until the admin screens are built, content is edited in the Supabase Table Editor.

- **A video:** upload it to YouTube as Unlisted. Copy the 11-character ID from its
  address (`youtu.be/<ID>`). In `lesson_media`, insert a row: the lesson's `id`,
  provider `youtube`, and the ID as `ref`.
- **A lesson or level:** add a row in `lessons` or `levels` and tick `published`.
  `plan` on a level decides who may open it: `percuma`, `asas` or `penuh`.
- **A quiz:** add rows in `quiz_questions`. `options` is a list such as
  `["Alif", "Ba", "Ta"]` and `correct_index` counts from 0. A lesson with a quiz
  is completed by scoring 80% or more.

The home page syllabus is separate: it comes from `src/lib/content/site.ts`.

## Making yourself an admin

Sign in to the app once. Then in the SQL Editor run, with your own e-mail address:

```sql
insert into public.user_roles (account_id, role)
select id, 'admin' from auth.users where email = 'you@example.com';
```
