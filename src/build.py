#!/usr/bin/env python3
"""Generate the Fitz Feral Hunters site (Paddock composition, D700 SP-01) into public/.

    python3 src/build.py            # reads content/site.json, writes public/*.html, sitemap, robots

Spec-first: every component carries data-per with the catalogue records it honours; the spec
sheet dialog lists the full cited set. The D700 corpus itself is not in this repo — names of
cited entries ship in src/cited-names.json.
"""
import re, json, html, pathlib, datetime, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from css import CSS
import cites

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = pathlib.Path(__file__).resolve().parent
PUB = ROOT / 'public'
S = json.loads((ROOT / 'content' / 'site.json').read_text())
NAMES = json.loads((SRC / 'cited-names.json').read_text())
STAMP = "D700 · 4 Oct 2026 · 6511 entries D0001-D6558 · 218 laws · 387 capsules · 466 groups · 1824 pairs · 499 anti-pairs · 457 palettes · 21 lenses"
X = cites.PADDOCK

def esc(s): return html.escape(str(s), quote=True)

def per(key):
    ids = list(cites.SHARED.get(key, [])) + list(X.get(key, []))
    ds = [i for i in ids if re.match(r'^D\d{4}$', i)]
    return f' data-per="{" ".join(dict.fromkeys(ds))}"' if ds else ''

TOKENS = """
  --bg:#f8f6f2; --surface:#f1eee8; --surface-2:color-mix(in srgb, var(--bg), var(--ink) 7%);
  --ink:#432a27; --ink-2:#664e49; --ink-3:#bfaea3;
  --accent:#2E6E4E; --accent-ink:#ffffff; --chrome:var(--ink);
  --line:color-mix(in srgb, var(--ink) 15%, transparent); --line-strong:color-mix(in srgb, var(--ink) 40%, transparent);
  --wash:color-mix(in srgb, var(--ink) 8%, transparent); --wash-press:color-mix(in srgb, var(--ink) 16%, transparent);
  --accent-hover:color-mix(in srgb, var(--accent), var(--ink) 10%); --accent-press:color-mix(in srgb, var(--accent), var(--ink) 18%);
  --focus:#2c84db; --err:#9b2c20; --ok:#2E6E4E;
  --foot-bg:#2c1714; --foot-ink:#f8f6f2; --foot-line:color-mix(in srgb, #f8f6f2 18%, transparent);
  --grain-blend:multiply; --grain-alpha:.16; --body-track:0; --ring:none;
  --scrim:linear-gradient(to top, rgb(44 23 20 / .78), rgb(44 23 20 / 0) 70%);
  --sp:"SP-01 PADDOCK";
"""
GRAIN = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='160' height='160'%3E"
         "%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='2' stitchTiles='stitch'/%3E"
         "%3CfeColorMatrix values='0 0 0 0 .5 0 0 0 0 .5 0 0 0 0 .5 0 0 0 1 0'/%3E%3C/filter%3E"
         "%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E")
css = CSS.replace('@@TOKENS@@', TOKENS).replace('@@STAMP@@', STAMP).replace('@@GRAIN@@', GRAIN).replace('@@SCHEME@@', 'light')
# site-mode additions: real pages, no hidden sections
css += """
.varbar .hide{margin-inline-start:4px}
.varbar[hidden]{display:none}
.notfound{padding-block:96px}
"""

PAGES = [("home", "/", "Home"), ("services", "/services", "Services"), ("about", "/about", "About"), ("gallery", "/gallery", "Gallery"), ("contact", "/contact", "Contact")]
HREF = {k: h for k, h, _ in PAGES}
TITLES = {
  "home": (f"{S['name']} · Pest & vermin control, Gippsland", "Professional pest control in Gippsland: deer control, kangaroo culling, pigs, foxes, rabbits and wild dogs for farmers and landholders across regional Victoria. Licensed, insured, humane. Based in Warragul."),
  "services": (f"Services · {S['name']}", "Deer control, kangaroo culling, feral pigs, foxes, rabbits and wild dogs across Gippsland. Night and thermal work, planned, insured and humane under the Victorian codes."),
  "about": (f"About · {S['name']}", f"Based in {S['base']}, working across {S['region']}. Licensed, insured, accountable. AHCPMG304 humane dispatch."),
  "gallery": (f"Gallery · {S['name']}", "Thermal images, night work, property damage and gear from pest control jobs across Gippsland."),
  "contact": (f"Contact · {S['name']}", f"Ring {S['phone_display']} or send an enquiry. Based in {S['base']}, working across {S['region']}."),
}

SPRITE = '''<svg hidden aria-hidden="true" focusable="false"><symbol id="i-phone" viewBox="0 0 24 24"><path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2z"/></symbol><symbol id="i-mail" viewBox="0 0 24 24"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/></symbol><symbol id="i-ext" viewBox="0 0 24 24"><path d="M14 4h6v6M20 4l-9 9M19 14v5a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V6a1 1 0 0 1 1-1h5"/></symbol><symbol id="i-pin" viewBox="0 0 24 24"><path d="M12 21s-6-5.5-6-11a6 6 0 0 1 12 0c0 5.5-6 11-6 11z"/><circle cx="12" cy="10" r="2.2"/></symbol></svg>'''
def ico(name): return f'<svg class="ico" aria-hidden="true"><use href="#{name}"/></svg>'

def slot(kind, label, src="", ar=None, tag="Photo slot"):
    """A ratio-locked photo. With a src (under public/photos/) it renders a real lazy image; without one, an honest labelled slot."""
    style = f' style="--ar:{ar}"' if ar else ''
    if src:
        return (f'<figure class="slot photo"{style}{per("slot")} style="margin:0{";--ar:"+ar if ar else ""}">'
                f'<img src="{esc(src)}" alt="{esc(label)}" loading="lazy" decoding="async" width="1600" height="1200" style="width:100%;height:100%;object-fit:cover;position:absolute;inset:0"></figure>')
    cls = 'slot thermal' if kind == 'thermal' else 'slot'
    mark = {'thermal': 'Thermal', 'night': 'Night', 'property': 'Property', 'gear': 'Gear'}.get(kind, 'Photo')
    return (f'<div class="{cls}"{style}{per("slot")} role="img" aria-label="{esc(tag)}: {esc(label)}">'
            f'<span class="mark" aria-hidden="true">{mark}</span><span class="tag">{esc(tag)} · client supplies</span>'
            f'<span class="label">{esc(label)}<small>{esc(kind)} · jpg/avif · alt text written per photo</small></span></div>')

def nav_links(current):
    return ''.join(f'<li><a href="{h}"{" aria-current=page" if k == current else ""}>{t}</a></li>' for k, h, t in PAGES)

def contact_line():
    return f'''<div class="contact-line"{per("contactline")}>
        <div class="kv"><b>{ico("i-phone")}Phone</b><span class="num">{S['phone_display']}</span><button type="button" class="copy" data-copy="{S['phone_display']}" aria-label="Copy phone number">Copy</button></div>
        <div class="kv"><b>{ico("i-mail")}Email</b><span>{S['email']}</span><button type="button" class="copy" data-copy="{S['email']}" aria-label="Copy email address">Copy</button></div>
        <div class="kv"><b>{ico("i-ext")}Follow</b><span><a href="{S['instagram']}" target="_blank" rel="noopener">Instagram</a> · <a href="{S['facebook']}" target="_blank" rel="noopener">Facebook</a></span></div>
      </div>'''

def cta_row(extra_style=''):
    return f'''<div class="cta-row"{per("cta")}>
        <a class="btn btn-primary" href="/contact#enquiry">Request a quote</a>
        <a class="btn btn-secondary num" href="tel:{S['phone_e164']}"{extra_style}>Call {S['phone_display']}</a>
      </div>'''

def header(current):
    return f'''
<div class="skips"{per("skip")}><a href="#main">Skip to content</a><a href="/contact#enquiry">Skip to contact</a></div>
<header class="site-head"{per("header")}>
  <div class="wrap">
    <div class="logo-slot" aria-hidden="true">Logo slot</div>
    <a class="wordmark" href="/"{per("wordmark")}><b>{esc(S['name'])}</b><small>{esc(S['tagline'])}</small></a>
    <nav class="nav" aria-label="Primary"{per("nav")}><ul>{nav_links(current)}<li class="nav-cta"><a class="btn btn-primary" href="/contact#enquiry" style="min-height:44px;padding-inline:16px">Request a quote</a></li></ul></nav>
    <details class="drawer" id="drawer"{per("burger")}><summary aria-label="Menu">Menu</summary><ul>{nav_links(current)}<li><a href="/contact#enquiry" style="color:var(--accent);font-weight:700">Request a quote</a></li></ul></details>
  </div>
</header>'''

def footer():
    abn = esc(S['abn']) if S['abn'] else '<span class="flag" style="border-color:var(--foot-line);color:inherit">to be supplied</span>'
    return f'''
<footer class="site-foot" id="footer"{per("footer")}>
  <div class="wrap">
    <div class="cols">
      <div class="stack" style="--gap:12px">
        <a class="wordmark" href="/" style="color:inherit"><b>{esc(S['name'])}</b><small style="color:color-mix(in srgb, var(--foot-ink) 65%, transparent)">{esc(S['tagline'])}</small></a>
        <p class="small" style="max-width:36ch">Licensed, insured feral animal control for farmers and landholders across {esc(S['region'])}.</p>
        <p class="small num">{S['phone_display']} · {S['email']}</p>
      </div>
      <div><h4>Pages</h4><ul>{nav_links(None)}</ul></div>
      <div><h4>Elsewhere</h4><ul><li><a href="{S['instagram']}" target="_blank" rel="noopener">Instagram {esc(S['instagram_handle'])}</a></li><li><a href="{S['facebook']}" target="_blank" rel="noopener">Facebook</a></li><li><a href="/contact#enquiry">Request a quote</a></li></ul></div>
    </div>
    <div class="cred-strip" aria-label="Credentials">{''.join(f'<span>{esc(t)}</span>' for t, _ in S['credentials'][:7])}</div>
    <div class="legal"><span>&copy; {datetime.date.today().year} {esc(S['name'])}</span><span>{esc(S['base'])} VIC</span><span>ABN {abn}</span><span>Work carried out under Victorian codes of practice</span></div>
  </div>
</footer>'''

def ctabar():
    return f'''
<div class="cta-bar" id="ctabar"{per("ctabar")}>
  <a class="btn btn-secondary num" href="tel:{S['phone_e164']}">Call {S['phone_display']}</a>
  <a class="btn btn-primary" href="/contact#enquiry">Request a quote</a>
</div>'''

def varbar():
    return f'''
<div class="varbar" id="varbar"{per("varbar")} role="region" aria-label="Mockup controls">
  <div class="wrap">
    <span><strong>D700 mockup · SP-01 PADDOCK</strong><span class="long"> · PAL Noma Forest Season · accent from PAL Forest Institutional (PALRULE-04)</span></span>
    <span class="grow"></span>
    <button type="button" id="t-motion" aria-pressed="false" title="Emulates the reduced-motion twin (D4980); the real gate is the media query (D3453)"><span class="long">Motion: on</span><span class="short">Motion</span></button>
    <button type="button" id="t-xray" aria-pressed="false" title="Outline every component and show the D-ids it honours"><span class="long">X-ray</span><span class="short">X-ray</span></button>
    <button type="button" id="t-spec" command="show-modal" commandfor="spec"><span class="long">Spec sheet</span><span class="short">Spec</span></button>
    <a href="{esc(S['night_shift_url'])}" target="_blank" rel="noopener"><span class="long">Other mockup: </span>Night Shift &rarr;</a>
    <button type="button" class="hide" id="t-hide" aria-label="Hide mockup controls">&times;</button>
  </div>
</div>'''

def spec_dialog():
    spfile = (ROOT / 'docs' / 'SP-01-ffh-paddock.md').read_text() if (ROOT / 'docs' / 'SP-01-ffh-paddock.md').exists() else '(SP record not found in docs/)'
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
  <div class="bar"><h2 id="spec-title">SP-01 · PADDOCK · spec sheet</h2><button type="button" class="btn btn-secondary" id="spec-close" aria-label="Close spec sheet">&times;</button></div>
  <div class="inner">
    <p class="counts">{counts}</p>
    <p>Compiled against <span class="mono">{esc(STAMP)}</span>. Every component on the page carries a <span class="mono">data-per</span> attribute naming the records it honours; switch on X-ray and hover any outlined component to read them.</p>
    <h3>Templates, dynamics, motion kit</h3><p class="mono">{' · '.join(tops)}</p>
    <h3>Palettes and colour rules</h3><p class="mono">{' · '.join(pals)}</p>
    <h3>Doctrine lenses</h3><p class="mono">{' · '.join(lenses)}</p>
    <h3>Laws honoured</h3><p class="mono">{' · '.join(laws)}</p>
    <h3>Pairs honoured</h3><p class="mono">{' · '.join(pairs)}</p>
    <h3>Anti-pairs swept and resolved</h3><p class="mono">{' · '.join(nopairs)}</p>
    <h3>Entries ({len(d_entries)})</h3><ul class="ids">{ids_li}</ul>
    <h3>Surface plan record</h3><pre>{esc(spfile)}</pre>
    <h3>What Fitz supplies before launch</h3>
    <ul style="margin:0;padding-left:18px;display:grid;gap:4px"><li>Logo (SVG or high-res PNG) for the header slot.</li><li>Photos: hero, two about shots, nine gallery shots at 1600px wide, with a one-line description each for alt text.</li><li>Instagram bio wording for the hero lede.</li><li>Testimonials with name, property type and locality (or a Google Business reviews link).</li><li>Pricing line for the first FAQ, ABN for the footer, and whether thermal drone services stay on the Services page.</li></ul>
  </div>
</dialog>'''

# ---------------------------------------------------------------- page bodies
def home_body():
    hp = S['hero_photo']
    creds_li = ''.join(
        f'<li{" class=note" if i == 7 else ""}><span class="eyebrow">{"Note" if i == 7 else "Credential"}</span><b class="num">{esc(t)}</b><p>{esc(d)}</p></li>'
        for i, (t, d) in enumerate(S['credentials']))
    tiles = ''.join(f'''
    <article class="tile reveal">
      <h3>{esc(t)}</h3><p>{esc(d)}</p>
      <a class="stretch" href="/services#svc-{k}" aria-hidden="true" tabindex="-1"></a>
      <a class="btn btn-secondary" href="/services#svc-{k}">Details<span class="sr"> for {esc(t)}</span></a>
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
    return f'''
<section class="hero wrap"{per("hero")}{per("hero-layout")}>
  <div class="hero-grid">
    <div class="stack" style="--gap:22px">
      <p class="eyebrow"{per("wordmark")}>{esc(S['base'])} · Gippsland · Regional Victoria</p>
      <h1 id="h-home">{esc(S['headline']).replace('&amp;', '&amp;')}</h1>
      <p class="lede"{per("lede")}>{esc(S['lede'])}{lede_flag}</p>
      {cta_row()}
      {contact_line()}
    </div>
    {slot(hp[0], hp[1], hp[2], ar="4/5")}
  </div>
</section>
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
<section class="band"{per("services-grid")}>
  <div class="wrap stack" style="--gap:28px">
    <div class="sec-head reveal"><p class="eyebrow">Services</p><h2>What I'm called out for</h2>
      <p class="measure">Deer and kangaroo work is most of it. The rest is the usual Gippsland list: pigs, foxes, rabbits and wild dogs, night and thermal where it counts.</p></div>
    <div class="grid grid-3">{tiles}</div>
  </div>
</section>
<section class="band alt"{per("howitworks")}>
  <div class="wrap stack" style="--gap:28px">
    <div class="sec-head reveal"><p class="eyebrow">How it works</p><h2>Four steps, no surprises</h2></div>
    <ol class="steps">{steps}</ol>
  </div>
</section>
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
<section class="band alt"{per("testimonials")}>
  <div class="wrap stack" style="--gap:28px">
    <div class="sec-head reveal"><p class="eyebrow">From the paddock</p><h2>What landholders say</h2>{tnote}</div>
    <div class="grid grid-3">{quotes}</div>
  </div>
</section>
<section class="band"{per("area")}>
  <div class="wrap stack" style="--gap:24px">
    <div class="sec-head reveal"><p class="eyebrow">Service area</p><h2>Based in {esc(S['base'])}, working across Gippsland</h2>
      <p class="measure">West, South and Central Gippsland most weeks. East Gippsland and the rest of regional Victoria by arrangement.</p></div>
    <ul class="chips reveal" aria-label="Localities served">{''.join(f'<li>{esc(a)}</li>' for a in S['area'])}</ul>
  </div>
</section>
<section class="band invert"{per("strip")}>
  <div class="wrap stack" style="--gap:20px">
    <h2 style="max-width:16ch">Got deer on the fence line? Get in touch.</h2>
    {cta_row(' style="border-color:var(--foot-line);color:var(--foot-ink)"')}
    <p class="caption">{S['email']} · Instagram {esc(S['instagram_handle'])} · Facebook {esc(S['facebook_label'])}</p>
  </div>
</section>'''

def services_body():
    rows = ''.join(f'''
    <article class="service" id="svc-{k}">
      <div class="stack" style="--gap:8px"><h3 tabindex="-1">{esc(t)}</h3><p class="small" style="color:var(--ink-2)">{esc(d)}</p></div>
      <ul>{''.join(f'<li>{esc(x)}</li>' for x in bullets)}</ul>
    </article>''' for k, t, d, bullets in S['services'])
    drone = '''
      <article class="service" id="svc-drone"><div class="stack" style="--gap:8px"><h3 tabindex="-1">Thermal drone services <span class="flag">optional, remove if not offering yet</span></h3><p class="small" style="color:var(--ink-2)">Thermal drone surveys to count animals, find mobs and map where they move before a program starts.</p></div>
        <ul><li>Pre-program counts</li><li>Finding stock after a storm or fire</li><li>Mapping movement corridors</li></ul></article>''' if S.get('thermal_drone') else ''
    faqs = ''.join(f'<details class="faq"><summary>{esc(q)}</summary><p>{esc(a)}</p></details>' for q, a in S['faq'])
    return f'''
<section class="page" aria-labelledby="h-services"{per("services")}>
  <div class="wrap stack" style="--gap:36px">
    <div class="sec-head"><p class="eyebrow">Services</p><h1 id="h-services" style="font-size:var(--fs-h2)">Pest and vermin control, Gippsland and regional Victoria</h1>
      <p class="measure">Every job is planned, insured and carried out humanely under the relevant Victorian codes of practice. Deer control on farms and kangaroo culling are the two most common call-outs; the rest of the list is below.</p></div>
    <div>{rows}
      <article class="service" id="svc-night"><div class="stack" style="--gap:8px"><h3 tabindex="-1">Night work and thermal</h3><p class="small" style="color:var(--ink-2)">Most feral animals move after dark. Thermal optics let me find them, count them and take them cleanly without lighting up the whole paddock.</p></div>
        <ul><li>Thermal spotting and shooting</li><li>Quiet, planned movements around stock</li><li>Counts you can use for permits and planning</li></ul></article>{drone}
    </div>
    <div class="prose"{per("privacy")}>
      <h3>What a job includes</h3>
      <ul><li>A site visit and a written plan: stock, neighbours, access, dates and safety.</li><li>Humane dispatch to AHCPMG304 and the code for each species.</li><li>Carcass handling and disposal as agreed with you.</li><li>A short report afterwards and a follow-up if the numbers call for it.</li></ul>
      <h3>Permits and codes, in plain language</h3>
      <p class="small" style="color:var(--ink-2)">Kangaroo control on private land needs an Authority to Control Wildlife from the Victorian government; I can help with the application. Deer are a game species and are taken under a Game Licence. All work follows the relevant Victorian codes of practice for the humane control of the species involved.</p>
    </div>
    <div{per("faq")}>{faqs}</div>
    <div class="cta-row"{per("cta")}><a class="btn btn-primary" href="/contact#enquiry">Request a quote</a><a class="btn btn-quiet num" href="tel:{S['phone_e164']}">or call {S['phone_display']}</a></div>
  </div>
</section>'''

def about_body():
    cur = esc(S['credentials_current']) if S.get('credentials_current') else '<span class="flag">month year</span>'
    a1, a2 = S['about_photos']
    return f'''
<section class="page" aria-labelledby="h-about"{per("about")}>
  <div class="wrap">
    <div class="grid" style="gap:40px">
      <div class="prose">
        <p class="eyebrow">About</p>
        <h1 id="h-about" style="font-size:var(--fs-h2)">Based in {esc(S['base'])}, working across Gippsland and regional Victoria</h1>
        <p>{esc(S['name'])} is one operator, licensed and insured, doing feral animal control for farmers and landholders who want the job done properly and the place left as they found it.</p>
        <p>The standard is clean, legal and professional: a plan before the first night, humane dispatch to AHCPMG304, and a short report after. No trophies, no mess, no surprises for the neighbours.</p>
        <p><span class="flag">one or two lines about Fitz to come</span> Years on farms, where the hunting started, why the thermal kit: in his own words, kept short.</p>
        <h3>Credentials</h3>
        <ul class="num">{''.join(f'<li><b>{esc(t)}</b>: {esc(d)}</li>' for t, d in S['credentials'][:7])}</ul>
        <p class="caption">Credentials current as at {cur}. Certificates of currency supplied on request before work starts.</p>
      </div>
      <div class="grid grid-2">{slot(*a1)}{slot(*a2)}</div>
    </div>
  </div>
</section>'''

def gallery_body():
    g = S['gallery']
    items = ''.join(f'''<li><figure style="margin:0"><button type="button" data-lb="{i}" aria-label="Open photo {i+1} of {len(g)}: {esc(c)}">{slot(k, c, src)}</button><figcaption>{esc(c)}</figcaption></figure></li>''' for i, (k, c, src) in enumerate(g))
    return f'''
<section class="page" aria-labelledby="h-gallery"{per("gallery")}>
  <div class="wrap stack" style="--gap:28px">
    <div class="sec-head"><p class="eyebrow">Gallery</p><h1 id="h-gallery" style="font-size:var(--fs-h2)">From the job</h1>
      <p class="measure">Thermal images, night work, property damage and gear. No property locations are shown and nobody's face appears without their say-so.</p></div>
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
    return f'''
<section class="page" aria-labelledby="h-contact">
  <div class="wrap contact-grid">
    <div class="stack" style="--gap:28px">
      <div class="sec-head" style="margin:0"><p class="eyebrow">Contact</p><h1 id="h-contact" style="font-size:var(--fs-h2)">Ring, email or send the form</h1>
        <p class="measure">Phone is quickest. If I'm out on a job I'll ring back the same day where I can.</p></div>
      <div class="contact-list"{per("contactline")}>
        <div class="kv"><b>{ico("i-phone")}Phone</b><div class="row"><span class="num" id="c-phone">{S['phone_display']}</span><button type="button" class="copy" data-copy="{S['phone_display']}" aria-label="Copy phone number">Copy</button><a class="btn btn-secondary" href="tel:{S['phone_e164']}">Call</a></div></div>
        <div class="kv"><b>{ico("i-mail")}Email</b><div class="row"><span id="c-email" style="font-size:19px">{S['email']}</span><button type="button" class="copy" data-copy="{S['email']}" aria-label="Copy email address">Copy</button></div></div>
        <div class="kv"><b>{ico("i-pin")}Based in</b><div class="row"><span style="font-size:19px">{esc(S['base'])}, Gippsland VIC</span></div></div>
        <div class="kv"{per("socials")}><b>Follow the work</b><div class="socials"><a href="{S['instagram']}" target="_blank" rel="noopener">Instagram {esc(S['instagram_handle'])} {ico("i-ext")}</a><a href="{S['facebook']}" target="_blank" rel="noopener">Facebook · {esc(S['facebook_label'])} {ico("i-ext")} <span class="flag">confirm page URL</span></a></div></div>
      </div>
    </div>
    <div>
      <form class="form" id="enquiry" action="/api/enquiry" method="post"{per("form")} aria-describedby="form-note">
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
        <p class="note">Mockup: enquiries sent here are received by the site's server function and emailed to {S['email']} once the mail key is configured; until then they are logged for testing. Without script the plain form still submits.</p>
      </form>
      <div class="confirm" id="confirm" role="status" tabindex="-1" hidden{per("confirm")}>
        <b>Enquiry received</b>
        <p>Thanks, <span id="confirm-name">there</span>. Fitz will ring the number you gave, usually within two business days.</p>
        <p class="small" style="color:var(--ink-2)"><b style="font-weight:600;color:var(--ink)">What happens next:</b> a quick phone chat about the property and the animals, then a site visit if it's a fit. If it's urgent, call <a class="num" href="tel:{S['phone_e164']}">{S['phone_display']}</a>.</p>
        <p class="small"><a href="/contact#enquiry" id="confirm-reset">Send another enquiry</a></p>
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
  /* form: progressive enhancement over the native form (posts to /api/enquiry without script) */
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
    form.addEventListener('submit',function(e){
      e.preventDefault();
      var errs=[];
      fields.forEach(function(f){ var el=document.getElementById(f[0]); var ok=f[2](el); mark(el,f[1],ok); if(!ok) errs.push([f[0],document.getElementById(f[1]).textContent]); });
      var anyHelp=form.querySelectorAll('input[name="help"]:checked').length>0; var hf=document.getElementById('f-help'); hf.classList.toggle('has-err',!anyHelp); if(!anyHelp) errs.push(['f-help',document.getElementById('e-help').textContent]);
      if(errs.length){ showErrors(errs); return; }
      sum.hidden=true;
      var btn=document.getElementById('f-submit'); btn.style.width=btn.getBoundingClientRect().width+'px'; btn.classList.add('is-busy'); btn.setAttribute('aria-disabled','true'); btn.disabled=true; btn.querySelector('.lbl').textContent='Sending';
      var fd=new FormData(form), payload={}; fd.forEach(function(v,k){ if(k==='help'){ (payload.help=payload.help||[]).push(v);} else payload[k]=v; });
      function reset(){ btn.classList.remove('is-busy'); btn.disabled=false; btn.removeAttribute('aria-disabled'); btn.style.width=''; btn.querySelector('.lbl').textContent='Send enquiry'; }
      fetch(form.action,{method:'POST',headers:{'Content-Type':'application/json','Accept':'application/json'},body:JSON.stringify(payload)})
        .then(function(r){ return r.json().then(function(j){ return {ok:r.ok && j.ok, j:j}; }); })
        .then(function(res){
          reset();
          if(!res.ok){ showErrors([['f-submit', (res.j && res.j.error) || 'The enquiry could not be sent. Ring '+document.getElementById('c-phone').textContent+' instead.']]); return; }
          var c=document.getElementById('confirm'); document.getElementById('confirm-name').textContent=document.getElementById('f-name').value.trim().split(' ')[0]||'there';
          form.hidden=true; c.hidden=false; c.focus(); try{localStorage.removeItem(KEY)}catch(e){}
        })
        .catch(function(){ reset(); showErrors([['f-submit','No connection. The enquiry was not sent; ring '+document.getElementById('c-phone').textContent+' instead.']]); });
    });
    document.getElementById('confirm-reset').addEventListener('click',function(e){ e.preventDefault(); form.reset(); document.getElementById('confirm').hidden=true; form.hidden=false; document.getElementById('f-name').focus(); });
  }
  /* reviewer chrome */
  var vb=document.getElementById('varbar'), tm=document.getElementById('t-motion'), tx=document.getElementById('t-xray'), ts=document.getElementById('t-spec'), th=document.getElementById('t-hide'), spec=document.getElementById('spec');
  try{ if(localStorage.getItem('ffh-varbar')==='hidden') vb.hidden=true; }catch(e){}
  th.addEventListener('click',function(){ vb.hidden=true; try{localStorage.setItem('ffh-varbar','hidden')}catch(e){} });
  tm.addEventListener('click',function(){ var off=root.getAttribute('data-motion')==='off'; if(off){root.removeAttribute('data-motion');tm.querySelector('.long').textContent='Motion: on';tm.setAttribute('aria-pressed','false')} else {root.setAttribute('data-motion','off');tm.querySelector('.long').textContent='Motion: off (reduced-motion twin)';tm.setAttribute('aria-pressed','true')} });
  var NAMES=%%NAMES%%;
  tx.addEventListener('click',function(){ var on=root.hasAttribute('data-xray'); if(on){root.removeAttribute('data-xray');tx.setAttribute('aria-pressed','false');[].forEach.call(document.querySelectorAll('[data-per]'),function(el){el.removeAttribute('title')})} else {root.setAttribute('data-xray','');tx.setAttribute('aria-pressed','true');[].forEach.call(document.querySelectorAll('[data-per]'),function(el){el.setAttribute('title',el.getAttribute('data-per').split(' ').map(function(i){return i+' '+(NAMES[i]||'')}).join('\n'))})} });
  if(!('commandForElement' in HTMLButtonElement.prototype)){ ts.addEventListener('click',function(){ if(!spec.open) spec.showModal(); }); }
  document.getElementById('spec-close').addEventListener('click',function(){ spec.close(); });
  spec.addEventListener('click',function(e){ if(e.target===spec) spec.close(); });
})();
</script>"""

def document(key, body, title, desc):
    path = HREF.get(key, '/404')
    canonical = S['url'].rstrip('/') + ('' if path == '/' else path)
    robots = '' if S.get('indexable') else '<meta name="robots" content="noindex, nofollow">\n'
    jsonld = {
      "@context": "https://schema.org", "@type": "LocalBusiness", "name": S['name'],
      "description": TITLES['home'][1], "telephone": S['phone_e164'], "email": S['email'], "url": S['url'].rstrip('/') + '/',
      "image": S['url'].rstrip('/') + '/og-1200x630.png',
      "address": {"@type": "PostalAddress", "addressLocality": S['base'], "addressRegion": "VIC", "addressCountry": "AU"},
      "areaServed": ["Gippsland", "Regional Victoria"], "sameAs": [S['instagram']],
      "knowsAbout": ["Deer control", "Kangaroo culling", "Feral pig control", "Fox control", "Rabbit control", "Wild dog control", "Thermal night work"],
    }
    caps = json.dumps([c for _, c, _ in S['gallery']])
    names = json.dumps(NAMES, ensure_ascii=False)
    return f'''<!doctype html>
<html lang="en-AU">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
{robots}<meta name="theme-color" content="#f8f6f2">
<link rel="canonical" href="{canonical}">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{esc(S['name'])}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{S['url'].rstrip('/')}/og-1200x630.png">
<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600;700&family=Barlow:wght@400;500;600&display=swap">
<style>{css}</style>
<script type="application/ld+json">{json.dumps(jsonld, ensure_ascii=False)}</script>
</head>
<body>
{SPRITE}{varbar()}{header(key)}
<main id="main"{per("doc")}{per("tokens")}{per("type")}{per("motion")}{per("focus")}{per("ground")}>
{body}
</main>
{footer()}{ctabar()}{spec_dialog()}{SCRIPT.replace('%%CAPS%%', caps).replace('%%NAMES%%', names)}
</body>
</html>'''

FAVICON = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="8" fill="#2E6E4E"/><path d="M18 14h30v9H28v9h17v9H28v9H18z" fill="#f8f6f2"/></svg>'''

def main():
    PUB.mkdir(exist_ok=True)
    pages = {
      'home': home_body(), 'services': services_body(), 'about': about_body(), 'gallery': gallery_body(), 'contact': contact_body(),
    }
    for key, body in pages.items():
        t, d = TITLES[key]
        fn = 'index.html' if key == 'home' else f'{key}.html'
        (PUB / fn).write_text(document(key, body, t, d))
    (PUB / '404.html').write_text(document('404', notfound_body(), f"Page not found · {S['name']}", "That page isn't here."))
    (PUB / 'favicon.svg').write_text(FAVICON)
    base = S['url'].rstrip('/')
    today = datetime.date.today().isoformat()
    (PUB / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
        ''.join(f'  <url><loc>{base}{"" if h == "/" else h}</loc><lastmod>{today}</lastmod></url>\n' for _, h, _ in PAGES) + '</urlset>\n')
    (PUB / 'robots.txt').write_text(('User-agent: *\nAllow: /\n' if S.get('indexable') else 'User-agent: *\nDisallow: /\n') + f'Sitemap: {base}/sitemap.xml\n')
    allids = set()
    for grp in (cites.SHARED, X, cites.TOP):
        for ids in grp.values(): allids.update(ids)
    print(f'built {len(pages)+1} pages into public/ · {len([i for i in allids if re.match(r"^D\d{4}$", i)])} entries · {len(allids)} citations')

if __name__ == '__main__':
    main()
