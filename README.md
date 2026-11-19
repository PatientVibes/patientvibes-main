# Missouri school districts & city limits

Served at **[patientvibes.io](https://patientvibes.io)** and **[schools.patientvibes.io](https://schools.patientvibes.io)**.

A phone-friendly map that answers *"which school districts serve parts of this city?"* for every incorporated city in Missouri. It overlays DESE school district boundaries on Census city limits. Search or tap a city to see the overlapping districts and roughly what share of the city each one covers.

Share a direct answer with a link: `https://schools.patientvibes.io/?city=Lee's Summit`

## How it works

- `site/` is the whole site: one `index.html` (Leaflet + Turf from unpkg, OpenStreetMap tiles) plus `site/data/`.
- The data is a **snapshot hosted here**, because the state GIS server (`gis.mo.gov`) blocks cross-origin browser requests. The page can't query it live.
- `tools/refresh_data.py` downloads fresh boundaries, writes simplified copies for drawing, and precomputes `overlaps.json` (city → districts with area share) from the **full-detail** geometry.
- `.github/workflows/refresh-data.yml` reruns it quarterly and commits only when boundaries actually changed. You can also run it by hand from the Actions tab.

## Local dev

```bash
pip install "shapely>=2"
python tools/refresh_data.py   # refresh site/data/
npm run build                  # copies site/ -> dist/
npx serve dist                 # http://localhost:3000
```

## Data sources & caveats

- School districts: Missouri DESE, `gis.mo.gov/arcgis/rest/services/DESE/Missouri_Public_Schools/MapServer/1`
- City limits: U.S. Census Bureau TIGERweb incorporated places, `.../TIGERweb/Places_CouSub_ConCity_SubMCD/MapServer/4` (`STATE='29'`). This can lag recent annexations.
- Overlap is not attendance zoning. Families should confirm an address with the district.

The previous portfolio site (Astro) lives in git history before this change.
