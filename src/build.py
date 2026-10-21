#!/usr/bin/env python3
"""Generate the Fitz Feral Hunters site (Paddock composition, D700 SP-01b) from content/site.json.

    python3 src/build.py                    # writes public/*.html, sitemap, robots, favicon
    python3 src/build.py --artifact FILE    # single-document review build (hash-routed) for the claude.ai artifact

Spec-first: every component carries data-per with the catalogue records it honours; the spec sheet
dialog lists the full cited set. The D700 corpus itself is not in this repo — names of cited entries
ship in src/cited-names.json. The contour field is generated deterministically at build time (src/topo.py).
"""
import re, json, html, pathlib, datetime, sys, math
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from css import CSS
import cites, topo

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = pathlib.Path(__file__).resolve().parent
PUB = ROOT / 'public'
S = json.loads((ROOT / 'content' / 'site.json').read_text())
NAMES = json.loads((SRC / 'cited-names.json').read_text())
STAMP = "D700 · 4 Oct 2026 · 6511 entries D0001-D6558 · 218 laws · 387 capsules · 466 groups · 1824 pairs · 499 anti-pairs · 457 palettes · 21 lenses"
X = cites.PADDOCK
SEED = "fitzferalhunters-paddock"
ARTIFACT = '--artifact' in sys.argv

def esc(s): return html.escape(str(s), quote=True)

def per(key):
    ids = list(cites.SHARED.get(key, [])) + list(X.get(key, []))
    ds = [i for i in ids if re.match(r'^D\d{4}$', i)]
    return f' data-per="{" ".join(dict.fromkeys(ds))}"' if ds else ''

# ---------------------------------------------------------------- tokens + stylesheet
TOKENS = """
  /* PALCAND "FFH Card" — sampled from the client's card: green #1b2622, gold #a07a48, champagne #cdb682, near-white type; ground kept from PAL Noma Forest Season */
  --bg:#f8f6f2; --surface:#f1eee8; --surface-2:color-mix(in srgb, var(--bg), var(--ink) 7%);
  --ink:#1b2622; --ink-2:color-mix(in srgb, var(--ink) 72%, var(--bg)); --ink-3:color-mix(in srgb, var(--ink) 38%, var(--bg));
  --chrome:#1b2622; --chrome-2:color-mix(in srgb, var(--chrome), #ffffff 7%);
  --gold:#a07a48; --gold-light:#cdb682; --gold-ink:color-mix(in srgb, var(--gold), var(--ink) 32%);
  --accent:color-mix(in srgb, var(--chrome), #ffffff 12%); --accent-ink:#f8f6f2;
  --line:color-mix(in srgb, var(--ink) 15%, transparent); --line-strong:color-mix(in srgb, var(--ink) 40%, transparent);
  --wash:color-mix(in srgb, var(--ink) 8%, transparent); --wash-press:color-mix(in srgb, var(--ink) 16%, transparent);
  --accent-hover:color-mix(in srgb, var(--accent), #ffffff 8%); --accent-press:color-mix(in srgb, var(--accent), var(--ink) 18%);
  --focus:#2c84db; --focus-dark:#7cb8ff; --err:#9b2c20; --ok:#2E6E4E;
  --foot-bg:var(--chrome); --foot-ink:#f8f6f2; --foot-line:color-mix(in srgb, #f8f6f2 18%, transparent);
  --grain-blend:multiply; --grain-alpha:.16; --body-track:0; --ring:none;
  --scrim:linear-gradient(to top, rgb(27 38 34 / .82), rgb(27 38 34 / 0) 70%);
  --sp:"SP-01c PADDOCK";
"""
GRAIN = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='160' height='160'%3E"
         "%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='2' stitchTiles='stitch'/%3E"
         "%3CfeColorMatrix values='0 0 0 0 .5 0 0 0 0 .5 0 0 0 0 .5 0 0 0 1 0'/%3E%3C/filter%3E"
         "%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E")
TOPO_SVG = topo.contour_svg(seed=SEED, color='#1b2622')
TOPO_URI = topo.svg_data_uri(TOPO_SVG) if ARTIFACT else '/topo-tile.svg'
import base64
def asset(path):
    """Brand asset URL: a site path, or a data URI in the single-file artifact build."""
    if not ARTIFACT: return path
    p = PUB / path.lstrip('/'); mime = 'image/png' if p.suffix == '.png' else 'image/jpeg'
    return f'data:{mime};base64,' + base64.b64encode(p.read_bytes()).decode()
css = (CSS.replace('@@TOKENS@@', TOKENS).replace('@@STAMP@@', STAMP).replace('@@GRAIN@@', GRAIN)
          .replace('@@TOPO@@', TOPO_URI).replace('@@SCHEME@@', 'light'))
css += """
.varbar .hide{margin-inline-start:4px}
.varbar[hidden]{display:none}
.notfound{padding-block:96px}
"""

PAGES = [("home", "/", "Home"), ("services", "/services", "Services"), ("about", "/about", "About"), ("gallery", "/gallery", "Gallery"), ("contact", "/contact", "Contact")]
HREF = {k: h for k, h, _ in PAGES}
def href(key, anchor=''):
    if ARTIFACT: return f'#{key}'
    return HREF[key] + (f'#{anchor}' if anchor else '')
def route_attr(key): return f' data-route="{key}"' if ARTIFACT else ''

TITLES = {
  "home": (f"{S['name']} · Pest & vermin control, Gippsland", "Professional pest control in Gippsland: deer control, kangaroo culling, pigs, foxes, rabbits and wild dogs for farmers and landholders across regional Victoria. Licensed, insured, humane. Based in Warragul."),
  "services": (f"Services · {S['name']}", "Deer control, kangaroo culling, feral pigs, foxes, rabbits and wild dogs across Gippsland. Night and thermal work, planned, insured and humane under the Victorian codes."),
  "about": (f"About · {S['name']}", f"Based in {S['base']}, working across {S['region']}. Licensed, insured, accountable. AHCPMG304 humane dispatch."),
  "gallery": (f"Gallery · {S['name']}", "Thermal images, night work, property damage and gear from pest control jobs across Gippsland."),
  "contact": (f"Contact · {S['name']}", f"Ring {S['phone_display']} or send an enquiry. Based in {S['base']}, working across {S['region']}."),
}

# real grid references (MGA zone 55) for the base and every locality on the chips
GR = {name: topo.grid_ref(la, lo) for name, la, lo in topo.LOCALITIES}
BASE_GR = GR[S['base']][0] if S['base'] in GR else ''

SPRITE = '''<svg hidden aria-hidden="true" focusable="false"><symbol id="i-phone" viewBox="0 0 24 24"><path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2z"/></symbol><symbol id="i-mail" viewBox="0 0 24 24"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/></symbol><symbol id="i-ext" viewBox="0 0 24 24"><path d="M14 4h6v6M20 4l-9 9M19 14v5a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V6a1 1 0 0 1 1-1h5"/></symbol><symbol id="i-pin" viewBox="0 0 24 24"><path d="M12 21s-6-5.5-6-11a6 6 0 0 1 12 0c0 5.5-6 11-6 11z"/><circle cx="12" cy="10" r="2.2"/></symbol><symbol id="i-north" viewBox="0 0 24 24"><path d="M12 3v18M8 21h8"/><path class="fill" d="M12 3l4.5 9h-9z"/></symbol></svg>'''
def ico(name, cls="ico"): return f'<svg class="{cls}" aria-hidden="true"><use href="#{name}"/></svg>'

def north(label="N"):
    return f'<span class="datum" title="Grid: MGA zone 55, GDA2020"><svg class="north" viewBox="0 0 24 24" aria-hidden="true"><use href="#i-north"/></svg><span>{label} · MGA 55</span></span>'

def scalebar(stack=False, unit='1 km'):
    return (f'<figure class="scalebar{" stack" if stack else ""}" aria-label="Scale bar: 150 pixels represent 1 kilometre at this sheet scale"{per("scalebar")}>'
            f'<div><div class="bar"><i></i><i></i><i></i><i></i></div><div class="ticks"><span>0</span><span>250</span><span>500</span><span>750</span><span>m</span></div></div>'
            f'<span class="unit">{unit}</span></figure>')

def meta(sheet, extra=''):
    return f'<p class="meta"{per("meta")}><b>Sheet</b><span>{esc(sheet)}</span><span class="lead" aria-hidden="true"></span><span>GR <span class="num">{BASE_GR}</span></span><span>MGA 55 · GDA2020</span>{extra}</p>'

def corners():
    return '<i class="corner tl" aria-hidden="true"></i><i class="corner tr" aria-hidden="true"></i><i class="corner bl" aria-hidden="true"></i><i class="corner br" aria-hidden="true"></i>'

def slot(kind, label, src="", ar=None, tag="Photo slot"):
    """A ratio-locked photo with registration ticks and a privacy plate. With a src it renders a real lazy image."""
    style = f' style="--ar:{ar}"' if ar else ''
    plate = '<span class="plate">Location withheld</span>'
    if src:
        return (f'<figure class="slot photo"{per("slot")}{per("frame")} style="margin:0{";--ar:"+ar if ar else ""}">'
                f'<img src="{esc(src)}" alt="{esc(label)}" loading="lazy" decoding="async" width="1600" height="1200" style="width:100%;height:100%;object-fit:cover;position:absolute;inset:0">{corners()}{plate}</figure>')
    cls = 'slot thermal' if kind == 'thermal' else 'slot'
    mark = {'thermal': 'Thermal', 'night': 'Night', 'property': 'Property', 'gear': 'Gear'}.get(kind, 'Photo')
    return (f'<div class="{cls}"{style}{per("slot")}{per("frame")} role="img" aria-label="{esc(tag)}: {esc(label)}">'
            f'<span class="mark" aria-hidden="true">{mark}</span><span class="tag">{esc(tag)} · client supplies</span>{plate}{corners()}'
            f'<span class="label">{esc(label)}<small>{esc(kind)} · jpg/avif · alt text written per photo</small></span></div>')

def nav_links(current):
    return ''.join(f'<li><a href="{href(k)}"{route_attr(k)}{" aria-current=page" if (k == current and not ARTIFACT) else ""}>{t}</a></li>' for k, h, t in PAGES)

def contact_line():
    return f'''<div class="contact-line"{per("contactline")}>
        <div class="kv"><b>{ico("i-phone")}Phone</b><span class="num">{S['phone_display']}</span><button type="button" class="copy" data-copy="{S['phone_display']}" aria-label="Copy phone number">Copy</button></div>
        <div class="kv"><b>{ico("i-mail")}Email</b><span>{S['email']}</span><button type="button" class="copy" data-copy="{S['email']}" aria-label="Copy email address">Copy</button></div>
        <div class="kv"><b>{ico("i-ext")}Follow</b><span><a href="{S['instagram']}" target="_blank" rel="noopener">Instagram</a> · <a href="{S['facebook']}" target="_blank" rel="noopener">Facebook</a></span></div>
      </div>'''

def cta_row(extra_style='', gold=False):
    return f'''<div class="cta-row"{per("cta")}>
        <a class="btn {'btn-gold' if gold else 'btn-primary'}" href="{href('contact','enquiry')}"{route_attr('contact')} data-focus="enquiry">Request a quote</a>
        <a class="btn btn-secondary num" href="tel:{S['phone_e164']}"{extra_style}>Call {S['phone_display']}</a>
      </div>'''

def header(current):
    return f'''
<div class="skips"{per("skip")}><a href="#main">Skip to content</a><a href="{href('contact','enquiry')}"{route_attr('contact')}>Skip to contact</a></div>
<header class="site-head"{per("header")}>
  <div class="wrap">
    <a class="logo" href="{href('home')}"{route_attr('home')}{per("wordmark")}{per("logo")}><img src="{asset('/brand/logo-lockup.png')}" alt="{esc(S['name'])} — {esc(S['tagline'])}" width="640" height="181" decoding="async" fetchpriority="high"></a>
    {north()}
    <nav class="nav" aria-label="Primary"{per("nav")}><ul>{nav_links(current)}<li class="nav-cta"><a class="btn btn-gold" href="{href('contact','enquiry')}"{route_attr('contact')} data-focus="enquiry" style="min-height:44px;padding-inline:16px">Request a quote</a></li></ul></nav>
    <details class="drawer" id="drawer"{per("burger")}><summary aria-label="Menu">Menu</summary><ul>{nav_links(current)}<li><a href="{href('contact','enquiry')}"{route_attr('contact')} data-focus="enquiry" style="color:var(--gold-light);font-weight:700">Request a quote</a></li></ul></details>
  </div>
</header>'''

def footer():
    abn = esc(S['abn']) if S['abn'] else '<span class="flag" style="border-color:var(--foot-line);color:inherit">to be supplied</span>'
    return f'''
<footer class="site-foot" id="footer"{per("footer")}>
  <div class="wrap">
    <div class="cols">
      <div class="stack" style="--gap:12px">
        <a class="logo foot-logo" href="{href('home')}"{route_attr('home')}{per("logo")}><img src="{asset('/brand/logo-lockup.png')}" alt="{esc(S['name'])} — {esc(S['tagline'])}" width="640" height="181" loading="lazy" decoding="async"></a>
        <p class="small" style="max-width:36ch">Licensed, insured feral animal control for farmers and landholders across {esc(S['region'])}.</p>
        <p class="small num">{S['phone_display']} · {S['email']}</p>
      </div>
      <div><h4>Pages</h4><ul>{nav_links(None)}</ul></div>
      <div><h4>Elsewhere</h4><ul><li><a href="{S['instagram']}" target="_blank" rel="noopener">Instagram {esc(S['instagram_handle'])}</a></li><li><a href="{S['facebook']}" target="_blank" rel="noopener">Facebook</a></li><li><a href="{href('contact','enquiry')}"{route_attr('contact')} data-focus="enquiry">Request a quote</a></li></ul></div>
    </div>
    <div class="cred-strip" aria-label="Credentials">{''.join(f'<span>{esc(t)}</span>' for t, _ in S['credentials'][:7])}</div>
    <div class="margin"{per("topo")}{per("meta")}><svg class="north" viewBox="0 0 24 24" aria-hidden="true"><use href="#i-north"/></svg><span>Grid MGA zone 55 · datum GDA2020</span><span>Contour interval 10 m · index 50 m</span><span>Base GR <span class="num">{BASE_GR}</span></span>{scalebar()}<span>Sheet styling after Victorian 1:25 000 topographic maps · field seed <span class="num">{esc(SEED)}</span></span></div>
    <div class="legal"><span>&copy; {datetime.date.today().year} {esc(S['name'])}</span><span>{esc(S['base'])} VIC</span><span>ABN {abn}</span><span>Work carried out under Victorian codes of practice</span></div>
  </div>
</footer>'''

def ctabar():
    return f'''
<div class="cta-bar" id="ctabar"{per("ctabar")}>
  <a class="btn btn-secondary num" href="tel:{S['phone_e164']}">Call {S['phone_display']}</a>
  <a class="btn btn-primary" href="{href('contact','enquiry')}"{route_attr('contact')} data-focus="enquiry">Request a quote</a>
</div>'''

def varbar():
    other = esc(S['night_shift_url'])
    return f'''
<div class="varbar" id="varbar"{per("varbar")} role="region" aria-label="Mockup controls">
  <div class="wrap">
    <span><strong>D700 mockup · SP-01c PADDOCK v3</strong><span class="long"> · card colourway (green · gold · cream) on the topographic sheet · seed {esc(SEED)}</span></span>
    <span class="grow"></span>
    <button type="button" id="t-motion" aria-pressed="false" title="Emulates the reduced-motion twin (D4980); the real gate is the media query (D3453)"><span class="long">Motion: on</span><span class="short">Motion</span></button>
    <button type="button" id="t-topo" aria-pressed="true" title="Toggle the contour field and grid (D2410) to compare against v1"><span class="long">Sheet: on</span><span class="short">Sheet</span></button>
    <button type="button" id="t-xray" aria-pressed="false" title="Outline every component and show the D-ids it honours"><span class="long">X-ray</span><span class="short">X-ray</span></button>
    <button type="button" id="t-spec" command="show-modal" commandfor="spec"><span class="long">Spec sheet</span><span class="short">Spec</span></button>
    <a href="{other}" target="_blank" rel="noopener"><span class="long">Other mockup: </span>Night Shift &rarr;</a>
    <button type="button" class="hide" id="t-hide" aria-label="Hide mockup controls">&times;</button>
  </div>
</div>'''

def spec_dialog():
    spfile = (ROOT / 'docs' / 'SP-01c-ffh-paddock-v3.md')
    spfile = spfile.read_text() if spfile.exists() else '(SP record not found in docs/)'
    allids = []
    for grp in (cites.SHARED, X, cites.TOP):
        for k, ids in grp.items(): allids += ids
    uniq = list(dict.fromkeys(allids))
    d_entries = sorted(i for i in uniq if re.match(r'^D\d{4}$', i))
    laws = sorted((i for i in uniq if i.startswith('LAW-')), key=lambda s: int(s.split('-')[1]))
    pairs = sorted((i for i in uniq if i.startswith('PAIR-')), key=lambda s: int(s.split('-')[1]))
    nopairs = sorted((i for i in uniq if i.startswith('NOPAIR-')), key=lambda s: int(s.split('-')[1]))
    pals = [i for i in uniq if i.startswith('PAL ') or i.startswith('CPAIR') or i.startswith('PALRULE')]
    lenses = [i for i in uniq if i.startswith('LENS') or i.startswith('DOC') or i.startswith('TENSION')]
    tops = [i for i in uniq if re.match(r'^(TP|DY|MK)', i)]
    ids_li = ''.join(f'<li>{i} · {esc(NAMES.get(i, ""))}</li>' for i in d_entries)
    counts = f'''<span>{len(d_entries)} entries</span><span>{len(laws)} laws</span><span>{len(pairs)} pairs</span><span>{len(nopairs)} anti-pairs resolved</span><span>{len(pals)} palette records</span><span>{len(lenses)} doctrine records</span><span>{len(tops)} templates/dynamics/kits</span><span>{len(uniq)} citations total</span>'''
    return f'''
<dialog class="spec" id="spec"{per("spec")} aria-labelledby="spec-title">
  <div class="bar"><h2 id="spec-title">SP-01c · PADDOCK v3 · spec sheet</h2><button type="button" class="btn btn-secondary" id="spec-close" aria-label="Close spec sheet">&times;</button></div>
  <div class="inner">
    <p class="counts">{counts}</p>
    <p>Compiled against <span class="mono">{esc(STAMP)}</span>. Every component on the page carries a <span class="mono">data-per</span> attribute naming the records it honours; switch on X-ray and hover any outlined component to read them. The v2 delta adds the topographic sheet layer: a seeded contour field (seed <span class="mono">{esc(SEED)}</span>, same hills on every build), an MGA-style 1 km grid, real zone-55 grid references for the base and every locality, scale bars, a map key, marginalia and photo registration frames. Nothing on the layer animates and no new hue was added.</p>
    <h3>Templates, dynamics, motion kit</h3><p class="mono">{' · '.join(tops)}</p>
    <h3>Palettes and colour rules</h3><p class="mono">{' · '.join(pals)}</p>
    <h3>Doctrine lenses</h3><p class="mono">{' · '.join(lenses)}</p>
    <h3>Laws honoured</h3><p class="mono">{' · '.join(laws)}</p>
    <h3>Pairs honoured</h3><p class="mono">{' · '.join(pairs)}</p>
    <h3>Anti-pairs swept and resolved</h3><p class="mono">{' · '.join(nopairs)}</p>
    <h3>Entries ({len(d_entries)})</h3><ul class="ids">{ids_li}</ul>
    <h3>Surface plan record</h3><pre>{esc(spfile)}</pre>
    <h3>What Fitz supplies before launch</h3>
    <ul style="margin:0;padding-left:18px;display:grid;gap:4px"><li>A vector or larger logo file if one exists (the current lockup is cut from the card).</li><li>Photos: hero, two about shots, nine gallery shots at 1600px wide, with a one-line description each for alt text.</li><li>Instagram bio wording for the hero lede.</li><li>Testimonials with name, property type and locality (or a Google Business reviews link).</li><li>Pricing line for the first FAQ, ABN for the footer, and whether thermal drone services stay on the Services page.</li></ul>
  </div>
</dialog>'''

# ---------------------------------------------------------------- locality map + key (service-area section)
def locality_map():
    pts = {name: topo.latlon_to_mga55(la, lo) for name, la, lo in topo.LOCALITIES}
    E0, E1, N0, N1 = 384000, 574000, 5722000, 5822000   # 190 km × 100 km window
    W, H = 760, 400
    sx = W / (E1 - E0); sy = H / (N1 - N0)
    def xy(E, N): return (E - E0) * sx, H - (N - N0) * sy
    grid = ''
    for E in range(400000, E1, 20000):
        x, _ = xy(E, N0); grid += f'<line class="grid" x1="{x:.1f}" y1="0" x2="{x:.1f}" y2="{H}"/><text class="edge" x="{x+3:.1f}" y="10">{E//1000}</text>'
    for N in range(5740000, N1, 20000):
        _, y = xy(E0, N); grid += f'<line class="grid" x1="0" y1="{y:.1f}" x2="{W}" y2="{y:.1f}"/><text class="edge" x="4" y="{y-3:.1f}">{N//1000}</text>'
    bx, by = xy(*pts[S['base']])
    def ring(r):
        rr = r * 1000 * sx; lx, ly = bx + rr * 0.71 + 3, by - rr * 0.71 - 3
        label = f'<text class="edge" x="{lx:.1f}" y="{ly:.1f}">{r} km</text>' if 0 < lx < W - 40 and 12 < ly < H else ''
        return f'<circle class="ring" cx="{bx:.1f}" cy="{by:.1f}" r="{rr:.1f}"/>' + label
    rings = ''.join(ring(r) for r in (25, 50, 100))
    towns = ''
    for name, (E, N) in pts.items():
        x, y = xy(E, N)
        if name == S['base']:
            towns += f'<rect class="base" x="{x-5:.1f}" y="{y-5:.1f}" width="10" height="10"/><text x="{x+9:.1f}" y="{y-6:.1f}" font-weight="700">{esc(name)} · base</text>'
        else:
            dx, dy = (-9, 4) if name in ('Bairnsdale', 'Drouin') else (9, 4)
            anchor = ' text-anchor="end"' if dx < 0 else ''
            towns += f'<circle class="town" cx="{x:.1f}" cy="{y:.1f}" r="3.6"/><text x="{x+dx:.1f}" y="{y+dy:.1f}"{anchor}>{esc(name)}</text>'
    km25 = 25000 * sx
    scale = f'<g transform="translate({W-km25-16:.1f} {H-22})"><line class="scale" x1="0" y1="0" x2="{km25:.1f}" y2="0"/><line class="scale" x1="0" y1="-4" x2="0" y2="4"/><line class="scale" x1="{km25/2:.1f}" y1="-3" x2="{km25/2:.1f}" y2="3"/><line class="scale" x1="{km25:.1f}" y1="-4" x2="{km25:.1f}" y2="4"/><text class="edge" x="0" y="14">0</text><text class="edge" x="{km25:.1f}" y="14" text-anchor="end">25 km</text></g>'
    northg = f'<g transform="translate({W-30} 18)"><use href="#i-north" width="20" height="20" x="-10" y="-10" style="stroke:var(--ink);fill:none;stroke-width:1.4"/><text class="edge" x="-3" y="24">N</text></g>'
    tile = f'<pattern id="topo-p" patternUnits="userSpaceOnUse" width="600" height="600"><image href="{TOPO_URI}" width="600" height="600"/></pattern>'
    names_list = ', '.join(n for n, _, _ in topo.LOCALITIES)
    return f'''<svg class="map" viewBox="0 0 {W} {H}" role="img" aria-label="Schematic map of the service area: {esc(S['base'])} as base with 25, 50 and 100 kilometre rings, and the localities {esc(names_list)}. Positions approximate."{per("map")}>
  <defs>{tile}</defs>
  <rect width="{W}" height="{H}" fill="url(#topo-p)" opacity=".9"/>
  {grid}{rings}{towns}{scale}{northg}
  <rect class="frame" x=".5" y=".5" width="{W-1}" height="{H-1}"/>
</svg>'''

def legend():
    k = lambda d, extra='': f'<svg viewBox="0 0 56 18" aria-hidden="true"><path class="k" d="{d}"{extra}/></svg>'
    rows = [
      (k("M0 11 C14 2 28 16 56 7"), "<b>Contour</b> · 10 m interval"),
      (k("M0 12 C14 3 28 17 56 8", ' stroke-width="2"'), "<b>Index contour</b> · every 50 m"),
      (k("M0 9h56 M8 6v6 M20 6v6 M32 6v6 M44 6v6"), "<b>Fence line</b> · where deer and dogs cross"),
      (k("M0 9h56", ' stroke-dasharray="6 4"'), "<b>Vehicle track</b> · access agreed before the job"),
      (k("M0 9 C8 4 12 14 20 9 S32 4 40 9 S52 14 56 9", ' stroke-dasharray="2 3"'), "<b>Dam / watercourse</b> · pig and fox sign"),
      (k("M2 9h2 M10 9h2 M18 9h2 M26 9h2 M34 9h2 M42 9h2 M50 9h2", ' stroke-width="3"'), "<b>Tree line / scrub</b> · thermal work"),
      ('<svg viewBox="0 0 56 18" aria-hidden="true"><rect x="23" y="4" width="10" height="10" fill="var(--accent)" stroke="var(--ink)" stroke-width="1.2"/></svg>', f"<b>Base</b> · {esc(S['base'])}"),
      ('<svg viewBox="0 0 56 18" aria-hidden="true"><circle cx="28" cy="9" r="3.6" fill="var(--bg)" stroke="var(--ink)" stroke-width="1.6"/></svg>', "<b>Locality</b> · with its six-figure grid reference"),
    ]
    return f'''<div class="legend"{per("legend")}><p class="eyebrow">Map key</p><dl>{''.join(f'<dt>{a}</dt><dd>{b}</dd>' for a, b in rows)}</dl>
      <p class="caption">Grid references are MGA zone 55 (GDA2020), read eastings then northings to 100 m, the way a Victorian 1:25 000 sheet is read. Town positions are approximate; the map is for orientation, not navigation.</p></div>'''

# ---------------------------------------------------------------- marginalia (facts beside prose)
NOTES = {
  "services": [
    ("Sambar", "Introduced to Victoria in the 1860s; now the main deer species across Gippsland's bush edge."),
    ("Fallow", "In Australia since the 1830s; paddock and plantation damage, often in daylight."),
    ("Foxes", "Released in Victoria in the 1850s for hunting; lambing losses follow the season."),
    ("Rabbits", "Twenty-four released at Barwon Park, Winchelsea, in 1859. The rest is history."),
    ("ATCW", "Authority to Control Wildlife, issued by the Victorian government under the Wildlife Act 1975."),
    ("Game Licence", "Issued by the Game Management Authority; deer are a game species in Victoria."),
  ],
  "about": [
    ("Warragul", f"Base of operations, grid reference {BASE_GR} on the MGA zone 55 grid."),
    ("AHCPMG304", "A nationally recognised unit for humane dispatch; the standard every job is held to."),
    ("Codes", "Victorian codes of practice for the humane control of each species govern the method."),
    ("Insurance", "$20 million public liability, with a certificate of currency available before work starts."),
  ],
}
def margin_notes(key):
    rows = ''.join(f'<p><sup>{i+1}</sup><span><b style="font-weight:600;color:var(--ink)">{esc(t)}.</b> {esc(d)}</span></p>' for i, (t, d) in enumerate(NOTES[key]))
    return f'<aside class="margin-notes" aria-label="Notes"{per("marginalia")}><h4>Notes</h4>{rows}</aside>'
def fn(n): return f'<sup class="fn" aria-label="note {n}">{n}</sup>'

# ---------------------------------------------------------------- page bodies
def divider(label):
    return f'<div class="wrap divider"{per("scalebar")}><span class="mono">{esc(label)}</span>{scalebar()}</div>'

def home_body():
    hp = S['hero_photo']
    creds_li = ''.join(
        f'<li{" class=note" if i == 7 else ""}><span class="eyebrow">{"Note" if i == 7 else "Credential"}</span><b class="num">{esc(t)}</b><p>{esc(d)}</p></li>'
        for i, (t, d) in enumerate(S['credentials']))
    tiles = ''.join(f'''
    <article class="tile reveal">
      <h3>{esc(t)}</h3><p>{esc(d)}</p>
      <a class="stretch" href="{href('services','svc-'+k)}"{route_attr('services')} data-focus="svc-{k}" aria-hidden="true" tabindex="-1"></a>
      <a class="btn btn-secondary" href="{href('services','svc-'+k)}"{route_attr('services')} data-focus="svc-{k}">Details<span class="sr"> for {esc(t)}</span></a>
    </article>''' for k, t, d, _ in S['services'])
    steps = ''.join(f'<li class="reveal"><b>{esc(t)}</b><p>{esc(d)}</p></li>' for t, d in S['steps'])
    if S['testimonials']:
        quotes = ''.join(f'<figure class="ghost reveal" style="border-style:solid"><blockquote style="margin:0"><q>{esc(q)}</q></blockquote><figcaption class="who">{esc(w)}</figcaption></figure>' for q, w in S['testimonials'])
        tnote = ''
    else:
        quotes = ''.join('<div class="ghost reveal"><q>Landholder quote to come. Fitz supplies real words from real jobs; nothing is written on their behalf.</q><span class="who">Name · property type · locality</span></div>' for _ in range(3))
        tnote = '<p class="measure small">Three slots, held empty until Fitz supplies quotes with a name, property type and locality. A Google Business reviews link sits here once reviews exist; third-party scores outrank hand-picked quotes. <span class="flag">section hidden until quotes arrive</span></p>'
    status_flag = '' if S.get('credentials_current') else ' <span class="flag">status line Fitz can edit</span>'
    lede_flag = f' <span class="flag">{esc(S["lede_flag"])}</span>' if S.get('lede_flag') else ''
    chips = ''.join(f'<li>{esc(a)}{"<span class=gr>GR " + GR[a][0] + "</span>" if a in GR else ""}</li>' for a in S['area'])
    return f'''
<section class="hero wrap"{per("hero")}{per("hero-layout")}>
  <div class="hero-grid">
    <div class="stack" style="--gap:22px">
      {meta("Home")}
      <p class="eyebrow"{per("wordmark")}>{esc(S['base'])} · Gippsland · Regional Victoria</p>
      <h1 id="h-home" tabindex="-1">{esc(S['headline'])}</h1>
      <p class="lede"{per("lede")}>{esc(S['lede'])}{lede_flag}</p>
      <p class="descriptors"{per("brand")}>{' <span aria-hidden="true">·</span> '.join(esc(x) for x in S['descriptors'])}</p>
      {cta_row()}
      {contact_line()}
    </div>
    {slot(hp[0], hp[1], hp[2], ar="4/5")}
  </div>
</section>
{divider("Credentials")}
<section class="band alt"{per("creds")}{per("setpiece")}>
  <div class="wrap stack" style="--gap:28px">
    <div class="sec-head reveal">
      <p class="eyebrow">Licensed · insured · accountable</p>
      <h2>The paperwork is in order before the ute leaves the shed</h2>
      <p class="status"><i aria-hidden="true"></i> {esc(S['status_line'])}{status_flag}</p>
    </div>
    <ol class="creds reveal" aria-label="Credentials">{creds_li}</ol>
  </div>
</section>
{divider("Services")}
<section class="band"{per("services-grid")}>
  <div class="wrap stack" style="--gap:28px">
    <div class="sec-head reveal"><p class="eyebrow">Services</p><h2>What I'm called out for</h2>
      <p class="measure">Deer and kangaroo work is most of it. The rest is the usual Gippsland list: pigs, foxes, rabbits and wild dogs, night and thermal where it counts.</p></div>
    <div class="grid grid-3">{tiles}</div>
  </div>
</section>
{divider("How it works")}
<section class="band alt"{per("howitworks")}>
  <div class="wrap stack" style="--gap:28px">
    <div class="sec-head reveal"><p class="eyebrow">How it works</p><h2>Four steps, no surprises</h2></div>
    <ol class="steps">{steps}</ol>
  </div>
</section>
{divider("Standards")}
<section class="band"{per("triad")}>
  <div class="wrap stack" style="--gap:28px">
    <div class="sec-head reveal"><p class="eyebrow">Why landholders call Fitz</p><h2>Turns up. Does it properly. Leaves it as found.</h2></div>
    <div class="triad reveal">
      <div><b>Licensed and insured</b><p>Firearms and Game licences, SSAA Farmer Assist, First Aid and $20 million public liability. Certificates before the first visit.</p></div>
      <div><b>Planned, not improvised</b><p>Every job starts with a walk of the property and a written plan: stock, neighbours, access, safe lines of fire, dates.</p></div>
      <div><b>Humane under the codes</b><p>AHCPMG304 humane dispatch. Clean, legal and professional is the standard, not the upsell.</p></div>
    </div>
  </div>
</section>
{divider("From the paddock")}
<section class="band alt"{per("testimonials")}>
  <div class="wrap stack" style="--gap:28px">
    <div class="sec-head reveal"><p class="eyebrow">From the paddock</p><h2>What landholders say</h2>{tnote}</div>
    <div class="grid grid-3">{quotes}</div>
  </div>
</section>
{divider("Service area")}
<section class="band"{per("area")}{per("topo")}>
  <div class="wrap stack" style="--gap:24px">
    <div class="sec-head reveal"><p class="eyebrow">Service area</p><h2>Based in {esc(S['base'])}, working across Gippsland</h2>
      <p class="measure">West, South and Central Gippsland most weeks. East Gippsland and the rest of regional Victoria by arrangement. Rings are road-free distances from the base; the real trip is longer.</p></div>
    <div class="area-grid reveal"><div class="map-scroll">{locality_map()}</div>{legend()}</div>
    <ul class="chips reveal" aria-label="Localities served with grid references">{chips}</ul>
  </div>
</section>
<section class="band invert"{per("strip")}>
  <div class="wrap stack" style="--gap:20px">
    <h2 style="max-width:16ch">Got deer on the fence line? Get in touch.</h2>
    {cta_row(' style="border-color:var(--foot-line);color:var(--foot-ink)"', gold=True)}
    <p class="caption">{S['email']} · Instagram {esc(S['instagram_handle'])} · Facebook {esc(S['facebook_label'])}</p>
  </div>
</section>'''

def services_body():
    notes = {k: i + 1 for i, (k, _) in enumerate(NOTES['services'])}
    def row(k, t, d, bullets):
        marks = {'deer': fn(notes['Sambar']) + fn(notes['Fallow']), 'kangaroos': fn(notes['ATCW']), 'foxes': fn(notes['Foxes']), 'rabbits': fn(notes['Rabbits'])}.get(k, '')
        return f'''
    <article class="service" id="svc-{k}">
      <div class="stack" style="--gap:8px"><h3 tabindex="-1">{esc(t)}{marks}</h3><p class="small" style="color:var(--ink-2)">{esc(d)}</p></div>
      <ul>{''.join(f'<li>{esc(x)}</li>' for x in bullets)}</ul>
    </article>'''
    rows = ''.join(row(k, t, d, b) for k, t, d, b in S['services'])
    drone = '''
      <article class="service" id="svc-drone"><div class="stack" style="--gap:8px"><h3 tabindex="-1">Thermal drone services <span class="flag">optional, remove if not offering yet</span></h3><p class="small" style="color:var(--ink-2)">Thermal drone surveys to count animals, find mobs and map where they move before a program starts.</p></div>
        <ul><li>Pre-program counts</li><li>Finding stock after a storm or fire</li><li>Mapping movement corridors</li></ul></article>''' if S.get('thermal_drone') else ''
    faqs = ''.join(f'<details class="faq"><summary>{esc(q)}</summary><p>{esc(a)}</p></details>' for q, a in S['faq'])
    return f'''
<section class="page" aria-labelledby="h-services"{per("services")}>
  <div class="wrap stack" style="--gap:36px">
    <div class="sec-head">{meta("Services")}<p class="eyebrow">Services</p><h1 id="h-services" tabindex="-1" style="font-size:var(--fs-h2)">Pest and vermin control, Gippsland and regional Victoria</h1>
      <p class="measure">Every job is planned, insured and carried out humanely under the relevant Victorian codes of practice. Deer control on farms and kangaroo culling are the two most common call-outs; the rest of the list is below.</p></div>
    <div class="notes-layout">
      <div>{rows}
        <article class="service" id="svc-night"><div class="stack" style="--gap:8px"><h3 tabindex="-1">Night work and thermal</h3><p class="small" style="color:var(--ink-2)">Most feral animals move after dark. Thermal optics let me find them, count them and take them cleanly without lighting up the whole paddock.</p></div>
          <ul><li>Thermal spotting and shooting</li><li>Quiet, planned movements around stock</li><li>Counts you can use for permits and planning</li></ul></article>{drone}
      </div>
      {margin_notes('services')}
    </div>
    <div class="prose"{per("privacy")}>
      <h3>What a job includes</h3>
      <ul><li>A site visit and a written plan: stock, neighbours, access, dates and safety.</li><li>Humane dispatch to AHCPMG304 and the code for each species.</li><li>Carcass handling and disposal as agreed with you.</li><li>A short report afterwards and a follow-up if the numbers call for it.</li></ul>
      <h3>Permits and codes, in plain language</h3>
      <p class="small" style="color:var(--ink-2)">Kangaroo control on private land needs an Authority to Control Wildlife{fn(notes['ATCW'])} from the Victorian government; I can help with the application. Deer are a game species and are taken under a Game Licence{fn(notes['Game Licence'])}. All work follows the relevant Victorian codes of practice for the humane control of the species involved.</p>
    </div>
    <div{per("faq")}>{faqs}</div>
    <div class="cta-row"{per("cta")}><a class="btn btn-primary" href="{href('contact','enquiry')}"{route_attr('contact')} data-focus="enquiry">Request a quote</a><a class="btn btn-quiet num" href="tel:{S['phone_e164']}">or call {S['phone_display']}</a></div>
  </div>
</section>'''

def about_body():
    cur = esc(S['credentials_current']) if S.get('credentials_current') else '<span class="flag">month year</span>'
    a1, a2 = S['about_photos']
    ledger = ''.join(f'<li><b>{esc(t)}</b><span class="lead" aria-hidden="true"></span><span>{esc(d)}</span></li>' for t, d in S['credentials'][:7])
    return f'''
<section class="page" aria-labelledby="h-about"{per("about")}>
  <div class="wrap">
    <div class="notes-layout">
      <div class="prose">
        {meta("About")}
        <p class="eyebrow">About</p>
        <h1 id="h-about" tabindex="-1" style="font-size:var(--fs-h2)">Based in {esc(S['base'])}{fn(1)}, working across Gippsland and regional Victoria</h1>
        <p>{esc(S['name'])} is one operator, licensed and insured{fn(4)}, doing feral animal control for farmers and landholders who want the job done properly and the place left as they found it.</p>
        <p>The standard is clean, legal and professional: a plan before the first night, humane dispatch to AHCPMG304{fn(2)}, and a short report after. No trophies, no mess, no surprises for the neighbours{fn(3)}.</p>
        <p><span class="flag">one or two lines about Fitz to come</span> Years on farms, where the hunting started, why the thermal kit: in his own words, kept short.</p>
        <h3>Credentials</h3>
        <ul class="ledger num"{per("ledger")}>{ledger}</ul>
        <p class="caption">Credentials current as at {cur}. Certificates of currency supplied on request before work starts.</p>
        <figure class="card-figure"{per("brand")}><img src="{asset('/brand/fitz-card.jpg')}" alt="The Fitz Feral Hunters card: rifle mark, Protecting Victoria's Farms, contract pest control, deer and feral management, thermal hunting, farm security, fully insured, 0499 866 580" width="1280" height="755" loading="lazy" decoding="async"><figcaption class="caption">The card, as supplied. The site's green, gold and cream are sampled from it.</figcaption></figure>
        <div class="grid grid-2" style="margin-top:8px">{slot(*a1)}{slot(*a2)}</div>
      </div>
      {margin_notes('about')}
    </div>
  </div>
</section>'''

def gallery_body():
    g = S['gallery']
    items = ''.join(f'''<li><figure style="margin:0"><button type="button" data-lb="{i}" aria-label="Open photo {i+1} of {len(g)}: {esc(c)}">{slot(k, c, src)}</button><figcaption><span class="mono" style="color:var(--ink-2)">Fig. {i+1:02d}</span> · {esc(c)}</figcaption></figure></li>''' for i, (k, c, src) in enumerate(g))
    return f'''
<section class="page" aria-labelledby="h-gallery"{per("gallery")}>
  <div class="wrap stack" style="--gap:28px">
    <div class="sec-head">{meta("Gallery")}<p class="eyebrow">Gallery</p><h1 id="h-gallery" tabindex="-1" style="font-size:var(--fs-h2)">From the job</h1>
      <p class="measure">Thermal images, night work, property damage and gear. No property locations are shown and nobody's face appears without their say-so; every frame carries the plate that says so.</p></div>
    <ul class="gal">{items}</ul>
    <p class="caption">Each slot takes one client photo at 1600px wide, delivered as AVIF with a JPEG fallback and lazy-loaded below the fold. Alt text is written per photo, describing what the thermal shows, not just "thermal image".</p>
  </div>
</section>
<dialog class="lightbox" id="lightbox" closedby="any" aria-labelledby="lb-cap" data-lightbox-state="closed"{per("gallery")}>
  <div class="frame">
    <div class="bar"><span class="eyebrow num" id="lb-pos">1 of {len(g)}</span>
      <div style="display:flex;gap:8px"><button type="button" class="btn btn-secondary" id="lb-prev" aria-label="Previous photo">&larr;</button><button type="button" class="btn btn-secondary" id="lb-next" aria-label="Next photo">&rarr;</button><button type="button" class="btn btn-secondary" id="lb-close" aria-label="Close">&times;</button></div></div>
    <div id="lb-slot">{slot(g[0][0], g[0][1], g[0][2], ar="3/2")}</div>
    <p id="lb-cap" class="caption">{esc(g[0][1])}</p>
  </div>
</dialog>'''

def contact_body():
    checks = ''.join(f'<label><input type="checkbox" name="help" value="{esc(x)}"> {esc(x)}</label>' for x in ["Deer", "Kangaroos", "Pigs", "Foxes", "Rabbits", "Wild dogs", "Not sure yet"])
    action = '#contact' if ARTIFACT else '/api/enquiry'
    note = ('Mockup: this review build does not send. On the live site the form posts to a server function that emails ' if ARTIFACT else 'Mockup: enquiries sent here are received by the site\'s server function and emailed to ') + S['email'] + (' and shows the confirmation below.' if ARTIFACT else ' once the mail key is configured; until then they are logged for testing.') + ' Without script the plain form still submits.'
    return f'''
<section class="page" aria-labelledby="h-contact">
  <div class="wrap contact-grid">
    <div class="stack" style="--gap:28px">
      <div class="sec-head" style="margin:0">{meta("Contact")}<p class="eyebrow">Contact</p><h1 id="h-contact" tabindex="-1" style="font-size:var(--fs-h2)">Ring, email or send the form</h1>
        <p class="measure">Phone is quickest. If I'm out on a job I'll ring back the same day where I can.</p></div>
      <div class="contact-list"{per("contactline")}>
        <div class="kv"><b>{ico("i-phone")}Phone</b><div class="row"><span class="num" id="c-phone">{S['phone_display']}</span><button type="button" class="copy" data-copy="{S['phone_display']}" aria-label="Copy phone number">Copy</button><a class="btn btn-secondary" href="tel:{S['phone_e164']}">Call</a></div></div>
        <div class="kv"><b>{ico("i-mail")}Email</b><div class="row"><span id="c-email" style="font-size:19px">{S['email']}</span><button type="button" class="copy" data-copy="{S['email']}" aria-label="Copy email address">Copy</button></div></div>
        <div class="kv"><b>{ico("i-pin")}Based in</b><div class="row"><span style="font-size:19px">{esc(S['base'])}, Gippsland VIC</span><span class="mono" style="color:var(--ink-2)">GR <span class="num">{BASE_GR}</span> · MGA 55</span></div></div>
        <div class="kv"{per("socials")}><b>Follow the work</b><div class="socials"><a href="{S['instagram']}" target="_blank" rel="noopener">Instagram {esc(S['instagram_handle'])} {ico("i-ext")}</a><a href="{S['facebook']}" target="_blank" rel="noopener">Facebook · {esc(S['facebook_label'])} {ico("i-ext")} <span class="flag">confirm page URL</span></a></div></div>
      </div>
    </div>
    <div>
      <form class="form" id="enquiry" action="{action}" method="post"{per("form")} aria-describedby="form-note">
        <p class="note" id="draft-note" role="status" hidden>Restored the enquiry you started earlier. Nothing has been sent.</p>
        <div class="summary" id="err-summary" role="alert" tabindex="-1" hidden><b>Fix the following to send your enquiry</b><ul id="err-list"></ul></div>
        <div class="field"><label for="f-name">Name</label><input id="f-name" name="name" type="text" autocomplete="name" required enterkeyhint="next" maxlength="120"><span class="err" id="e-name">Enter your name so I know who to ask for.</span></div>
        <div class="field"><label for="f-phone">Phone</label><span class="hint">Mobile is best. Any format is fine, e.g. 0412 345 678.</span><input id="f-phone" name="phone" type="tel" autocomplete="tel" inputmode="tel" required enterkeyhint="next" pattern="[0-9+\\(\\)\\s\\-]{{8,}}" maxlength="40"><span class="err" id="e-phone">Enter a phone number with at least eight digits.</span></div>
        <div class="field"><label for="f-email">Email <span style="font-weight:400;color:var(--ink-2)">(optional)</span></label><input id="f-email" name="email" type="email" autocomplete="email" inputmode="email" enterkeyhint="next" maxlength="200"><span class="err" id="e-email">That email address doesn't look right. Check it or leave it blank.</span></div>
        <div class="field"><label for="f-loc">Property location</label><span class="hint">Town or nearest locality, e.g. Neerim South. No street address needed.</span><input id="f-loc" name="location" type="text" autocomplete="address-level2" required enterkeyhint="next" maxlength="120"><span class="err" id="e-loc">Tell me the town or locality so I can plan the trip.</span></div>
        <fieldset class="field" id="f-help"><legend>What do you need help with?</legend><span class="hint">Tick everything that applies.</span><div class="checks">{checks}</div><span class="err" id="e-help">Tick at least one. "Not sure yet" is fine.</span></fieldset>
        <div class="field"><label for="f-msg">Anything else <span style="font-weight:400;color:var(--ink-2)">(optional)</span></label><span class="hint">Damage, numbers, timing, access: whatever you've noticed.</span><textarea id="f-msg" name="message" enterkeyhint="done" maxlength="2000"></textarea></div>
        <div class="sr" aria-hidden="true"><label for="f-company">Leave this field empty</label><input id="f-company" name="company" type="text" tabindex="-1" autocomplete="off"></div>
        <div class="cta-row"><button type="submit" class="btn btn-primary" id="f-submit"><span class="spin" aria-hidden="true"></span><span class="lbl">Send enquiry</span></button><span class="note" id="form-note">Your details go to Fitz only. No mailing list, nothing shared.</span></div>
        <p class="note">{note}</p>
      </form>
      <div class="confirm" id="confirm" role="status" tabindex="-1" hidden{per("confirm")}>
        <b>Enquiry received</b>
        <p>Thanks, <span id="confirm-name">there</span>. Fitz will ring the number you gave, usually within two business days.</p>
        <p class="small" style="color:var(--ink-2)"><b style="font-weight:600;color:var(--ink)">What happens next:</b> a quick phone chat about the property and the animals, then a site visit if it's a fit. If it's urgent, call <a class="num" href="tel:{S['phone_e164']}">{S['phone_display']}</a>.</p>
        <p class="small"><a href="{href('contact','enquiry')}" id="confirm-reset">Send another enquiry</a></p>
      </div>
    </div>
  </div>
</section>'''

def notfound_body():
    return f'''
<section class="page notfound" aria-labelledby="h-404">
  <div class="wrap prose">
    <p class="eyebrow">404</p>
    <h1 id="h-404" style="font-size:var(--fs-h2)">That page isn't here</h1>
    <p>The address may have been mistyped, or the page has moved. The five pages that exist are below, and the phone always works.</p>
    <ul>{''.join(f'<li><a href="{h}">{t}</a></li>' for _, h, t in PAGES)}</ul>
    <p class="num">Call {S['phone_display']}</p>
  </div>
</section>'''

# ---------------------------------------------------------------- script
SCRIPT = r"""
<script>
(function(){
  var root=document.documentElement;
  var ARTIFACT=%%ARTIFACT%%;
  /* hash router (artifact build only): five sections, bare tokens */
  if(ARTIFACT){
    var pages=[].slice.call(document.querySelectorAll('[data-page]')), tokens=pages.map(function(p){return p.id});
    var titles=%%TITLES%%;
    var live=document.getElementById('route-live');
    function current(){var h=(location.hash||'#home').slice(1);return tokens.indexOf(h)>-1?h:'home'}
    function show(tok,focusId){
      pages.forEach(function(p){p.hidden=(p.id!==tok)});
      [].forEach.call(document.querySelectorAll('[data-route]'),function(a){ if(a.closest('.nav, .drawer, .site-foot')){ if(a.getAttribute('data-route')===tok && !a.classList.contains('btn')) a.setAttribute('aria-current','page'); else a.removeAttribute('aria-current'); } });
      var d=document.getElementById('drawer'); if(d) d.removeAttribute('open');
      document.title=titles[tok]||document.title; if(live) live.textContent=(titles[tok]||'').split(' · ')[0];
      var target=focusId?document.getElementById(focusId):null;
      if(target){ target.scrollIntoView({block:'start'}); (target.querySelector('input')||target).focus({preventScroll:true}); }
      else { window.scrollTo({top:0,behavior:'instant'}); var h=document.getElementById('h-'+tok); if(h) h.focus({preventScroll:true}); }
    }
    document.addEventListener('click',function(e){ var a=e.target.closest('a[data-route]'); if(!a) return; var tok=a.getAttribute('data-route'); e.preventDefault(); var f=a.getAttribute('data-focus'); if(location.hash!=='#'+tok){ history.pushState(null,'','#'+tok); } show(tok,f); });
    window.addEventListener('hashchange',function(){show(current())}); window.addEventListener('popstate',function(){show(current())});
    show(current());
  }
  /* copy buttons */
  [].forEach.call(document.querySelectorAll('.copy'),function(b){
    b.addEventListener('click',function(){
      var txt=b.getAttribute('data-copy'), done=function(){b.setAttribute('data-state','copied');b.textContent='Copied';setTimeout(function(){b.removeAttribute('data-state');b.textContent='Copy'},1600)};
      function fallback(){ var el=b.previousElementSibling; if(el){ var r=document.createRange(); r.selectNodeContents(el); var s=getSelection(); s.removeAllRanges(); s.addRange(r); } b.textContent='Select & copy'; setTimeout(function(){b.textContent='Copy'},1600); }
      try{ navigator.clipboard.writeText(txt).then(done,fallback); }catch(err){ fallback(); }
    });
  });
  /* mobile CTA bar exits while the form is in view */
  var bar=document.getElementById('ctabar'), form=document.getElementById('enquiry');
  if(bar && form && 'IntersectionObserver' in window){
    new IntersectionObserver(function(es){ es.forEach(function(x){ bar.hidden=x.isIntersecting && x.intersectionRatio>0.15; }); },{threshold:[0,0.15,0.5]}).observe(form);
  }
  /* lightbox */
  var lb=document.getElementById('lightbox'), caps=%%CAPS%%, idx=0, invoker=null;
  function paint(i){ idx=(i+caps.length)%caps.length; var s=document.getElementById('lb-slot'); var src=document.querySelector('[data-lb="'+idx+'"] .slot'); if(src){ var c=src.cloneNode(true); c.style.setProperty('--ar','3/2'); s.replaceChildren(c);} document.getElementById('lb-cap').textContent=caps[idx]; document.getElementById('lb-pos').textContent=(idx+1)+' of '+caps.length; }
  if(lb && lb.showModal){
    [].forEach.call(document.querySelectorAll('[data-lb]'),function(b){ b.addEventListener('click',function(){ invoker=b; paint(+b.getAttribute('data-lb')); lb.setAttribute('data-lightbox-state','open'); lb.showModal(); document.getElementById('lb-close').focus(); }); });
    document.getElementById('lb-prev').addEventListener('click',function(){paint(idx-1)});
    document.getElementById('lb-next').addEventListener('click',function(){paint(idx+1)});
    document.getElementById('lb-close').addEventListener('click',function(){lb.close()});
    lb.addEventListener('keydown',function(e){ if(e.key==='ArrowLeft') paint(idx-1); if(e.key==='ArrowRight') paint(idx+1); });
    lb.addEventListener('click',function(e){ if(e.target===lb) lb.close(); });
    lb.addEventListener('close',function(){ lb.setAttribute('data-lightbox-state','closed'); if(invoker) invoker.focus(); });
  }
  /* form: progressive enhancement over the native form */
  if(form){
    form.setAttribute('novalidate','');
    var fields=[['f-name','e-name',function(el){return el.value.trim().length>0}],
                ['f-phone','e-phone',function(el){return el.value.replace(/\D/g,'').length>=8}],
                ['f-email','e-email',function(el){return el.value.trim()===''||el.checkValidity()}],
                ['f-loc','e-loc',function(el){return el.value.trim().length>0}]];
    var KEY='ffh-enquiry-draft';
    try{ var draft=JSON.parse(localStorage.getItem(KEY)||'null'); if(draft){ var restored=false; Object.keys(draft).forEach(function(k){ var el=document.getElementById(k); if(el && el.value==='' && draft[k]){ el.value=draft[k]; restored=true; } }); if(restored){ document.getElementById('draft-note').hidden=false; } } }catch(e){}
    var saveT=null;
    form.addEventListener('input',function(){ clearTimeout(saveT); saveT=setTimeout(function(){ try{ var o={}; fields.forEach(function(f){o[f[0]]=document.getElementById(f[0]).value}); o['f-msg']=document.getElementById('f-msg').value; localStorage.setItem(KEY,JSON.stringify(o)); }catch(e){} },300); });
    function mark(el,errId,ok){ var w=el.closest('.field'); if(!w) return; w.classList.toggle('has-err',!ok); el.setAttribute('aria-invalid',ok?'false':'true'); if(!ok) el.setAttribute('aria-describedby',errId); }
    fields.forEach(function(f){ var el=document.getElementById(f[0]); el.addEventListener('blur',function(){ if(el.value!=='') mark(el,f[1],f[2](el)); }); });
    var sum=document.getElementById('err-summary'), list=document.getElementById('err-list');
    function showErrors(errs){ list.replaceChildren(); errs.forEach(function(x){ var li=document.createElement('li'), a=document.createElement('a'); a.href='#'+x[0]; a.textContent=x[1]; a.addEventListener('click',function(ev){ev.preventDefault(); var t=document.getElementById(x[0]); (t.querySelector('input')||t).focus(); t.scrollIntoView({block:'center'})}); li.appendChild(a); list.appendChild(li); }); sum.hidden=false; sum.focus(); }
    function succeed(){ var c=document.getElementById('confirm'); document.getElementById('confirm-name').textContent=document.getElementById('f-name').value.trim().split(' ')[0]||'there'; form.hidden=true; c.hidden=false; c.focus(); try{localStorage.removeItem(KEY)}catch(e){} }
    form.addEventListener('submit',function(e){
      e.preventDefault();
      var errs=[];
      fields.forEach(function(f){ var el=document.getElementById(f[0]); var ok=f[2](el); mark(el,f[1],ok); if(!ok) errs.push([f[0],document.getElementById(f[1]).textContent]); });
      var anyHelp=form.querySelectorAll('input[name="help"]:checked').length>0; var hf=document.getElementById('f-help'); hf.classList.toggle('has-err',!anyHelp); if(!anyHelp) errs.push(['f-help',document.getElementById('e-help').textContent]);
      if(errs.length){ showErrors(errs); return; }
      sum.hidden=true;
      var btn=document.getElementById('f-submit'); btn.style.width=btn.getBoundingClientRect().width+'px'; btn.classList.add('is-busy'); btn.setAttribute('aria-disabled','true'); btn.disabled=true; btn.querySelector('.lbl').textContent='Sending';
      function reset(){ btn.classList.remove('is-busy'); btn.disabled=false; btn.removeAttribute('aria-disabled'); btn.style.width=''; btn.querySelector('.lbl').textContent='Send enquiry'; }
      if(ARTIFACT){ setTimeout(function(){ reset(); succeed(); },900); return; }
      var fd=new FormData(form), payload={}; fd.forEach(function(v,k){ if(k==='help'){ (payload.help=payload.help||[]).push(v);} else payload[k]=v; });
      fetch(form.action,{method:'POST',headers:{'Content-Type':'application/json','Accept':'application/json'},body:JSON.stringify(payload)})
        .then(function(r){ return r.json().then(function(j){ return {ok:r.ok && j.ok, j:j}; }); })
        .then(function(res){ reset(); if(!res.ok){ showErrors([['f-submit', (res.j && res.j.error) || 'The enquiry could not be sent. Ring '+document.getElementById('c-phone').textContent+' instead.']]); return; } succeed(); })
        .catch(function(){ reset(); showErrors([['f-submit','No connection. The enquiry was not sent; ring '+document.getElementById('c-phone').textContent+' instead.']]); });
    });
    document.getElementById('confirm-reset').addEventListener('click',function(e){ e.preventDefault(); form.reset(); document.getElementById('confirm').hidden=true; form.hidden=false; document.getElementById('f-name').focus(); });
  }
  /* reviewer chrome */
  var vb=document.getElementById('varbar'), tm=document.getElementById('t-motion'), tt=document.getElementById('t-topo'), tx=document.getElementById('t-xray'), ts=document.getElementById('t-spec'), th=document.getElementById('t-hide'), spec=document.getElementById('spec');
  try{ if(localStorage.getItem('ffh-varbar')==='hidden') vb.hidden=true; }catch(e){}
  th.addEventListener('click',function(){ vb.hidden=true; try{localStorage.setItem('ffh-varbar','hidden')}catch(e){} });
  tm.addEventListener('click',function(){ var off=root.getAttribute('data-motion')==='off'; if(off){root.removeAttribute('data-motion');tm.querySelector('.long').textContent='Motion: on';tm.setAttribute('aria-pressed','false')} else {root.setAttribute('data-motion','off');tm.querySelector('.long').textContent='Motion: off (reduced-motion twin)';tm.setAttribute('aria-pressed','true')} });
  tt.addEventListener('click',function(){ var off=root.getAttribute('data-sheet')==='off'; if(off){root.removeAttribute('data-sheet');tt.querySelector('.long').textContent='Sheet: on';tt.setAttribute('aria-pressed','true')} else {root.setAttribute('data-sheet','off');tt.querySelector('.long').textContent='Sheet: off (v1 ground)';tt.setAttribute('aria-pressed','false')} });
  var NAMES=%%NAMES%%;
  tx.addEventListener('click',function(){ var on=root.hasAttribute('data-xray'); if(on){root.removeAttribute('data-xray');tx.setAttribute('aria-pressed','false');[].forEach.call(document.querySelectorAll('[data-per]'),function(el){el.removeAttribute('title')})} else {root.setAttribute('data-xray','');tx.setAttribute('aria-pressed','true');[].forEach.call(document.querySelectorAll('[data-per]'),function(el){el.setAttribute('title',el.getAttribute('data-per').split(' ').map(function(i){return i+' '+(NAMES[i]||'')}).join('\n'))})} });
  if(!('commandForElement' in HTMLButtonElement.prototype)){ ts.addEventListener('click',function(){ if(!spec.open) spec.showModal(); }); }
  document.getElementById('spec-close').addEventListener('click',function(){ spec.close(); });
  spec.addEventListener('click',function(e){ if(e.target===spec) spec.close(); });
})();
</script>"""

def jsonld():
    return json.dumps({
      "@context": "https://schema.org", "@type": "LocalBusiness", "name": S['name'],
      "description": TITLES['home'][1], "telephone": S['phone_e164'], "email": S['email'], "url": S['url'].rstrip('/') + '/',
      "image": S['url'].rstrip('/') + '/og-1200x630.png',
      "address": {"@type": "PostalAddress", "addressLocality": S['base'], "addressRegion": "VIC", "addressCountry": "AU"},
      "areaServed": ["Gippsland", "Regional Victoria"], "sameAs": [S['instagram']],
      "knowsAbout": ["Deer control", "Kangaroo culling", "Feral pig control", "Fox control", "Rabbit control", "Wild dog control", "Thermal night work"],
    }, ensure_ascii=False)

def script():
    return (SCRIPT.replace('%%CAPS%%', json.dumps([c for _, c, _ in S['gallery']])).replace('%%NAMES%%', json.dumps(NAMES, ensure_ascii=False))
                  .replace('%%ARTIFACT%%', 'true' if ARTIFACT else 'false').replace('%%TITLES%%', json.dumps({k: TITLES[k][0] for k in TITLES})))

def document(key, body, title, desc):
    path = HREF.get(key, '/404')
    canonical = S['url'].rstrip('/') + ('' if path == '/' else path)
    robots = '' if S.get('indexable') else '<meta name="robots" content="noindex, nofollow">\n'
    sheet_css = css + "\n[data-sheet='off'] body::after{display:none}\n"
    return f'''<!doctype html>
<html lang="en-AU">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
{robots}<meta name="theme-color" content="#1b2622">
<link rel="canonical" href="{canonical}">
<link rel="icon" href="/favicon.png" type="image/png" sizes="64x64">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{esc(S['name'])}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{S['url'].rstrip('/')}/og-1200x630.png">
<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cinzel:wght@700&family=Barlow+Condensed:wght@600;700&family=Barlow:wght@400;500;600&display=swap">
<style>{sheet_css}</style>
<script type="application/ld+json">{jsonld()}</script>
</head>
<body>
{SPRITE}{varbar()}{header(key)}
<main id="main"{per("doc")}{per("tokens")}{per("type")}{per("motion")}{per("focus")}{per("ground")}{per("topo")}>
{body}
</main>
{footer()}{ctabar()}{spec_dialog()}{script()}
</body>
</html>'''

def artifact_document():
    """Single document for the claude.ai artifact: no skeleton tags, hash-routed sections."""
    sections = ''.join(f'<section data-page="{k}" id="{k}" aria-labelledby="h-{k}">{b}</section>' for k, b in
                       (('home', home_body()), ('services', services_body()), ('about', about_body()), ('gallery', gallery_body()), ('contact', contact_body())))
    sheet_css = css + "\n[data-sheet='off'] body::after{display:none}\n"
    return f'''<title>Fitz Feral Hunters Paddock</title>
<meta name="claude:viewport-fit-sides" content="cover">
<meta name="description" content="{esc(TITLES['home'][1])}">
<meta name="theme-color" content="#1b2622">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cinzel:wght@700&family=Barlow+Condensed:wght@600;700&family=Barlow:wght@400;500;600&display=swap">
<style>{sheet_css}</style>
<script type="application/ld+json">{jsonld()}</script>
{SPRITE}{varbar()}{header(None)}
<main id="main"{per("doc")}{per("tokens")}{per("type")}{per("motion")}{per("focus")}{per("ground")}{per("topo")}>
<p class="sr" id="route-live" aria-live="polite"></p>
{sections}
</main>
{footer()}{ctabar()}{spec_dialog()}{script()}'''

FAVICON = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="8" fill="#2E6E4E"/><path d="M18 14h30v9H28v9h17v9H28v9H18z" fill="#f8f6f2"/></svg>'''

def main():
    allids = set()
    for grp in (cites.SHARED, X, cites.TOP):
        for ids in grp.values(): allids.update(ids)
    n_entries = len([i for i in allids if re.match(r"^D\d{4}$", i)])
    if ARTIFACT:
        out = pathlib.Path(sys.argv[sys.argv.index('--artifact') + 1])
        out.write_text(artifact_document())
        print(f'artifact → {out} ({out.stat().st_size/1024:.0f} KB) · {n_entries} entries · {len(allids)} citations · topo tile {len(TOPO_SVG)/1024:.0f} KB')
        return
    PUB.mkdir(exist_ok=True)
    pages = {'home': home_body(), 'services': services_body(), 'about': about_body(), 'gallery': gallery_body(), 'contact': contact_body()}
    for key, body in pages.items():
        t, d = TITLES[key]
        (PUB / ('index.html' if key == 'home' else f'{key}.html')).write_text(document(key, body, t, d))
    (PUB / '404.html').write_text(document('404', notfound_body(), f"Page not found · {S['name']}", "That page isn't here."))
    (PUB / 'favicon.svg').write_text(FAVICON)
    (PUB / 'topo-tile.svg').write_text(TOPO_SVG)
    base = S['url'].rstrip('/'); today = datetime.date.today().isoformat()
    (PUB / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
        ''.join(f'  <url><loc>{base}{"" if h == "/" else h}</loc><lastmod>{today}</lastmod></url>\n' for _, h, _ in PAGES) + '</urlset>\n')
    (PUB / 'robots.txt').write_text(('User-agent: *\nAllow: /\n' if S.get('indexable') else 'User-agent: *\nDisallow: /\n') + f'Sitemap: {base}/sitemap.xml\n')
    print(f'built {len(pages)+1} pages into public/ · {n_entries} entries · {len(allids)} citations · topo tile {len(TOPO_SVG)/1024:.0f} KB')

if __name__ == '__main__':
    main()
