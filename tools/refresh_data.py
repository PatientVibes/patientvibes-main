"""Refresh the map data: DESE school districts, Census city limits, 2020 Census residents.

Writes to site/data/:
  districts.geojson  simplified district boundaries for drawing; C = color index (neighbors never match)
  cities.geojson     simplified incorporated city limits for drawing
  overlaps.json      { cityGEOID: { "pop": residents, "d": [[DIST_CODE, land_share, sq_mi, residents], ...] } }
                     land from FULL-detail boundaries; residents from 2020 block counts by internal point
  meta.json          download date + feature counts

Fails loudly if any source is truncated or the statewide population != 6,154,913.
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
BLOCKS_URL = ('https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/Tracts_Blocks/MapServer/12/query'
              '?where=STATE%3D%2729%27+AND+COUNTY%3D%27{}%27&outFields=POP100,INTPTLAT,INTPTLON&returnGeometry=false&f=json')
MO_COUNTIES = [f'{n:03d}' for n in range(1, 230, 2)] + ['186', '510']  # odd FIPS + Ste. Genevieve (186) + St. Louis city (510)
MIN_SQMI = 0.01  # ~6 acres: ignore boundary-alignment slivers, keep real small pieces
SQMI_PER_DEG2 = 111.32 ** 2 / 2.58999  # after the cos(lat) x-scale below

def fetch(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'schools-map-refresh'})
    d = json.load(urllib.request.urlopen(req, timeout=180))
    if d.get('exceededTransferLimit'):
        raise SystemExit('server truncated results: ' + url)
    return d['features']

def fetch_blocks():
    """2020 Census block internal points + population, county by county (each under the 100k page limit)."""
    pts = []
    for c in MO_COUNTIES:
        req = urllib.request.Request(BLOCKS_URL.format(c), headers={'User-Agent': 'schools-map-refresh'})
        d = json.load(urllib.request.urlopen(req, timeout=180))
        if d.get('exceededTransferLimit'):
            raise SystemExit('blocks truncated for county ' + c)
        for f in d.get('features', []):
            a = f['attributes']
            if a['POP100']:
                pts.append((float(a['INTPTLON']), float(a['INTPTLAT']), a['POP100']))
    return pts

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
    blocks = fetch_blocks()
    mo = sum(b[2] for b in blocks)
    print('blocks with residents:', len(blocks), 'MO population:', mo)
    if mo != 6154913:  # official 2020 Missouri total; catches a missing county
        raise SystemExit(f'block population {mo} != 6,154,913 (2020 Census)')

    # Overlaps from full-detail geometry. Shares are ratios inside one city, so a
    # cos(latitude) x-scale is plenty accurate for an equal-area-ish comparison.
    k = math.cos(math.radians(38.5))
    proj = lambda g: transform(lambda x, y, z=None: (x * k, y), g)
    dgeo = [proj(shape(f['geometry']).buffer(0)) for f in dists]
    tree = STRtree(dgeo)
    # Residents: each populated block goes to the city and district containing its internal point.
    from shapely import points as mkpoints
    cgeo = [proj(shape(c['geometry']).buffer(0)) for c in cities]
    ctree = STRtree(cgeo)
    bpts = mkpoints([(x * k, y) for x, y, _ in blocks])
    res = {}  # (city idx, district idx) -> residents
    city_pop = [0] * len(cities)
    for bi, ci in zip(*ctree.query(bpts, predicate='within')):
        city_pop[ci] += blocks[bi][2]
        for di in tree.query(bpts[bi], predicate='within'):
            res[(ci, di)] = res.get((ci, di), 0) + blocks[bi][2]
            break

    overlaps = {}
    for ci, c in enumerate(cities):
        cg = cgeo[ci]
        if cg.area == 0:
            continue
        rows = []
        for i in tree.query(cg, predicate='intersects'):
            a = dgeo[i].intersection(cg).area
            if a * SQMI_PER_DEG2 >= MIN_SQMI:
                rows.append([dists[i]['properties']['DIST_CODE'], round(a / cg.area, 5), round(a * SQMI_PER_DEG2, 2), res.get((ci, i), 0)])
        overlaps[c['properties']['GEOID']] = {'pop': city_pop[ci], 'd': sorted(rows, key=lambda r: (-r[3], -r[1]))}

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
