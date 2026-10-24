#!/usr/bin/env python3
"""
Apollo signet ring generator  (all dimensions in mm)
------------------------------------------------------
Builds a watertight, two-part signet ring:
  * ring body  (gold)  – heavy comfort-fit shank, broad shoulders, flat oval table,
                          stone seat pocket
  * stone insert (red) – oval carnelian with Apollo portrait in raised relief
and exports printable STL / 3MF plus a coloured GLB for rendering.

Usage:  python3 build_ring.py --us-size 9 --height height.npy --out outdir
"""
import argparse, json, os, zipfile
import numpy as np
import trimesh
from scipy import ndimage as ndi
from skimage import measure

# ---------------------------------------------------------------- parameters
ap = argparse.ArgumentParser()
ap.add_argument('--us-size', type=float, default=9.0)
ap.add_argument('--height', default='height.npy')
ap.add_argument('--out', default='out')
ap.add_argument('--img-scale', type=float, default=1.0)
ap.add_argument('--nt', type=int, default=1800)
ap.add_argument('--nr', type=int, default=330)
ap.add_argument('--voxel', type=float, default=0.05)
ap.add_argument('--relief', type=float, default=0.85, help='max relief height above stone field')
args = ap.parse_args()

inner_d = 11.63 + 0.8128 * args.us_size          # US ring size -> inner diameter
R_in = inner_d / 2
os.makedirs(args.out, exist_ok=True)

# shank
T_bot, T_top = 2.3, 4.4         # radial thickness bottom/top
W_bot, W_top = 4.6, 14.0        # width along finger bottom/top
# bezel (oval, long axis along the finger = Y)
Ax, Ay = 7.1, 8.7               # outer semi-axes at top face
z_top = R_in + 5.0              # top face of the bezel
rim = 1.30                      # bezel wall thickness at top
Px, Py = Ax - rim, Ay - rim     # pocket semi-axes
pocket_depth = 1.6
z_seat = z_top - pocket_depth
clear = 0.10                    # radial clearance stone <-> pocket


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


def sdf(x, y, z):
    r = np.sqrt(x ** 2 + z ** 2) + 1e-9
    s = (1 + z / r) / 2                       # 0 bottom, 1 top
    s1 = s ** 1.5
    T = T_bot + (T_top - T_bot) * s1
    Wd = W_bot + (W_top - W_bot) * s1 ** 1.3
    a, b = T / 2, Wd / 2
    u = r - (R_in + a); v = y
    n = 3.6                                   # flatter, squarer section = heavier look
    nrm = ((np.abs(u) / a) ** n + (np.abs(v) / b) ** n) ** (1 / n)
    d_shank = (nrm - 1) * np.minimum(a, b)

    # near-vertical oval bezel block with rounded edges
    z_low = R_in + 0.2
    k = np.clip((z - z_low) / (z_top - z_low), 0, 1)
    sc = 0.90 + 0.10 * k ** 0.6
    d2 = ellipse_d(x, y, Ax * sc, Ay * sc)
    dz = np.maximum(z - z_top, (R_in - 1.0) - z)
    rr = 0.55
    d2p, dzp = d2 + rr, dz + rr
    d_head = np.hypot(np.maximum(d2p, 0), np.maximum(dzp, 0)) + np.minimum(np.maximum(d2p, dzp), 0) - rr

    d = smin(d_shank, d_head, 3.0)

    # finger hole (keep comfort fit, remove any blend intrusion)
    d = smax(d, (R_in - r), 0.25)
    # stone seat pocket
    d_pocket = np.maximum(ellipse_d(x, y, Px, Py), z_seat - z)
    d = smax(d, -d_pocket, 0.10)                 # softly rounded seat edge
    return d


# ---------------------------------------------------------------- body via marching cubes
vx = args.voxel
R_out = R_in + T_top + 1
xs = np.arange(-(Ax + 1.2), Ax + 1.2 + vx, vx)
xs = np.arange(-max(R_out, Ax + 1.2), max(R_out, Ax + 1.2) + vx, vx)
ys = np.arange(-(Ay + 1.2), Ay + 1.2 + vx, vx)
zs = np.arange(-(R_in + T_bot + 1.0), z_top + 1.0, vx)
print('grid', len(xs), len(ys), len(zs))
vol = np.empty((len(xs), len(ys), len(zs)), np.float32)
X, Y = np.meshgrid(xs, ys, indexing='ij')
for k, zz in enumerate(zs):
    vol[:, :, k] = sdf(X, Y, np.full_like(X, zz))
print('nan', np.isnan(vol).sum(), 'boundary min', min(vol[0].min(),vol[-1].min(),vol[:,0].min(),vol[:,-1].min(),vol[:,:,0].min(),vol[:,:,-1].min()))
vol = np.nan_to_num(vol, nan=1.0)
vol = np.pad(vol, 1, constant_values=1.0)
verts, faces, _, _ = measure.marching_cubes(vol, 0.0, spacing=(vx, vx, vx))
verts += np.array([xs[0], ys[0], zs[0]]) - vx
body = trimesh.Trimesh(verts, faces, process=True)
body.merge_vertices()
parts = body.split(only_watertight=False)
print('parts', [len(p.faces) for p in parts][:10])
body = max(parts, key=lambda p: len(p.faces))
body.fix_normals()
trimesh.smoothing.filter_taubin(body, lamb=0.5, nu=-0.53, iterations=14)   # remove marching-cubes faceting
print('body raw faces', len(body.faces), 'watertight', body.is_watertight)
if len(body.faces) > 600_000:
    import fast_simplification
    v2, f2 = fast_simplification.simplify(body.vertices, body.faces, target_reduction=1 - 600_000 / len(body.faces))
    body = trimesh.Trimesh(v2, f2, process=True)
    body.fix_normals()
print('body faces', len(body.faces), 'watertight', body.is_watertight, 'vol mm3', round(body.volume, 1))

# ---------------------------------------------------------------- stone (height-field, watertight by construction)
h = np.load(args.height)
H, W = h.shape
sx, sy = Px - clear, Py - clear
field_z = z_top - 0.55                    # field recessed: the rim guards the relief, like a coin
stone_bot = z_seat + 0.0
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
    bevel = np.where(rr > 0.88, -0.30 * ((rr - 0.88) / 0.12) ** 1.5, 0.0)
    return field_z + bevel + args.relief * np.clip(hv, 0, 1.05)


ZT = top_z(U, V)
top = np.c_[(U * sx).ravel(), (V * sy).ravel(), ZT.ravel()]
centre = np.array([[0, 0, top_z(np.array([0.0]), np.array([0.0]))[0]]])
ring_bot = np.c_[sx * np.cos(th), sy * np.sin(th), np.full(Nt, stone_bot)]
centre_bot = np.array([[0, 0, stone_bot]])
V_all = np.vstack([centre, top, ring_bot, centre_bot])
iC = 0
def iT(i, j): return 1 + i * Nt + (j % Nt)
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
try:
    one = trimesh.boolean.union([body, stone], engine='manifold')
    print('one-piece watertight', one.is_watertight)
except Exception as e:
    print('union failed', e); one = trimesh.util.concatenate([body, stone])

# ---------------------------------------------------------------- exports
GOLD = [212, 168, 74, 255]
RED = [176, 22, 18, 255]
body.export(f'{args.out}/ring_body_gold.stl')
stone.export(f'{args.out}/apollo_stone_red.stl')
one.export(f'{args.out}/ring_one_piece.stl')

# coloured GLB (PBR)
from trimesh.visual.material import PBRMaterial
b2 = body.copy(); s2 = stone.copy()
b2.visual = trimesh.visual.TextureVisuals(material=PBRMaterial(name='gold', baseColorFactor=[1.0, 0.766, 0.336, 1], metallicFactor=1.0, roughnessFactor=0.22))
s2.visual = trimesh.visual.TextureVisuals(material=PBRMaterial(name='carnelian', baseColorFactor=[0.70, 0.07, 0.04, 1], metallicFactor=0.0, roughnessFactor=0.28))
sc = trimesh.Scene(); sc.add_geometry(b2, node_name='ring_body_gold'); sc.add_geometry(s2, node_name='apollo_stone_red')
sc.export(f'{args.out}/apollo_signet_coloured.glb')


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
with zipfile.ZipFile(f'{args.out}/apollo_signet_2colour.3mf', 'w', zipfile.ZIP_DEFLATED) as z:
    z.writestr('[Content_Types].xml', '<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>')
    z.writestr('_rels/.rels', '<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
    z.writestr('3D/3dmodel.model', model)

info = dict(us_size=args.us_size, inner_diameter_mm=round(inner_d, 2),
            bezel_mm=[2 * Ax, 2 * Ay], stone_mm=[round(2 * sx, 2), round(2 * sy, 2)],
            pocket_mm=[2 * Px, 2 * Py], pocket_depth_mm=pocket_depth, clearance_mm=clear,
            relief_mm=args.relief, body_volume_mm3=round(body.volume, 1), stone_volume_mm3=round(stone.volume, 1),
            body_watertight=bool(body.is_watertight), stone_watertight=bool(stone.is_watertight),
            one_piece_watertight=bool(one.is_watertight),
            bbox_mm=np.round(one.extents, 2).tolist())
json.dump(info, open(f'{args.out}/specs.json', 'w'), indent=1)
print(json.dumps(info, indent=1))
