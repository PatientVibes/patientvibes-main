"""Refresh the map data from the state (DESE) and Census (TIGERweb).

Writes to site/data/:
  districts.geojson  simplified school district boundaries (for drawing)
  cities.geojson     simplified incorporated city limits (for drawing)
  overlaps.json      city GEOID -> [[DIST_CODE, share], ...] computed from FULL-detail boundaries
  meta.json          download date + feature counts

Run from the repo root:  python tools/refresh_data.py   (needs shapely >= 2)
"""
import datetime, json, math, os, urllib.request
from shapely.geometry import shape, mapping
from shapely import set_precision, STRtree
from shapely.ops import transform

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
OUT = os.path.join(ROOT, 'site', 'data')
DIST_URL = 'https://gis.mo.gov/arcgis/rest/services/DESE/Missouri_Public_Schools/MapServer/1/query?where=1%3D1&outFields=*&outSR=4326&f=geojson'
CITY_URL = 'https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/Places_CouSub_ConCity_SubMCD/MapServer/4/query?where=STATE%3D%2729%27&outFields=*&outSR=4326&f=geojson'
MIN_SHARE = 0.005  # ignore boundary slivers under 0.5% of a city's area

def fetch(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'schools-map-refresh'})
    d = json.load(urllib.request.urlopen(req, timeout=180))
    if d.get('exceededTransferLimit'):
        raise SystemExit('server truncated results: ' + url)
    return d['features']

def slim(feats, keep, tol):
    out = []
    for f in feats:
        g = set_precision(shape(f['geometry']).buffer(0).simplify(tol, preserve_topology=True), 1e-5)
        if not g.is_empty:
            out.append({'type': 'Feature', 'properties': {k: f['properties'].get(k) for k in keep}, 'geometry': mapping(g)})
    return {'type': 'FeatureCollection', 'features': out}

def write(name, obj):
    with open(os.path.join(OUT, name), 'w', encoding='utf-8') as fh:
        json.dump(obj, fh, separators=(',', ':'))

def main():
    os.makedirs(OUT, exist_ok=True)
    dists, cities = fetch(DIST_URL), fetch(CITY_URL)

    # Overlaps from full-detail geometry. Shares are ratios inside one city, so a
    # cos(latitude) x-scale is plenty accurate for an equal-area-ish comparison.
    k = math.cos(math.radians(38.5))
    proj = lambda g: transform(lambda x, y, z=None: (x * k, y), g)
    dgeo = [proj(shape(f['geometry']).buffer(0)) for f in dists]
    tree = STRtree(dgeo)
    overlaps = {}
    for c in cities:
        cg = proj(shape(c['geometry']).buffer(0))
        if cg.area == 0:
            continue
        rows = []
        for i in tree.query(cg, predicate='intersects'):
            share = dgeo[i].intersection(cg).area / cg.area
            if share >= MIN_SHARE:
                rows.append([dists[i]['properties']['DIST_CODE'], round(share, 4)])
        overlaps[c['properties']['GEOID']] = sorted(rows, key=lambda r: -r[1])

    # Color index so no two neighboring districts share a color (greedy, most-neighbors first).
    nbrs = [set(j for j in tree.query(g, predicate='intersects') if j != i) for i, g in enumerate(dgeo)]
    color = {}
    for i in sorted(range(len(dgeo)), key=lambda i: -len(nbrs[i])):
        used = {color[j] for j in nbrs[i] if j in color}
        color[i] = next(c for c in range(99) if c not in used)
    for i, f in enumerate(dists):
        f['properties']['C'] = color[i]
    print('colors used:', max(color.values()) + 1)

    write('districts.geojson', slim(dists, ['DIST_NAME', 'DIST_CODE', 'COUNTY', 'URL', 'DPHONE_1', 'C'], 0.0003))
    write('cities.geojson', slim(cities, ['NAME', 'BASENAME', 'GEOID'], 0.0001))
    write('overlaps.json', overlaps)
    write('meta.json', {'updated': datetime.date.today().isoformat(), 'districts': len(dists), 'cities': len(cities)})
    print(f'districts={len(dists)} cities={len(cities)} overlaps={len(overlaps)}')

if __name__ == '__main__':
    main()
