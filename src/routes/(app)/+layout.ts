// Everything behind sign-in is a client-side app. Each page is prerendered as an
// empty shell (static file, no Worker call) and renders in the browser. The same
// build can later be wrapped by Capacitor for Android and iOS.
//
// Rule: no +page.server.ts, +layout.server.ts or form actions under (app).
// Server-only work belongs in src/routes/api.
export const ssr = false;
export const prerender = true;
