"""Deterministic topographic contour tile + MGA grid references for the Paddock composition.

- Periodic value noise on a wrapping lattice (so the tile repeats seamlessly), seeded from a
  string through FNV-1a → mulberry32 (the catalogue's LAW-10 dialect). Same seed, same hills, every build.
- Marching squares extracts isolines at a 10 m interval; every fifth line is an index contour.
- UTM/MGA zone 55 (GDA2020 ≈ WGS84) conversion for real-world grid references of Gippsland localities.
"""
import math, re

# ---------------------------------------------------------------- seeded PRNG (FNV-1a → mulberry32)
def fnv1a(s: str) -> int:
    h = 0x811c9dc5
    for b in s.encode():
        h ^= b; h = (h * 0x01000193) & 0xffffffff
    return h

def mulberry32(seed: int):
    a = seed & 0xffffffff
    def rnd():
        nonlocal a
        a = (a + 0x6D2B79F5) & 0xffffffff
        t = a
        t = ((t ^ (t >> 15)) * (t | 1)) & 0xffffffff
        t ^= (t + (((t ^ (t >> 7)) * (t | 61)) & 0xffffffff)) & 0xffffffff
        return ((t ^ (t >> 14)) & 0xffffffff) / 4294967296
    return rnd

# ---------------------------------------------------------------- periodic value noise
def lattice(n, rnd):
    return [[rnd() for _ in range(n)] for _ in range(n)]

def smooth(t): return t * t * (3 - 2 * t)

def value_noise(lat, x, y):
    n = len(lat)
    xi, yi = int(math.floor(x)) % n, int(math.floor(y)) % n
    xf, yf = x - math.floor(x), y - math.floor(y)
    sx, sy = smooth(xf), smooth(yf)
    a, b = lat[yi][xi], lat[yi][(xi + 1) % n]
    c, d = lat[(yi + 1) % n][xi], lat[(yi + 1) % n][(xi + 1) % n]
    return (a + (b - a) * sx) + ((c + (d - c) * sx) - (a + (b - a) * sx)) * sy

def heightfield(seed: str, cells: int, base_period: int = 5, octaves: int = 3):
    rnd = mulberry32(fnv1a(seed))
    lats = [lattice(base_period * (2 ** o), rnd) for o in range(octaves)]
    H = [[0.0] * (cells + 1) for _ in range(cells + 1)]
    amp_total = sum(0.5 ** o for o in range(octaves))
    for j in range(cells + 1):
        for i in range(cells + 1):
            u, v = i / cells, j / cells  # 0..1, periodic
            h = 0.0
            for o, lat in enumerate(lats):
                p = base_period * (2 ** o)
                h += value_noise(lat, u * p, v * p) * (0.5 ** o)
            H[j][i] = h / amp_total
    # ridged touch for creek-line sharpness (small), then normalise 0..1
    mn = min(min(r) for r in H); mx = max(max(r) for r in H)
    for j in range(cells + 1):
        for i in range(cells + 1):
            H[j][i] = (H[j][i] - mn) / (mx - mn)
    return H

# ---------------------------------------------------------------- marching squares → polylines
def isolines(H, level):
    """Return list of segments [(x0,y0,x1,y1)] in cell units for one level."""
    segs = []
    rows = len(H) - 1; cols = len(H[0]) - 1
    def interp(x0, y0, v0, x1, y1, v1):
        t = 0.5 if v1 == v0 else (level - v0) / (v1 - v0)
        return (x0 + (x1 - x0) * t, y0 + (y1 - y0) * t)
    for j in range(rows):
        for i in range(cols):
            tl, tr, br, bl = H[j][i], H[j][i + 1], H[j + 1][i + 1], H[j + 1][i]
            idx = (tl >= level) << 3 | (tr >= level) << 2 | (br >= level) << 1 | (bl >= level)
            if idx in (0, 15): continue
            top = interp(i, j, tl, i + 1, j, tr); right = interp(i + 1, j, tr, i + 1, j + 1, br)
            bottom = interp(i, j + 1, bl, i + 1, j + 1, br); left = interp(i, j, tl, i, j + 1, bl)
            table = {1: [(left, bottom)], 2: [(bottom, right)], 3: [(left, right)], 4: [(top, right)],
                     5: [(top, left), (bottom, right)], 6: [(top, bottom)], 7: [(top, left)], 8: [(top, left)],
                     9: [(top, bottom)], 10: [(top, right), (left, bottom)], 11: [(top, right)], 12: [(left, right)],
                     13: [(bottom, right)], 14: [(left, bottom)]}
            for a, b in table[idx]:
                segs.append((a[0], a[1], b[0], b[1]))
    return segs

def join_segments(segs, eps=1e-6):
    """Chain segments into polylines (greedy); keeps the SVG small."""
    from collections import defaultdict
    key = lambda p: (round(p[0], 4), round(p[1], 4))
    adj = defaultdict(list)
    for n, (x0, y0, x1, y1) in enumerate(segs):
        adj[key((x0, y0))].append(n); adj[key((x1, y1))].append(n)
    used = [False] * len(segs); lines = []
    for n in range(len(segs)):
        if used[n]: continue
        used[n] = True
        x0, y0, x1, y1 = segs[n]
        line = [(x0, y0), (x1, y1)]
        # extend forward
        for end in (1, 0):
            while True:
                p = line[-1] if end else line[0]
                nxt = None
                for m in adj[key(p)]:
                    if not used[m]: nxt = m; break
                if nxt is None: break
                used[nxt] = True
                a, b = (segs[nxt][0], segs[nxt][1]), (segs[nxt][2], segs[nxt][3])
                other = b if key(a) == key(p) else a
                if end: line.append(other)
                else: line.insert(0, other)
        lines.append(line)
    return lines

def contour_svg(seed="fitzferalhunters-paddock", size=1200, cells=96, interval=0.05, index_every=5,
                minor_width=0.6, index_width=1.15, color="#432a27", minor_alpha=0.075, index_alpha=0.12):
    """Seamless contour tile as an SVG string. interval 0.05 of the 0..1 range = 20 levels ≈ a 10 m contour
    interval over a 200 m relief, index contour every fifth line (50 m), the Vicmap 1:25 000 convention."""
    H = heightfield(seed, cells)
    scale = size / cells
    minor, index = [], []
    levels = [round(k * interval, 4) for k in range(1, int(1 / interval))]
    for k, lv in enumerate(levels, start=1):
        lines = join_segments(isolines(H, lv))
        d = ''
        for line in lines:
            if len(line) < 6: continue  # drop specks: closed loops smaller than a cell or two
            pts = [f"{x * scale:.0f} {y * scale:.0f}" for x, y in line]
            d += 'M' + 'L'.join(pts)
        (index if k % index_every == 0 else minor).append(d)
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 {size} {size}">'
           f'<g fill="none" stroke="{color}" stroke-linejoin="round" stroke-linecap="round">'
           f'<path stroke-width="{minor_width}" stroke-opacity="{minor_alpha}" d="{"".join(minor)}"/>'
           f'<path stroke-width="{index_width}" stroke-opacity="{index_alpha}" d="{"".join(index)}"/>'
           f'</g></svg>')
    return svg

def svg_data_uri(svg: str) -> str:
    s = svg.replace('"', "'")
    s = re.sub(r'\s+', ' ', s)
    for a, b in (('%', '%25'), ('#', '%23'), ('<', '%3C'), ('>', '%3E'), ('&', '%26')):
        s = s.replace(a, b)
    return 'data:image/svg+xml,' + s

# ---------------------------------------------------------------- MGA zone 55 (GDA2020 / GRS80)
def latlon_to_mga55(lat, lon):
    """Transverse Mercator (Krüger series, mm-level) for GRS80, zone 55 (central meridian 147°E)."""
    a = 6378137.0; f = 1 / 298.257222101
    k0 = 0.9996; E0 = 500000.0; N0 = 10000000.0; lon0 = math.radians(147.0)
    n = f / (2 - f)
    A = a / (1 + n) * (1 + n ** 2 / 4 + n ** 4 / 64)
    alpha = [n / 2 - 2 * n ** 2 / 3 + 5 * n ** 3 / 16, 13 * n ** 2 / 48 - 3 * n ** 3 / 5, 61 * n ** 3 / 240]
    phi = math.radians(lat); lam = math.radians(lon) - lon0
    t = math.sinh(math.atanh(math.sin(phi)) - 2 * math.sqrt(n) / (1 + n) * math.atanh(2 * math.sqrt(n) / (1 + n) * math.sin(phi)))
    xi = math.atan2(t, math.cos(lam)); eta = math.atanh(math.sin(lam) / math.sqrt(1 + t * t))
    E = E0 + k0 * A * (eta + sum(alpha[j] * math.cos(2 * (j + 1) * xi) * math.sinh(2 * (j + 1) * eta) for j in range(3)))
    N = N0 + k0 * A * (xi + sum(alpha[j] * math.sin(2 * (j + 1) * xi) * math.cosh(2 * (j + 1) * eta) for j in range(3)))
    return E, N

def grid_ref(lat, lon):
    """Six-figure grid reference (100 m) the way a Victorian topo sheet is read: 3 digits easting, 3 northing."""
    E, N = latlon_to_mga55(lat, lon)
    return f"{int(E / 100) % 1000:03d} {int(N / 100) % 1000:03d}", int(E), int(N)

LOCALITIES = [  # approximate town centres, decimal degrees (schematic use; positions ±2 km)
    ("Warragul", -38.160, 145.931), ("Drouin", -38.137, 145.858), ("Neerim South", -38.012, 145.955),
    ("Moe", -38.172, 146.260), ("Morwell", -38.236, 146.396), ("Traralgon", -38.195, 146.541),
    ("Sale", -38.104, 147.066), ("Leongatha", -38.476, 145.946), ("Korumburra", -38.432, 145.824),
    ("Yarram", -38.564, 146.676), ("Bairnsdale", -37.826, 147.613),
]

if __name__ == '__main__':
    import sys
    svg = contour_svg()
    print(len(svg), 'bytes of SVG')
    open(sys.argv[1] if len(sys.argv) > 1 else 'topo-tile.svg', 'w').write(svg)
    for name, la, lo in LOCALITIES:
        gr, E, N = grid_ref(la, lo)
        print(f"{name:14s} GR {gr}  E {E}  N {N}")
