# paddock1 — Fitz Feral Hunters, Paddock composition

Static site for a Gippsland pest and vermin control business, compiled from the D700 design catalogue
(surface plans **SP-01 PADDOCK** and its v2 delta **SP-01b** — the topographic sheet layer: TP04 The Calm Commerce Front on DY01 Calm interface, PAL Noma Forest Season
with the Forest Institutional green as the one action colour, motion kit MK-01). Every component carries a
`data-per` attribute naming the catalogue records it honours; the **Spec sheet** button on the site lists them.

## Layout

```
content/site.json   ← the only file to edit for contact details, credentials, services, FAQ, localities, photos
src/build.py        ← generator: python3 src/build.py  → writes public/
src/css.py          ← stylesheet (tokens at the top)
src/topo.py         ← seeded contour tile (periodic noise + marching squares) and MGA zone 55 grid references
src/cites.py        ← catalogue citations per component
public/             ← the deployed site (generated, committed so Vercel needs no build step)
api/enquiry.js      ← Vercel function behind the contact form
docs/               ← SP-01 / SP-01b / SP-01c records, probe verdicts, FOLD lines
public/brand/       ← logo lockup (keyed PNG for dark bands, JPG plate), rifle mark, the card as supplied
```

## Editing content

1. Change `content/site.json`.
2. Run `python3 src/build.py` (Python 3.10+, no dependencies).
3. Commit and push. Vercel redeploys on every push to `main`.

Photos: drop files into `public/photos/` and put the path (e.g. `/photos/hero.jpg`) as the third value of a
gallery/hero/about entry in `site.json`. Empty string keeps the labelled placeholder slot.

Testimonials: add `["quote", "Name · property type · locality"]` pairs to `testimonials`; the empty-state
cards disappear once there is at least one.

Launch switches: set `"indexable": true` (removes `noindex` and opens `robots.txt`), fill `abn`,
`credentials_current`, and remove `lede_flag` once the Instagram wording is in.

## Contact form

`POST /api/enquiry` accepts JSON (enhanced form) or form-encoded (no-JS fallback) and validates server-side.
Set these environment variables in the Vercel project to email enquiries:

| Variable | Purpose |
|---|---|
| `RESEND_API_KEY` | Resend API key. Without it, enquiries are logged to the function logs only. |
| `ENQUIRY_TO` | Recipient (defaults to fitzferalhunters1@gmail.com). |
| `ENQUIRY_FROM` | Verified sender, e.g. `Fitz Feral Hunters <enquiries@fitzferalhunters.com.au>`. |

## Verification

`docs/verdicts-both.txt` holds the CAP-24 probe run (65/65 VERIFIED) for the artifact build. To re-probe this
build locally: `node probe.js` from the design workspace against `public/`.

Compiled against STAMP :: D700 · 4 Oct 2026 · 6511 entries D0001-D6558 · 218 laws · 387 capsules · 466 groups · 1824 pairs · 499 anti-pairs · 457 palettes · 21 lenses
