# Missouri school districts & city limits

**Live:** [schools.patientvibes.io](https://schools.patientvibes.io) (also served at [patientvibes.io](https://patientvibes.io))

A phone-friendly map that answers **"which school districts serve this city, and how many residents live in each part?"** for all 947 incorporated cities in Missouri. It overlays Missouri DESE school district boundaries on U.S. Census city limits and adds 2020 Census residents for every city × district overlap.

It was built for a Kansas City parents' group after the state's district viewer turned out to have no city-limits layer.

## What people can do

- **Search a city** (or open a share link like `/?city=Lee's Summit`) to see every overlapping district, with:
  - residents in that part of the city, and that share of the city's residents (2020 Census)
  - share of the city's land, with acres or square miles for small pieces
  - a residents bar and a land bar, sortable by either
  - the district's website
- **Focus mode:** while a city is selected, other city outlines are hidden and non-overlapping districts are faded. *Show all cities* or *Reset* restores the full map.
- **Linked highlighting:** hover a row (computer) to highlight its district; tap a row to select it and zoom; tap a district on the map to select its row.
- **Tap anywhere** for a card with the district's name, county, phone (tap to call), website, the city you're in, and how many of that city's residents live in that district.
- **District names** are labeled on the map from zoom 10. Neighboring districts never share a color.
- **Share:** *Copy link to this city* (uses the phone's share menu on mobile).

Example: Kansas City overlaps **15** districts. Kansas City 33 covers 21% of the city's land but holds 41% of its 508,090 residents.

## How it works

```
gis.mo.gov (DESE districts) ─┐
tigerweb (Census places) ────┼─► tools/refresh_data.py ─► site/data/*.json ─► scripts/build.mjs ─► dist/ ─► Cloudflare Pages
tigerweb (2020 blocks) ──────┘        (Python + shapely)        (committed)        (copy + version)
```

- **The data is a hosted snapshot, not a live query.** `gis.mo.gov` sends no CORS headers, so browsers on other sites can't read it. Everything the page needs is in `site/data/`.
- `tools/refresh_data.py` downloads all three sources and writes:

  | File | Contents | Size |
  |---|---|---|
  | `districts.geojson` | 515 districts, simplified (~3 m) for drawing; `C` = color index | ~1.5 MB |
  | `cities.geojson` | 947 incorporated places, simplified | ~1.5 MB |
  | `overlaps.json` | `{ cityGEOID: { pop, d: [[DIST_CODE, landShare, sqMi, residents], …] } }` | ~60 KB |
  | `meta.json` | download date + counts (shown on the page) | tiny |

- **Land overlap** uses the *full-detail* boundaries, not the simplified ones. Pieces under ~6 acres are dropped as boundary-alignment noise.
- **Residents:** each of ~169k populated 2020 Census blocks goes to the city and district containing its internal point. Blocks are built along these boundaries, so they rarely straddle them. The script **fails** unless the statewide total is exactly **6,154,913** (the official 2020 count), which catches a missing county.
- **Colors:** greedy graph coloring over district adjacency (currently 6 colors).
- `scripts/build.mjs` copies `site/` → `dist/` and appends `?v=<commit>` to the data URLs, so a new deploy never reads hour-old cached data (`site/_headers` caches `/data/*` for 1 h).

## Updating the data

Automatic: `.github/workflows/refresh-data.yml` runs quarterly (1st of Jan/Apr/Jul/Oct) and on demand from the **Actions** tab. It commits only when boundaries or counts change, and that commit triggers a deploy.

By hand:

```bash
pip install "shapely>=2"
python tools/refresh_data.py     # ~1–2 min; rewrites site/data/
git add site/data && git commit -m "data: refresh" && git push
```

## Local preview

```bash
npm run build          # site/ -> dist/ (no dependencies)
npx serve dist         # or: cd site && python -m http.server
```

## Data sources

| Layer | Source | Notes |
|---|---|---|
| School districts | Missouri DESE, `gis.mo.gov/arcgis/rest/services/DESE/Missouri_Public_Schools/MapServer/1` | DESE updates annually as needed |
| City limits | U.S. Census TIGERweb incorporated places, `…/TIGERweb/Places_CouSub_ConCity_SubMCD/MapServer/4`, `STATE='29'` | Can lag recent annexations |
| Residents | U.S. Census TIGERweb 2020 blocks, `…/TIGERweb/Tracts_Blocks/MapServer/12` (`POP100`) | 2020 counts, all ages, on today's district lines |
| Basemap | OpenStreetMap tiles | |

**Validation (2026-11-19):** Kansas City's 15 districts and land shares match the Census/NCES school district layer within 0.05 points and match Show Me KC Schools' published count of 15. City resident totals match official 2020 counts (KC 508,090; Lee's Summit 101,108; St. Louis 301,578).

## Caveats (also shown on the page)

- Overlap is not attendance zoning. Families should confirm an address with the district.
- Resident counts are 2020 and all ages, not current enrollment, so fast-growing areas are undercounted.
- City limits come from the Census Bureau, not each city's own GIS.
