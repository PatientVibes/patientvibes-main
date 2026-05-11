# TODO

Open work items on `patientvibes-main`. Grouped by visibility/priority. Last updated 2026-05-10 after the Sage Editorial redesign shipped.

Done work isn't tracked here — see `git log` and [archive/plans/](archive/plans/) for what's already complete.

---

## Plan items · deferred

- [ ] **Task 15 — Kindle Scribe pipeline output photo** in the sibling `patientvibes-agents-site` repo. Was the only explicit deferral at the end of the 2026-05-10 redesign session.
  - Add `public/images/kindle-scribe-pipeline-output.jpg` (the actual photo of a printed Kindle Scribe PDF page with annotations)
  - Reference it in `src/components/KindlePipelinePage.astro` (Project Page v2 component) so the kindle-pipeline detail page has a real photo instead of a `.pv-figure` placeholder
  - `public/images/` doesn't exist yet in that repo — has to be created
  - Spec details: [archive/plans/2026-05-10-redesign-and-cross-site-integration.md](archive/plans/2026-05-10-redesign-and-cross-site-integration.md) Task 15

## Polish · missing-but-expected

- [ ] **Social sharing metadata.** [src/layouts/BaseLayout.astro](src/layouts/BaseLayout.astro) emits `<title>`, `<meta name="description">`, canonical, favicons, font preloads, RSS link — but no `og:image`, `og:type`, `og:url`, `twitter:card`. Sharing the site on Slack/Twitter/LinkedIn renders a bare unfurl. Generate an OG image (likely via [@vercel/og](https://www.npmjs.com/package/@vercel/og) or Satori, rendering from the [archive/mockups-2026-05-10/OG Card.html](archive/mockups-2026-05-10/OG%20Card.html) mockup) and add the meta tags.
- [ ] **`<Terminal />` block is static.** [src/components/Terminal.astro](src/components/Terminal.astro) hardcodes a sample kindle-pipeline run. Could be driven by props once the harness publishes a "latest run summary" JSON somewhere consumable. Task 7 (extracting the component) called this out: *"If you later want to drive this from the most recent kindle-pipeline run, props can come in then."* — explicit future work.
- [ ] **"updated 2d ago" in the Now section header is hardcoded.** Could be `formatYearMonth(catalog.generatedAt)` from [src/lib/load-projects.ts](src/lib/load-projects.ts), or a real relative-time helper. Currently misleads visitors when the site's just been rebuilt.

## Designed but unbuilt

- [ ] **Dark mode.** Mockup at [archive/mockups-2026-05-10/Homepage Dark.html](archive/mockups-2026-05-10/Homepage%20Dark.html). The token system has `.pv-on-ink` inversion classes ready in [src/styles/tokens.css](src/styles/tokens.css), and the favicon already does `prefers-color-scheme: dark`, but there's no full-page dark mode toggle or media query. Smaller scope: add a `prefers-color-scheme: dark` media query in [src/styles/tokens.css](src/styles/tokens.css) that re-maps the `:root` tokens. Larger scope: add a UI toggle that persists to localStorage.

## Probably-not-features · noted for completeness

- [ ] **Hero tag aggregator is hardcoded** (9 tags with hand-typed counts) in [src/pages/index.astro](src/pages/index.astro). Reasonable to keep static. Wiring to real data needs project-level tags first, which the catalog at `agents.patientvibes.io/api/projects.json` doesn't currently expose.
- [ ] **Workshop entries are aspirational.** Both rows describe hardware projects (`esp32 door scanner`, `desk parts`) that don't have real artifacts to link to yet. Either:
  - Build them out (real work, lives off-site or in a new repo)
  - Keep as `status: 'draft'` / `status: 'build'` aspiration cards (current pattern) but remove the misleading `href="#"`

---

## Cross-site / infra · monitor

- **Remote feature branch lingering**: `origin/feat/sage-editorial-redesign` is still on GitHub after the 2026-05-10 merge to main. Drop it whenever with `git push origin --delete feat/sage-editorial-redesign`.
- **Fixture freshness**: [__fixtures__/projects.json](__fixtures__/projects.json) is the offline-build fallback. Currently dated 2026-05-11; refresh with `curl -fsS https://agents.patientvibes.io/api/projects.json > __fixtures__/projects.json` every few months or when projects materially change.
- **Cloudflare Workers and Pages GitHub App grant**: if a future push doesn't auto-deploy (check `deployment_trigger.type` on the latest CF Pages deploy — should be `github:push`, not `ad_hoc`), the App grant for the `PatientVibes` user may have been revoked. See `Lessons captured` in [CLAUDE.md](CLAUDE.md) for the fix.
