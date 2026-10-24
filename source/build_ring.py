#!/usr/bin/env python3
"""
Apollo signet ring generator, Roman type  (all dimensions in mm)
-----------------------------------------------------------------
Builds a watertight, two-part finger ring in the form of the Roman gold gem-set
signet rings of the 1st-2nd century AD (Henig types II/III):
  * ring body  (gold)  - hoop of D section, narrow at the back and swelling towards the
                          shoulders; flat inner surface (no modern comfort fit); flat oval
                          bezel plate with a stepped collet around the stone
  * stone insert (red) - oval carnelian with the Apollo portrait in raised relief.  The
                          stone stands proud of the collet, so the portrait is the top of
                          the ring (as on Roman rings, where the gem face sits at or above
                          the gold so that it can be pressed into wax)
and exports printable STL / 3MF, a coloured GLB and the payload for the HTML viewer.

Usage:  python3 source/build_ring.py --us-size 9 --out out
Writes, under --out (use --out . to refresh this repository in place):
  print/multi-colour/apollo_signet_2colour.3mf
  print/two-part/ring_body_gold.stl, print/two-part/apollo_stone_red.stl
  print/one-piece/ring_one_piece.stl
  viewer/apollo_signet_coloured.glb
  build/viewer_payload/ (input of source/viewer-build/build.mjs), build/specs.json
"""
import argparse, json, os, zipfile
import numpy as np
import trimesh
from scipy import ndimage as ndi
from skimage import measure

# ---------------------------------------------------------------- parameters
ap = argparse.ArgumentParser()
ap.add_argument('--us-size', type=float, default=9.0)
ap.add_argument('--height', default=os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'portrait', 'portrait_height.npy'))
ap.add_argument('--out', default='out')
ap.add_argument('--img-scale', type=float, default=1.09)
ap.add_argument('--nt', type=int, default=1800)
ap.add_argument('--nr', type=int, default=330)
ap.add_argument('--voxel', type=float, default=0.05)
ap.add_argument('--body-faces', type=int, default=500_000, help='face budget of the body mesh')
ap.add_argument('--relief', type=float, default=0.9, help='max relief height above stone field')
args = ap.parse_args()

inner_d = 11.63 + 0.8128 * args.us_size          # US ring size -> inner diameter
R_in = inner_d / 2
P_MC, P_TWO, P_ONE = f'{args.out}/print/multi-colour', f'{args.out}/print/two-part', f'{args.out}/print/one-piece'
P_VIEW, P_BUILD = f'{args.out}/viewer', f'{args.out}/build'
for d in (P_MC, P_TWO, P_ONE, P_VIEW, P_BUILD):
    os.makedirs(d, exist_ok=True)

# stone (the Apollo insert, unchanged): oval 11.4 x 14.6 mm, long axis along the finger (Y)
clear = 0.10                    # radial clearance stone <-> seat
Px, Py = 5.80, 7.40             # seat (pocket) semi-axes
sx, sy = Px - clear, Py - clear # stone semi-axes
st_wall = 0.75                  # stone side wall: base -> start of the rounded bevel
st_field = 1.05                 # flat field of the stone above its base (bevel = 0.30)

# Roman body
T_back, T_sh = 1.8, 3.1         # hoop radial thickness: back / shoulders
W_back, W_sh = 2.8, 11.5        # hoop width along the finger: back / shoulders
h_seat = 2.0                    # solid gold under the stone
z_seat = R_in + h_seat          # floor of the stone seat
seat_depth = 0.70               # collet top above the seat (< st_wall: the stone stands proud)
z_col = z_seat + seat_depth     # top of the collet = top of the gold
col_w = 0.75                    # collet wall thickness
step_w, step_h = 0.65, 0.45     # flat step of the bezel plate around the collet
z_plat = z_col - step_h         # top of the bezel plate
plate_t = 1.3                   # bezel plate thickness at its overhanging ends
Cx, Cy = Px + col_w, Py + col_w
Bx, By = Cx + step_w, Cy + step_w


def smin(a, b, k):
    h = np.clip(0.5 + 0.5 * (b - a) / k, 0, 1)
    return b * (1 - h) + a * h - k * h * (1 - h)


def smax(a, b, k):
    return -smin(-a, -b, k)


def ellipse_d(x, y, ax, ay):
    """approximate signed distance to an ellipse (good enough near the boundary)"""
    e = np.sqrt((x / ax) ** 2 + (y / ay) ** 2) + 1e-9
    gx = x / ax ** 2 / e; gy = y / ay ** 2 / e
    return (e - 1) / np.sqrt(gx ** 2 + gy ** 2 + 1e-12)


def rbox(d2, dz, rr):
    """intersection of an in-plane distance and a vertical slab distance, edge rounded by rr"""
    d2p, dzp = d2 + rr, dz + rr
    return np.hypot(np.maximum(d2p, 0), np.maximum(dzp, 0)) + np.minimum(np.maximum(d2p, dzp), 0) - rr


def sdf(x, y, z):
    r = np.sqrt(x ** 2 + z ** 2) + 1e-9
    # hoop: D section (flat inside, rounded outside), swelling from the back to the shoulders
    phi = np.arctan2(np.abs(x), z)                         # 0 at the bezel, pi at the back
    s = np.clip((np.pi - phi) / (0.80 * np.pi), 0, 1)
    s = s * s * (3 - 2 * s)
    T = T_back + (T_sh - T_back) * s ** 1.5
    hw = (W_back + (W_sh - W_back) * s ** 3) / 2          # slender hoop, flaring at the shoulders
    u = r - R_in
    n = 2.4
    nrm = ((np.maximum(u, 0) / T) ** n + (np.abs(y) / hw) ** n) ** (1 / n)
    d_hoop = (nrm - 1) * np.minimum(T, hw)
    d_hoop = smax(d_hoop, z - (z_plat - 0.3), 0.3)       # the hoop stays under the bezel plate

    # bezel plate: flat oval, sides sloping in towards the shoulders
    z_pb = z_plat - plate_t
    k = np.clip((z - z_pb) / plate_t, 0, 1)
    sc = 0.93 + 0.07 * k
    d_plate = rbox(ellipse_d(x, y, Bx * sc, By * sc), np.maximum(z - z_plat, z_pb - z), 0.25)
    d = smin(d_hoop, d_plate, 1.8)                        # shoulders flow into the bezel
    d = smax(d, z - z_plat, 0.3)                          # flat table, softly rounded edge

    # collet: raised oval wall that holds the stone (the step of the bezel)
    d_col = rbox(ellipse_d(x, y, Cx, Cy), np.maximum(z - z_col, (z_plat - 0.5) - z), 0.18)
    d = smin(d, d_col, 0.15)

    d = smax(d, R_in - r, 0.3)                            # finger hole: flat band, rounded edges
    d_pocket = np.maximum(ellipse_d(x, y, Px, Py), z_seat - z)
    d = smax(d, -d_pocket, 0.06)                          # stone seat
    return d


def sdf_v(V):
    return sdf(V[:, 0], V[:, 1], V[:, 2])


def sdf_grad(V, h=1e-3):
    g = np.empty_like(V)
    for i in range(3):
        e = np.zeros(3); e[i] = h
        g[:, i] = (sdf_v(V + e) - sdf_v(V - e)) / (2 * h)
    return g


def project(V, iters=6):
    """Newton steps onto the zero level set: removes the marching-cubes facets"""
    for _ in range(iters):
        g = sdf_grad(V)
        V = V - (sdf_v(V) / ((g * g).sum(1) + 1e-12))[:, None] * g
    return V


# ---------------------------------------------------------------- body via marching cubes
vx = args.voxel
R_out = R_in + T_sh + 1.0
xs = np.arange(-max(R_out, Bx + 1.0), max(R_out, Bx + 1.0) + vx, vx)
ys = np.arange(-(By + 1.0), By + 1.0 + vx, vx)
zs = np.arange(-(R_in + T_back + 1.0), z_col + 1.0, vx)
print('grid', len(xs), len(ys), len(zs))
vol = np.empty((len(xs), len(ys), len(zs)), np.float32)
X, Y = np.meshgrid(xs, ys, indexing='ij')
for k, zz in enumerate(zs):
    vol[:, :, k] = sdf(X, Y, np.full_like(X, zz))
vol = np.nan_to_num(vol, nan=1.0)
vol = np.pad(vol, 1, constant_values=1.0)
verts, faces, _, _ = measure.marching_cubes(vol, 0.0, spacing=(vx, vx, vx))
del vol
verts += np.array([xs[0], ys[0], zs[0]]) - vx
body = trimesh.Trimesh(verts, faces, process=True)
body = max(body.split(only_watertight=False), key=lambda p: len(p.faces))
body.vertices = project(np.asarray(body.vertices))
print('body raw faces', len(body.faces), 'watertight', body.is_watertight)
if len(body.faces) > args.body_faces:
    import fast_simplification
    v2, f2 = fast_simplification.simplify(np.asarray(body.vertices, np.float32), np.asarray(body.faces),
                                          target_reduction=1 - args.body_faces / len(body.faces))
    body = trimesh.Trimesh(project(v2.astype(np.float64)), f2, process=True)
body.fix_normals()
g = sdf_grad(np.asarray(body.vertices))
body_normals = g / np.linalg.norm(g, axis=1, keepdims=True)   # exact surface normals
print('body faces', len(body.faces), 'watertight', body.is_watertight, 'vol mm3', round(body.volume, 1))

# ---------------------------------------------------------------- stone (height-field, watertight by construction)
h = np.load(args.height)
H, W = h.shape
stone_bot = z_seat
field_z = z_seat + st_field                # stone face: above the collet, the portrait on top
Nt, Nr = args.nt, args.nr
rho = np.linspace(0, 1, Nr + 1)[1:]       # exclude centre (added separately)
th = np.linspace(0, 2 * np.pi, Nt, endpoint=False)
RH, TH = np.meshgrid(rho, th, indexing='ij')       # (Nr, Nt)
U, V = RH * np.cos(TH), RH * np.sin(TH)


def top_z(U, V):
    rr = np.sqrt(U ** 2 + V ** 2)
    col = W / 2 + U * (W / 2) * args.img_scale
    row = H / 2 - V * (H / 2) * args.img_scale
    hv = ndi.map_coordinates(h, [row, col], order=1, mode='nearest')
    hv *= np.clip((0.97 - rr) / 0.06, 0, 1)                # fade relief before bevel
    bevel = np.where(rr > 0.88, -(st_field - st_wall) * (np.clip(rr - 0.88, 0, None) / 0.12) ** 1.5, 0.0)
    return field_z + bevel + args.relief * np.clip(hv, 0, 1.05)


ZT = top_z(U, V)
top = np.c_[(U * sx).ravel(), (V * sy).ravel(), ZT.ravel()]
centre = np.array([[0, 0, top_z(np.array([0.0]), np.array([0.0]))[0]]])
ring_bot = np.c_[sx * np.cos(th), sy * np.sin(th), np.full(Nt, stone_bot)]
centre_bot = np.array([[0, 0, stone_bot]])
V_all = np.vstack([centre, top, ring_bot, centre_bot])
iB0 = 1 + Nr * Nt
iCB = iB0 + Nt
F = []
j = np.arange(Nt); jn = (j + 1) % Nt
F.append(np.c_[np.zeros(Nt, int), 1 + j, 1 + jn])                      # centre fan
for i in range(Nr - 1):
    a = 1 + i * Nt + j; b = 1 + i * Nt + jn
    c = 1 + (i + 1) * Nt + j; d = 1 + (i + 1) * Nt + jn
    F.append(np.c_[a, c, d]); F.append(np.c_[a, d, b])
a = 1 + (Nr - 1) * Nt + j; b = 1 + (Nr - 1) * Nt + jn
c = iB0 + j; d = iB0 + jn
F.append(np.c_[a, c, d]); F.append(np.c_[a, d, b])                    # side wall
F.append(np.c_[np.full(Nt, iCB), iB0 + jn, iB0 + j])                  # bottom fan
stone = trimesh.Trimesh(V_all, np.vstack(F), process=True)
stone.fix_normals()
print('stone faces', len(stone.faces), 'watertight', stone.is_watertight, 'vol mm3', round(stone.volume, 1))

# ---------------------------------------------------------------- one-piece (for single-material resin / casting)
# a filler closes the 0.10 mm fitting gap round the stone up to 0.10 mm below the collet top
fill = trimesh.creation.cylinder(radius=1.0, height=1.0, sections=720)
fill.apply_scale([Px + 0.02, Py + 0.02, (z_col - 0.10) - (z_seat - 0.05)])
fill.apply_translation([0, 0, ((z_col - 0.10) + (z_seat - 0.05)) / 2])
try:
    one = trimesh.boolean.union([body, stone, fill], engine='manifold')
    print('one-piece watertight', one.is_watertight)
except Exception as e:
    print('union failed', e); one = trimesh.util.concatenate([body, stone])

# ---------------------------------------------------------------- exports
body.export(f'{P_TWO}/ring_body_gold.stl')
stone.export(f'{P_TWO}/apollo_stone_red.stl')
one.export(f'{P_ONE}/ring_one_piece.stl')

# coloured GLB (PBR), with the exact surface normals of the body
from trimesh.visual.material import PBRMaterial
b2 = body.copy(); s2 = stone.copy()
b2.vertex_normals = body_normals
b2.visual = trimesh.visual.TextureVisuals(material=PBRMaterial(name='gold', baseColorFactor=[1.0, 0.766, 0.336, 1], metallicFactor=1.0, roughnessFactor=0.22))
s2.visual = trimesh.visual.TextureVisuals(material=PBRMaterial(name='carnelian', baseColorFactor=[0.70, 0.07, 0.04, 1], metallicFactor=0.0, roughnessFactor=0.28))
sc = trimesh.Scene(); sc.add_geometry(b2, node_name='ring_body_gold'); sc.add_geometry(s2, node_name='apollo_stone_red')
sc.export(f'{P_VIEW}/apollo_signet_coloured.glb', include_normals=True)

# payload for the HTML viewer (source/viewer-build/build.mjs packs it into apollo_signet_viewer.html)
vdir = f'{P_BUILD}/viewer_payload'
os.makedirs(vdir, exist_ok=True)
np.asarray(body.vertices, np.float32).tofile(f'{vdir}/body_pos.f32')
np.asarray(body_normals, np.float32).tofile(f'{vdir}/body_nrm.f32')
np.asarray(body.faces, np.uint32).tofile(f'{vdir}/body_idx.u32')
np.asarray(stone.vertices, np.float32).tofile(f'{vdir}/stone_pos.f32')
np.asarray(stone.faces, np.uint32).tofile(f'{vdir}/stone_idx.u32')
json.dump(dict(us_size=args.us_size, R_in=R_in, z_seat=z_seat, z_col=z_col, Px=Px, Py=Py,
               stone_top=float(stone.vertices[:, 2].max())),
          open(f'{vdir}/meta.json', 'w'))


# coloured multi-part 3MF (hand-written: basematerials + two objects, assembled)
def obj_xml(oid, m, pid):
    v = '\n'.join(f'<vertex x="{a:.5f}" y="{b:.5f}" z="{c:.5f}"/>' for a, b, c in m.vertices)
    t = '\n'.join(f'<triangle v1="{a}" v2="{b}" v3="{c}"/>' for a, b, c in m.faces)
    return f'<object id="{oid}" type="model" pid="1" pindex="{pid}" name="{"ring_body_gold" if pid==0 else "apollo_stone_red"}"><mesh><vertices>\n{v}\n</vertices><triangles>\n{t}\n</triangles></mesh></object>'

model = f'''<?xml version="1.0" encoding="UTF-8"?>
<model unit="millimeter" xml:lang="en-US" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02">
<metadata name="Title">Apollo signet ring</metadata>
<resources>
<basematerials id="1"><base name="Gold" displaycolor="#D4A84AFF"/><base name="Carnelian red" displaycolor="#B01612FF"/></basematerials>
{obj_xml(2, body, 0)}
{obj_xml(3, stone, 1)}
<object id="4" type="model" name="Apollo signet ring"><components><component objectid="2"/><component objectid="3"/></components></object>
</resources>
<build><item objectid="4" transform="1 0 0 0 1 0 0 0 1 0 0 {-(zs[0]):.4f}"/></build>
</model>'''
with zipfile.ZipFile(f'{P_MC}/apollo_signet_2colour.3mf', 'w', zipfile.ZIP_DEFLATED) as z:
    z.writestr('[Content_Types].xml', '<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>')
    z.writestr('_rels/.rels', '<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
    z.writestr('3D/3dmodel.model', model)

stone_top = float(stone.vertices[:, 2].max())
info = dict(us_size=args.us_size, inner_diameter_mm=round(inner_d, 2),
            bezel_mm=[round(2 * Bx, 2), round(2 * By, 2)], collet_mm=[round(2 * Cx, 2), round(2 * Cy, 2)],
            stone_mm=[round(2 * sx, 2), round(2 * sy, 2)], seat_mm=[2 * Px, 2 * Py], seat_depth_mm=seat_depth,
            clearance_mm=clear, relief_mm=args.relief,
            stone_face_above_gold_mm=round(field_z - z_col, 2), portrait_top_above_gold_mm=round(stone_top - z_col, 2),
            gold_height_above_finger_mm=round(z_col - R_in, 2), total_height_above_finger_mm=round(stone_top - R_in, 2),
            hoop_back_mm=[T_back, W_back], hoop_shoulders_mm=[T_sh, W_sh],
            body_volume_mm3=round(body.volume, 1), stone_volume_mm3=round(stone.volume, 1),
            body_watertight=bool(body.is_watertight), stone_watertight=bool(stone.is_watertight),
            one_piece_watertight=bool(one.is_watertight),
            bbox_mm=np.round(one.extents, 2).tolist())
json.dump(info, open(f'{P_BUILD}/specs.json', 'w'), indent=1)
print(json.dumps(info, indent=1))
