APOLLO SIGNET RING - PRINT FILES
All dimensions in millimetres. Ring size US 9 (inner diameter 18.95 mm).

FILES
  apollo_signet_2colour.3mf         Gold body + red stone, assembled, colours assigned.
                                    For multi-material printers (Bambu AMS, Prusa MMU).
  ring_body_gold.stl                Gold mount with the oval stone seat (1.6 mm deep).
  apollo_stone_red.stl              Red stone insert with the Apollo portrait.
                                    Print flat side down; it needs no supports.
  ring_one_piece.stl                Body and stone fused, for single-colour resin
                                    printing or lost-wax casting.
  apollo_signet_coloured.glb        Full-resolution coloured model for viewing/rendering.
  apollo_portrait_heightmap_16bit.png  The portrait relief as a 16-bit height map
                                    (white = highest), for CNC engraving or reuse.
  build_ring.py + portrait_height.npy  Generator, to make another ring size:
      python3 build_ring.py --us-size 10 --height portrait_height.npy \
              --img-scale 1.09 --relief 0.9 --out out
      (needs: numpy scipy scikit-image trimesh manifold3d fast-simplification)

MEASUREMENTS
  Table (top of the ring)   17.4 x 14.2 mm      Stone   14.6 x 11.4 mm
  Shank                     2.3 mm at the base, 4.4 mm at the shoulders
  Portrait relief           0.90 mm above the stone field
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
  Solid body volume 2,139 mm3: about 33 g in 18k gold, 28 g in 14k, 22 g in
  sterling silver. A jeweller would normally hollow the underside of the table
  to save metal. The stone can be cast in red resin or glass, or carved in real
  carnelian from the height map.
