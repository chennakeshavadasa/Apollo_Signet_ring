# Apollo Signet Ring

A Roman-style gold signet ring set with a carnelian carrying a laureate head of Apollo, ready for 3D printing.
Ring size US 9 (inner diameter 18.95 mm); the generator in `source/` makes other sizes.

**[Open the interactive 3D viewer](https://chennakeshavadasa.github.io/Apollo_Signet_ring/viewer/apollo_signet_viewer.html)** (turn, zoom, preset views; nothing to install)

Website: [chennakeshavadasa.github.io/Apollo_Signet_ring](https://chennakeshavadasa.github.io/Apollo_Signet_ring/)

<p align="center"><img src="images/render_three_quarter.png" width="640" alt="Apollo signet ring, three-quarter view"></p>
<p align="center">
  <img src="images/render_top.png" width="420" alt="Bezel face">
  <img src="images/render_portrait_closeup.png" width="420" alt="Portrait close-up">
</p>

## Which file do I print?

All print files are in [`print/`](https://github.com/chennakeshavadasa/Apollo_Signet_ring/tree/main/print), in millimetres. Pick **one** of the three folders:

| Your printer / goal | Print | Notes |
|---|---|---|
| **Multi-colour FDM printer** (Bambu AMS, Prusa MMU, ...) | [`print/multi-colour/apollo_signet_2colour.3mf`](print/multi-colour/apollo_signet_2colour.3mf) | One file with the gold body and the red stone already assembled. If the slicer does not assign the filaments by itself, give `ring_body_gold` the gold filament and `apollo_stone_red` the red one. |
| **Resin (MSLA) printer**, or any single-colour printer (Ender 3 etc.) when you want two colours | [`print/two-part/ring_body_gold.stl`](print/two-part/ring_body_gold.stl) **and** [`print/two-part/apollo_stone_red.stl`](print/two-part/apollo_stone_red.stl) | Print the body in gold/yellow and the stone in red, then glue the stone into its seat. Gives the sharpest portrait. |
| **One colour only**, or a pattern for **lost-wax casting** in metal | [`print/one-piece/ring_one_piece.stl`](print/one-piece/ring_one_piece.stl) | Body and stone fused into one solid; the fitting gap is closed. |

**Best result:** a resin printer with the two-part STLs. The portrait has detail down to about 0.05 mm (eye, lips, laurel veins).

### Printing tips

- Print a quick test of the ring body first to confirm the finger size.
- **Stone:** print it flat side down; it needs no supports. On FDM use a 0.2 mm nozzle and 0.04-0.08 mm layers (a 0.4 mm nozzle softens the face).
- **Ring body:** put the supports on the inside of the band and under the bezel; keep them off the top of the bezel and the collet.
- **Fit:** the seat has 0.10 mm clearance all round. If the stone is tight, scale it to 99 % in X and Y; if it is loose, a drop of CA glue holds it.

### Ender 3 and other single-nozzle FDM printers

The Ender 3 prints one colour at a time, so use the STL files:

- **Gold ring with a red stone:** print [`print/two-part/ring_body_gold.stl`](print/two-part/ring_body_gold.stl) in gold or yellow filament and [`print/two-part/apollo_stone_red.stl`](print/two-part/apollo_stone_red.stl) in red, then glue the stone into its seat.
- **One colour:** print [`print/one-piece/ring_one_piece.stl`](print/one-piece/ring_one_piece.stl).
- Skip the 3MF: it opens in Cura, but with one nozzle both parts come out in the same filament.

Open the STLs in Cura, Creality Print, PrusaSlicer or OrcaSlicer. They are in millimetres and load at the right size (about 24 x 17 x 25 mm) with no scaling.

| Setting | Recommendation |
|---|---|
| Nozzle | The stock 0.4 mm nozzle works but blurs the curls, laurel leaves and facial features; a 0.2 mm nozzle is much better for the stone |
| Layer height | Multiples of 0.04 mm on the Ender 3: 0.04 mm for the stone (the relief is only 0.9 mm tall), 0.08 mm for the ring body |
| Stone | Flat side down, no supports. Print slowly with full part cooling, or print two stones at once so each layer has time to cool |
| Ring body | As it loads, stone seat on top, with tree supports. They touch the inside of the band and the underside (sand those); the top of the bezel stays clean |
| Fit | If the stone is tight, scale it to 98-99 % in X and Y. Print the ring body first to check the finger size |
| Material | PLA for a test or display piece; PETG for a ring you will wear (a thin PLA band can crack) |

An Ender 3 gives a recognisable laurel-crowned head, but some fine detail is lost and small layer steps may show on the face.
For a crisp portrait, have only the stone printed in resin (a print service is fine) and print the ring body on the Ender 3.

## View it in 3D

**Online:** [https://chennakeshavadasa.github.io/Apollo_Signet_ring/viewer/apollo_signet_viewer.html](https://chennakeshavadasa.github.io/Apollo_Signet_ring/viewer/apollo_signet_viewer.html)
(GitHub Pages, published from `main`; it updates by itself a minute after each push).

**Offline:** download [`viewer/apollo_signet_viewer.html`](viewer/apollo_signet_viewer.html) and double-click it; it is a single file that opens in any browser.

Drag to turn, scroll or pinch to zoom, and use the buttons for the preset views, a turntable and **Lift stone** (shows the seat).

[`viewer/apollo_signet_coloured.glb`](viewer/apollo_signet_coloured.glb) is the full-resolution coloured model for Blender, Windows 3D Viewer and other 3D programs.

## Design

The gold body follows the Roman gold gem-set signet rings of the 1st-2nd century AD (Henig types II/III):

- a D-section hoop, flat inside (no modern comfort fit), slender at the back and swelling into broad shoulders;
- a flat oval bezel with a stepped collet round the stone;
- the carnelian stands proud of the gold, as on Roman signets, where the gem face is the top of the ring.

### Measurements (mm)

| | |
|---|---|
| Bezel plate | 14.4 x 17.6 |
| Collet | 13.1 x 16.3 |
| Stone | 11.4 x 14.6 |
| Stone seat | 11.6 x 14.8, 0.70 deep, 0.10 clearance all round |
| Hoop | 1.8 thick x 2.8 wide at the back; 3.1 x 11.5 at the shoulders |
| Stone face | 0.35 above the gold |
| Portrait relief | 0.90; its top is 1.25 above the gold |
| Height above the finger | 2.7 (gold), 3.95 (with the stone) |

### Casting in metal

Solid body volume 1,129 mm³: about 17 g in 18k gold, 15 g in 14k gold, 12 g in sterling silver.
The stone can be cast in red resin or glass, or carved in real carnelian from the height map in [`portrait/`](https://github.com/chennakeshavadasa/Apollo_Signet_ring/tree/main/portrait).

## Make another ring size

```bash
pip install -r source/requirements.txt
python3 source/build_ring.py --us-size 10 --out out
cd source/viewer-build && npm install && node build.mjs ../../out/build/viewer_payload ../../out/viewer/apollo_signet_viewer.html
```

`out/` then has the same `print/` and `viewer/` folders as this repository (`--out .` refreshes the repository's own files).

## Repository layout

```
print/
  multi-colour/   apollo_signet_2colour.3mf                    multi-colour FDM printers
  two-part/       ring_body_gold.stl, apollo_stone_red.stl     resin or single-colour printers, two colours
  one-piece/      ring_one_piece.stl                           one colour, lost-wax casting
viewer/           apollo_signet_viewer.html (3D view in the browser), apollo_signet_coloured.glb
images/           renders from the viewer
portrait/         Apollo portrait height map: 16-bit PNG (white = highest) and the .npy the generator reads
source/
  build_ring.py   ring generator (writes print/, viewer/*.glb and the viewer payload)
  requirements.txt
  viewer-build/   builds viewer/apollo_signet_viewer.html (three.js, esbuild)
```
