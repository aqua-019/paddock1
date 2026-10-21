# SP-01d · Fitz Feral Hunters · PADDOCK v0.3.1 — sheet layer off, map out, all of Victoria, the drone (diff-mode SP, D700 §0D)

Compiled against: STAMP :: D700 · 4 Oct 2026 · 6511 entries D0001-D6558 · 218 laws · 387 capsules · 466 groups · 1824 pairs · 499 anti-pairs · 457 palettes · 21 lenses
Client feedback on v0.3 (via Aqua): "get rid of the map … advertise that I'm covering all of Victoria, not just Gippsland"; Aqua: remove the topography effect added in v0.2. Also: more credentials to come; a DJI Matrice 4T thermal drone to advertise for scouting and night work.
Lenses: LENS-03 (Useful First) and LENS-04 return to the lead — the sheet layer was the designer's complexity, and the client has said so; LENS-14 keeps Warragul as the base and the card as the one reference; LENS-13 gets its single moment back as the drone band (one dark feature band on the home page, the card's own colours). TENSION-03: delight on the rare moment (the new capability), plain everywhere else.

Delta: `sheet_layer: false` in content/site.json removes the contour field, grid, sheet meta lines, scale bars, grid references, locality map, map key and footer datum line (the generator keeps them behind the flag; nothing else from v0.2 — marginalia, photo frames, ledger, figure numbers — changes). Coverage copy, titles, JSON-LD areaServed and the service-area section now say Victoria, with Gippsland named as home ground and regions as chips. Thermal drone scouting is a confirmed service (Services page section, no "optional" flag) and a feature band on Home naming the aircraft. The credentials wall carries a "more to come" flag.

SP-01d :: Fitz Feral Hunters :: SURFACES=all (delta only) :: CITES=SP-01 + SP-01c minus the SHEET_KEYS set (D2410, D0041, D1851, D1856, D3077, D3359, D6468, D0436 for the map) plus D5303 (Inverse-pair section theming) · D0059 (Split-screen layout) · D0297 (Section-end CTA rhythm) · D3399 (Interactive accent twin) · D0141 (All-caps eyebrow kickers) · LENS-03 · LENS-13 :: FLOOR=unchanged + 8 delta asserts

## ASSERT lines (delta)
ASSERT :: all :: body::after carries no background-image; no element references topo-tile.svg; public/topo-tile.svg is not written :: PER=LENS-03 · LENS-04 · client instruction
ASSERT :: home :: no .map, .legend, .scalebar, .meta or .datum element renders; dividers are a label on a hairline :: PER=LENS-03 · client instruction
ASSERT :: all :: "Victoria" appears in the home title, meta description, hero eyebrow, service-area h2, services h1, about h1 and JSON-LD areaServed; Warragul, Gippsland stays as the base in the eyebrow, contact and footer :: PER=LENS-14 · D1749 (Structured data markup)
ASSERT :: home :: service-area chips are 12 Victorian regions with no grid references :: PER=D2124 (Wayfinding scent labels) · LENS-14
ASSERT :: home :: exactly one dark feature band between the services grid and how-it-works, naming the DJI Matrice 4T, with the gold button twin and a photo slot :: PER=D5303 · D0059 · D3399 · LENS-13 · LAW-15
ASSERT :: services :: #svc-drone is present, names the aircraft, and carries no "optional" flag :: PER=LENS-02
ASSERT :: home :: the credentials wall carries a visible "more credentials to come" flag :: PER=LENS-02 · D0374 (Empty-slot ghost card)
ASSERT :: all :: hover census, contrast pairs, body size, mobile overflow and reduced-motion results unchanged from SP-01c :: PER=D3171 · D0192 · D3193 · D3453

MEASURE :: probe rounds=1 · pass rate=10/10 · rig: Playwright Chromium against a local http serve of public/
