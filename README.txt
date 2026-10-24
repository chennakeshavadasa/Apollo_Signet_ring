APOLLO SIGNET RING - ROMAN TYPE - PRINT FILES
All dimensions in millimetres. Ring size US 9 (inner diameter 18.95 mm).

DESIGN
  The gold body follows the Roman gold gem-set signet rings of the 1st-2nd
  century AD (Henig types II/III):
  - hoop of D section with a flat inner surface (no modern comfort fit),
    slender at the back (1.8 thick x 2.8 wide) and swelling into broad
    shoulders (3.1 thick x 11.5 wide)
  - flat oval bezel plate with a stepped collet round the stone
  - the carnelian stands proud of the gold, as on Roman signets, where the gem
    face is the top of the ring so that it can be pressed into wax.
  The Apollo portrait is unchanged.

FILES
  apollo_signet_viewer.html         Interactive 3D view. Open it in any browser
                                    (works offline): drag to turn, scroll or pinch
                                    to zoom; buttons for the standard views, a
                                    turntable and "lift stone" to show the seat.
  apollo_signet_2colour.3mf         Gold body + red stone, assembled, colours assigned.
                                    For multi-material printers (Bambu AMS, Prusa MMU).
  ring_body_gold.stl                Gold body with the oval stone seat (0.70 mm deep).
  apollo_stone_red.stl              Red stone insert with the Apollo portrait.
                                    Print flat side down; it needs no supports.
  ring_one_piece.stl                Body and stone fused (fitting gap closed), for
                                    single-colour resin printing or lost-wax casting.
  apollo_signet_coloured.glb        Full-resolution coloured model for viewing/rendering.
  render_top.png, render_portrait_closeup.png, render_three_quarter.png
                                    Views from the 3D viewer.
  apollo_portrait_heightmap_16bit.png  The portrait relief as a 16-bit height map
                                    (white = highest), for CNC engraving or reuse.
  build_ring.py + portrait_height.npy  Generator, to make another ring size:
      python3 build_ring.py --us-size 10 --height portrait_height.npy \
              --img-scale 1.09 --relief 0.9 --out out
      (needs: numpy scipy scikit-image trimesh manifold3d fast-simplification)
  viewer/                           Builds the HTML viewer from the generator output:
      cd viewer && npm install && node build.mjs ../out/viewer_payload ../apollo_signet_viewer.html

MEASUREMENTS
  Bezel plate               14.4 x 17.6 mm      Collet   13.1 x 16.3 mm
  Stone                     11.4 x 14.6 mm      Seat     11.6 x 14.8 mm, 0.70 deep
  Hoop                      1.8 x 2.8 mm at the back, 3.1 x 11.5 mm at the shoulders
  Stone face                0.35 mm above the gold
  Portrait                  0.90 mm relief, its top 1.25 mm above the gold
  Height above the finger   gold 2.7 mm, with the stone 3.95 mm
  Stone fit                 0.10 mm clearance all round

PRINTING
  - A resin (MSLA) printer gives the best result: the face has detail down to
    about 0.05 mm (eye, lips, laurel veins).
  - FDM: use a 0.2 mm nozzle and 0.06-0.08 mm layers for the stone. A 0.4 mm
    nozzle will soften the face.
  - If the stone is tight in the seat on your printer, scale it to 99% in X and Y.
    If it is loose, a drop of CA glue holds it.
  - Print a quick test of the ring body first to confirm the finger size.

CASTING IN GOLD
  Solid body volume 1,129 mm3: about 17 g in 18k gold, 15 g in 14k, 12 g in
  sterling silver. The stone can be cast in red resin or glass, or carved in
  real carnelian from the height map.
