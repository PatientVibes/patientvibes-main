# patientvibes-main: Missouri school districts map

See README.md for what the site is and how the data flows.

## Deploy
- Cloudflare Pages project `patientvibes-main`, git-connected; pushes to `main` auto-deploy. Build `npm run build` → `dist` (just copies `site/`). No npm dependencies.
- Domains: `patientvibes.io` (apex CNAME → `patientvibes-main.pages.dev`) and `schools.patientvibes.io`. Other subdomains in the zone (agents, plaza, nextcloud, paperless, stirling, pokemon, property) belong to other projects. Don't touch them.
- Cloudflare tokens are in 1Password: `Cloudflare - All API Token` (field `credential`) for admin and DNS; account ID is in `cloudflare - patientvibes - pages` (custom field `Account ID`).

## Rules
- Don't point the page at `gis.mo.gov` live. It has no CORS headers. Always ship a snapshot via `tools/refresh_data.py`.
- Keep `site/data/*` small enough for phones (currently ~1.5 MB each, gzipped by Cloudflare).
- Previous Astro portfolio: see git history before the "schools map" commit.
