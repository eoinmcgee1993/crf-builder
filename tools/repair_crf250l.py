"""Repair crf250l.glb in place-ish (writes crf250l-fixed.glb).

Two classes of defect, both from the procedural generator:

1. Round/flat parts (wheels, chain, contact shadow) were built in the XY
   plane and never rotated onto the bike. Fixed with a node matrix, so the
   vertex data is untouched.
2. The six decal panels are flat plates in the wrong places. Rebuilt as
   lofted surfaces with clean 0..1 UVs, keeping the mesh names and the
   one-material-per-panel contract the integration guide depends on.
"""
import struct, json, math
import numpy as np

SRC, DST = 'crf250l.glb', 'crf250l-fixed.glb'

data = open(SRC, 'rb').read()
off = 12; chunks = []
while off < len(data):
    clen, ctype = struct.unpack('<I4s', data[off:off+8])
    chunks.append((ctype, off+8, clen)); off += 8 + clen
g   = json.loads(data[chunks[0][1]:chunks[0][1]+chunks[0][2]].decode())
BIN = bytearray(data[chunks[1][1]:chunks[1][1]+chunks[1][2]])

nodes_by_name = {n['name']: n for n in g['nodes']}

def centre_of(name):
    acc = g['accessors'][g['meshes'][nodes_by_name[name]['mesh']]['primitives'][0]['attributes']['POSITION']]
    return [(a+b)/2 for a, b in zip(acc['min'], acc['max'])]

def node_matrix(name, axis, deg):
    """Rotate a mesh about its OWN centre: T(c) . R . T(-c), column-major."""
    c = centre_of(name)
    t = math.radians(deg); ct, st = math.cos(t), math.sin(t)
    R = np.eye(4)
    if axis == 'y':  R[0,0]=ct; R[0,2]=st; R[2,0]=-st; R[2,2]=ct
    elif axis == 'x':R[1,1]=ct; R[1,2]=-st; R[2,1]=st; R[2,2]=ct
    T1 = np.eye(4); T1[:3,3] = c
    T0 = np.eye(4); T0[:3,3] = [-v for v in c]
    M = T1 @ R @ T0
    return [float(v) for v in M.T.flatten()]   # glTF is column-major

# A wheel drawn in XY with its axle down Z becomes a wheel with its axle
# across the bike after a quarter turn about Y. The chain ring is the same
# shape and the same mistake; the shadow needs laying flat instead.
for nm in ('crf_wheel_front', 'crf_wheel_rear', 'crf_chain'):
    nodes_by_name[nm]['matrix'] = node_matrix(nm, 'y', 90)
nodes_by_name['crf_contact_shadow']['matrix'] = node_matrix('crf_contact_shadow', 'x', -90)

# The chain ring also has to sit on the sprocket side, not on the centreline.
m = nodes_by_name['crf_chain']['matrix']; m[12] -= 0.165

# ---------------------------------------------------------------- panels
def loft(spine, crown=0.018, nu=14):
    """Fender: a spine of (z, y, halfwidth) swept across X with a crown."""
    pts = np.array(spine, dtype=float)
    nv = len(pts)
    def f(u, v):
        i = v * (nv - 1); i0 = int(min(i, nv - 2)); s = i - i0
        z, y, hw = pts[i0] * (1 - s) + pts[i0 + 1] * s
        a = 2 * u - 1
        return np.array([hw * a, y + crown * (1 - a * a), z])
    return grid(f, nu, 48)

def quadpanel(c00, c10, c01, c11, x0, bulge, mirror=False, nu=16, nv=16):
    """Shroud / fork guard: bilinear patch in (z,y), bulging out along X."""
    def f(u, v):
        z = (c00[0]*(1-u) + c10[0]*u)*(1-v) + (c01[0]*(1-u) + c11[0]*u)*v
        y = (c00[1]*(1-u) + c10[1]*u)*(1-v) + (c01[1]*(1-u) + c11[1]*u)*v
        b = (1 - (2*u-1)**2) * (1 - (2*v-1)**2)
        x = x0 + bulge * b
        return np.array([-x if mirror else x, y, z])
    return grid(f, nu, nv)

def grid(f, nu, nv):
    P, N, T, I = [], [], [], []
    for j in range(nv):
        for i in range(nu):
            u, v = i/(nu-1), j/(nv-1)
            p = f(u, v)
            e = 1e-4
            du = f(min(u+e,1), v) - f(max(u-e,0), v)
            dv = f(u, min(v+e,1)) - f(u, max(v-e,0))
            n = np.cross(du, dv)
            ln = np.linalg.norm(n)
            n = n/ln if ln > 1e-9 else np.array([0.,1.,0.])
            P.append(p); N.append(n); T.append([u, v])
    for j in range(nv-1):
        for i in range(nu-1):
            a = j*nu+i; b = a+1; c = a+nu; d = c+1
            I += [a, c, b, b, c, d]
    return (np.array(P, dtype=np.float32), np.array(N, dtype=np.float32),
            np.array(T, dtype=np.float32), np.array(I, dtype=np.uint32))

# Front wheel centre (0, .325, .732) r=.325 ; rear (0, .325, -.72) r=.325
# Seat/tank spans y .84-1.13, z -.71..0.43 ; tank half-width .18
PANELS = {
 'panel_front_fender': loft([(0.96,0.690,0.080),(0.89,0.762,0.098),(0.79,0.806,0.110),
                             (0.67,0.810,0.110),(0.56,0.780,0.100),(0.46,0.720,0.082)]),
 'panel_rear_fender_tail': loft([(-0.24,0.870,0.090),(-0.44,0.856,0.105),(-0.63,0.826,0.112),
                                 (-0.81,0.786,0.105),(-0.96,0.746,0.092),(-1.07,0.712,0.075)]),
 'panel_right_shroud': quadpanel((0.04,0.62),(0.33,0.65),(0.00,1.00),(0.38,0.98), 0.176, 0.034),
 'panel_left_shroud':  quadpanel((0.04,0.62),(0.33,0.65),(0.00,1.00),(0.38,0.98), 0.176, 0.034, mirror=True),
 'panel_right_fork_guard': quadpanel((0.68,0.40),(0.80,0.43),(0.66,0.62),(0.78,0.65), 0.152, 0.020, nu=10, nv=12),
 'panel_left_fork_guard':  quadpanel((0.68,0.40),(0.80,0.43),(0.66,0.62),(0.78,0.65), 0.152, 0.020, mirror=True, nu=10, nv=12),
}

def pad4():
    while len(BIN) % 4: BIN.append(0)

def add(arr, target=None):
    pad4()
    o = len(BIN); raw = arr.tobytes(); BIN.extend(raw)
    bv = {'buffer': 0, 'byteOffset': o, 'byteLength': len(raw)}
    if target: bv['target'] = target
    g['bufferViews'].append(bv)
    return len(g['bufferViews']) - 1

def accessor(bv, count, ctype, atype, mn=None, mx=None):
    a = {'bufferView': bv, 'componentType': ctype, 'count': count, 'type': atype}
    if mn is not None: a['min'] = mn; a['max'] = mx
    g['accessors'].append(a)
    return len(g['accessors']) - 1

for name, (P, N, T, I) in PANELS.items():
    mesh = g['meshes'][nodes_by_name[name]['mesh']]
    prim = mesh['primitives'][0]
    prim['attributes'] = {
        'POSITION':   accessor(add(P, 34962), len(P), 5126, 'VEC3',
                               [float(v) for v in P.min(0)], [float(v) for v in P.max(0)]),
        'NORMAL':     accessor(add(N, 34962), len(N), 5126, 'VEC3'),
        'TEXCOORD_0': accessor(add(T, 34962), len(T), 5126, 'VEC2'),
    }
    prim['indices'] = accessor(add(I, 34963), len(I), 5125, 'SCALAR')
    print(f"  {name:24} {len(P):5} verts  {len(I)//3:5} tris  "
          f"x {P[:,0].min():+.3f}..{P[:,0].max():+.3f}  "
          f"y {P[:,1].min():+.3f}..{P[:,1].max():+.3f}  "
          f"z {P[:,2].min():+.3f}..{P[:,2].max():+.3f}")

g['buffers'][0]['byteLength'] = len(BIN)
js = json.dumps(g, separators=(',', ':')).encode()
while len(js) % 4: js += b' '
pad4()
out = (struct.pack('<4sII', b'glTF', 2, 12 + 8 + len(js) + 8 + len(BIN))
       + struct.pack('<I4s', len(js), b'JSON') + js
       + struct.pack('<I4s', len(BIN), b'BIN\x00') + bytes(BIN))
open(DST, 'wb').write(out)
print(f"\nwrote {DST}  {len(out)} bytes (was {len(data)})")
