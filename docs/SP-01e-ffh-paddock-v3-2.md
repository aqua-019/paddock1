# SP-01e · Fitz Feral Hunters · PADDOCK v0.3.2 — the dense sheet, no map (diff-mode SP, D700 §0D)

Compiled against: STAMP :: D700 · 4 Oct 2026 · 6511 entries D0001-D6558 · 218 laws · 387 capsules · 466 groups · 1824 pairs · 499 anti-pairs · 457 palettes · 21 lenses
Correction to v0.3.1: Aqua keeps the topographic background ("great") and wants it denser — more lines per pixel, more area visually covered. Only the locality map goes, as the client asked. Everything else in v0.3.1 (all-of-Victoria copy, the drone band, the credentials flag) stands.
Lenses: LENS-12 back in the lead for the ground, within LENS-04's rule for text and controls; LENS-14 unchanged.

Delta: `sheet_layer: true`, `sheet_map: false`. `--ink-2` firmed from a 72% to an 80% ink mix (5.97:1 → 7.7:1 on cream): the v0.3 colourway had let secondary text slip under the v0.2 floor, and a busier ground is exactly where it must hold. The same seeded 1200px tile is drawn at 600px (`TOPO_SCALE = 0.5`) with 29 levels instead of 19 (interval 1/30), strokes 1.3/2.2 px in tile units (0.65/1.1 px on screen), stroke-opacity .11 minor / .17 index. Measured line density rises from 58 to ≈175 px of contour per 1,000 px² (3.0×). Sheet meta lines, scale-bar dividers, the base grid reference and the footer datum line return with the sheet; the locality map and key stay off behind `sheet_map`.

SP-01e :: Fitz Feral Hunters :: SURFACES=all (delta only) :: CITES=SP-01c set (sheet keys restored) minus the map keys (D0436-as-map, D0191-as-map, D3780-as-legend) plus LENS-12 :: FLOOR=unchanged + 6 delta asserts

## ASSERT lines (delta)
ASSERT :: all :: body::after carries the tile at background-size 600px (mobile 450px); the tile file is written and ≤ 135 KB (gzip ≈ 50 KB) :: PER=D2410 (Contour isoline plot) · D4987 (Carbon-Aware Interface Budget)
ASSERT :: all :: contour density ≥ 3× v0.2 (≥ 170 px of line per 1,000 px² at the drawn scale) :: PER=D2410 · LENS-12
ASSERT :: all :: contour strokes are ink #1b2622 at .11 / .17 alpha; no stroke on the layer exceeds .17 :: PER=D3006 (Alpha-tint border tokens) · LENS-04
ASSERT :: all :: token contrast on the field: body ≥ 12:1, ink-2 ≥ 7:1 against the solid ground; the field never sits under a control :: PER=D0192 (APCA contrast pairing) · LENS-15
ASSERT :: home :: no .map or .legend renders; sheet meta, scale bars and the footer datum line do :: PER=client instruction · D0041 (Blueprint / schematic)
ASSERT :: all :: seed and geometry unchanged: three builds hash identically :: PER=D1851 (Seeded PRNG) · LAW-10

MEASURE :: probe rounds=2 (round 1: 1 FAILED — ink-2 5.97:1 inherited from v0.3; token firmed to 80%) · final 9/9 VERIFIED (docs/verdicts-v3-2.txt) · SP-01c re-run 11/12, the one miss being the superseded .075/.12 alpha claim · density 175 px/1000px² (3.0× v0.2) · tile 129 KB raw / 51 KB gz · index.html 102 KB · rig: Playwright Chromium against public/

FOLD :: D2410 → density is set by interval and drawn scale together; halving the drawn tile doubles lines per pixel at no file cost, so go there before adding levels (29 levels at 600px = 3.0×, 129 KB; 38 levels = 185 KB for little more) :: Fitz Feral Hunters v0.3.2
FOLD :: D3006 · LENS-04 → when a decorative field gets denser, re-measure the secondary ink against the solid ground, not the field; the floor that slips is usually a token changed for another reason (the colourway), not the field :: Fitz Feral Hunters v0.3.2
FOLD :: client feedback → "the map should go" and "the topography is great" were one message about two layers; keep ornament layers behind separate switches (sheet_layer / sheet_map) so a yes to one is not a no to the other :: Fitz Feral Hunters v0.3.2
