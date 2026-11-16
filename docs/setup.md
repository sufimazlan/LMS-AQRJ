# Setup: from this repository to a live site

You do these steps in your own accounts. Nobody else needs your passwords.

## 1. Supabase (database and sign-in)

1. Create a project at supabase.com. Region: **Southeast Asia (Singapore)**.
2. SQL Editor: paste and run `supabase/migrations/20261116000000_foundations.sql`.
   (Or with the CLI: `npx supabase link` then `npx supabase db push`.)
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

## Replacing the icons

Export your logo to `static/icons/`: `icon.svg`, `icon-192.png`, `icon-512.png`,
`icon-maskable-512.png` (logo inside the middle 80%, no transparent corners) and
`apple-touch-icon.png` (180 px). Update `src/lib/ui/Logo.svelte` to match.
