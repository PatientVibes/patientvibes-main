# patientvibes-main: Missouri school districts map

Static site at **schools.patientvibes.io** and **patientvibes.io**. Read README.md first for features, data flow and file formats.

## Layout

```
site/index.html            the whole app: Leaflet 1.9.4 + Turf 6.5.0 from unpkg, inline CSS/JS, no build step
site/data/                 committed data snapshot (generated; don't hand-edit)
site/_headers              Cloudflare cache rules (/data/* = 1 h)
tools/refresh_data.py      downloads DESE + Census, writes site/data/ (Python, shapely>=2)
scripts/build.mjs          site/ -> dist/, stamps data URLs with ?v=<commit>
.github/workflows/refresh-data.yml   quarterly + manual data refresh, commits only on change
```

## Deploy

- Cloudflare Pages project **`patientvibes-main`**, git-connected through the "Cloudflare Workers and Pages" GitHub App. Every push to `main` deploys (~1 min). Build `npm run build`, output `dist`. No npm dependencies.
- Custom domains on the project: `patientvibes.io` (apex CNAME → `patientvibes-main.pages.dev`) and `schools.patientvibes.io` (proxied CNAME → same, added 2026-11-19).
- The zone holds **only** the apex and `schools.` (both -> `patientvibes-main`). Everything else was removed on 2026-11-21: the homelab's Nextcloud/Paperless/Stirling moved to `chrispaulmoore.com`, and `agents.`, `plaza.`, `pokemon.` were deleted (their Pages projects still exist on `*.pages.dev`). Any new subdomain on this zone should belong to this site.
- Verify a deploy: `curl -s https://schools.patientvibes.io/ | grep -o "overlaps.json?v=[a-z0-9]*"` shows the new commit SHA prefix.

## Credentials (1Password, vault "Service Account", id `jkpi6kbttqrirancazuclw2tna`)

The `op` CLI runs as a service account, so pass `--vault`:

- `op item get 3vlhufs6givjkmkbtms4drjcpm --vault jkpi6kbttqrirancazuclw2tna --fields credential --reveal`: Cloudflare all-access API token (Pages domains, DNS)
- `op item get 3uqk7spvqx4wyfkktbvyn7ere4 --vault jkpi6kbttqrirancazuclw2tna --fields "Account ID" --reveal`: Cloudflare account ID

## Rules / gotchas

- **Never point the page at `gis.mo.gov` live.** It has no CORS headers. Always ship a snapshot via `tools/refresh_data.py`.
- **Changing a `site/data/*` format?** Update `site/index.html` in the same commit. `build.mjs` versions the URLs, so cached old data can't meet a new page. The build fails if it finds no `'data/…'` URLs, so keep them as quoted string literals.
- **Population sanity check:** `refresh_data.py` exits unless the Missouri block total = 6,154,913. Missouri county FIPS codes are odd 001–229 **plus 186 (Ste. Genevieve) and 510 (St. Louis city)**. Missing 186 once silently dropped ~18k people.
- **Overlap threshold** is an absolute area (`MIN_SQMI = 0.01`, ~6 acres), not a percentage. A 0.5% cutoff once hid 3 real districts from Kansas City (12 instead of 15).
- **Shares** use a cos(latitude) x-scale on lon/lat. That's fine for ratios inside one city; square miles are approximate (±~4%).
- **Colors:** `C` property from greedy coloring in `refresh_data.py`; the page palette must have at least as many entries as colors used (currently 6 of 8).
- Keep `site/data/*.geojson` phone-friendly (~1.5 MB each; Cloudflare gzips). Raise simplification tolerance before adding properties.
- Test at 390×844 (phone) and desktop. Both city search and `?city=` links should list districts with no console errors.

## History

- 2026-11-19: replaced the old Astro portfolio with this map (PRs #2–#7). The portfolio is backed up elsewhere and is not needed here.
- 2026-11-21: cleared every other subdomain out of the `patientvibes.io` zone (see Deploy).
