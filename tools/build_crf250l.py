"""Build crf250l.glb to CRF250L reference dimensions.

Wheelbase 1445, seat height 875, rake 27.6 deg, 21in front / 18in rear —
the published figures, so the silhouette is proportioned rather than guessed.
Node names, the six panel_* meshes and one material per panel are kept
exactly as INTEGRATION.md specifies.
"""
import struct, json, sys
import numpy as np
sys.path.insert(0, '.')
from geom import Mesh, surface, revolve, tube, box, mirror_x

# ---- reference frame: +Z forward, +Y up, +X right, ground at y=0 ----
FA = np.array([0.0, 0.367, 0.725])   # front axle, 21in wheel
RA = np.array([0.0, 0.325, -0.720])  # rear axle, 18in wheel
SH = np.array([0.0, 1.100, 0.360])   # steering head
FORK = (FA - SH); FORK /= np.linalg.norm(FORK)
def on_fork(y):
    return SH + FORK * ((SH[1] - y) / -FORK[1])

parts = {}
def part(name): parts.setdefault(name, Mesh()); return parts[name]
def put(name, tri): part(name).add(*tri)
def put_pair(name, tri):          # a part and its mirror image
    put(name, tri); put(name, mirror_x(*tri))

# ---------------------------------------------------------------- wheels
def wheel(name, rim_name, centre, r, width, spokes=18):
    r_in = r - (0.075 if width < 0.1 else 0.095)
    w = width / 2
    put(name, revolve([(r_in,-w),(r-0.02,-w),(r,-w+0.025),(r,w-0.025),
                       (r-0.02,w),(r_in,w),(r_in,-w)], centre, axis=0, seg=32))
    rw = width * 0.30
    put(rim_name, revolve([(r_in-0.035,-rw),(r_in,-rw),(r_in,rw),(r_in-0.035,rw)],
                          centre, axis=0, seg=32))
    put(rim_name, revolve([(0.055,-0.065),(0.055,0.065)], centre, axis=0, seg=20))
    for k in range(spokes):
        a = 2*np.pi*k/spokes
        side = 0.055 if k % 2 else -0.055
        hub = centre + np.array([side, np.cos(a)*0.05, np.sin(a)*0.05])
        b = a + (0.22 if k % 2 else -0.22)
        out = centre + np.array([0.0, np.cos(b)*(r_in-0.012), np.sin(b)*(r_in-0.012)])
        put(rim_name, tube([hub, out], 0.0045, seg=5))

wheel('crf_wheel_front', 'crf_rim_front', FA, 0.367, 0.076)
wheel('crf_wheel_rear',  'crf_rim_rear',  RA, 0.325, 0.120)
put('crf_rim_front', revolve([(0.105,-0.080),(0.132,-0.080),(0.132,-0.074),(0.105,-0.074)],
                             FA, axis=0, seg=24))   # front brake disc

# ----------------------------------------------------------------- frame
TUBE = 0.021
put('crf_frame', tube([on_fork(1.16), on_fork(0.98)], 0.036, seg=14))   # head tube
put_pair('crf_frame', tube([[0.070,1.055,0.335],[0.098,0.975,0.145],
                            [0.100,0.855,-0.030],[0.088,0.560,-0.048],
                            [0.082,0.470,-0.050]], TUBE))               # main spar
put('crf_frame', tube([[0.0,1.000,0.392],[0.0,0.760,0.430],[0.0,0.470,0.330],
                       [0.0,0.345,0.145],[0.0,0.330,-0.010]], TUBE))    # downtube + cradle
put_pair('crf_frame', tube([[0.0,0.330,-0.010],[0.075,0.400,-0.045],
                            [0.082,0.470,-0.050]], 0.018))
put_pair('crf_frame', tube([[0.072,0.880,-0.020],[0.084,0.846,-0.300],
                            [0.086,0.822,-0.600]], 0.017))              # subframe upper
put_pair('crf_frame', tube([[0.080,0.560,-0.060],[0.086,0.730,-0.380],
                            [0.086,0.818,-0.585]], 0.015))              # subframe lower
put('crf_frame', tube([[0.0,0.930,-0.115],[0.0,0.520,-0.250]], 0.032))  # shock body
put_pair('crf_frame', box([0.105,0.425,-0.135],[0.185,0.450,-0.045]))   # footpeg

# ---------------------------------------------------------------- engine
put('crf_engine', box([-0.104,0.330,-0.105],[0.104,0.540,0.145]))       # cases
put('crf_engine', tube([[0.0,0.520,0.055],[0.0,0.742,0.126]], 0.098, seg=4))   # barrel
put('crf_engine', tube([[0.0,0.735,0.122],[0.0,0.822,0.150]], 0.104, seg=4))   # head
put('crf_engine', revolve([(0.0,0.113),(0.088,0.113),(0.088,0.152),(0.0,0.152)],
                          np.array([0.0,0.420,0.010]), axis=0, seg=22))  # clutch cover

# ----------------------------------------------------------- tank + seat
def body(stations, seg=22, flat=2.0):
    """Superellipse cross-sections lofted along Z. flat=2 is an ellipse;
    higher flattens the top, which is what turns a sausage into a seat."""
    st = np.array(stations, float); n = len(st); e = 2.0/flat
    def f(u, v):
        i = v*(n-1); i0=int(min(i,n-2)); s=i-i0
        z, top, bot, hw = st[i0]*(1-s) + st[i0+1]*s
        a = u*2*np.pi; ca, sa = np.cos(a), np.sin(a)
        return np.array([hw*np.sign(sa)*abs(sa)**e,
                         (top+bot)/2 + (top-bot)/2*np.sign(ca)*abs(ca)**e, z])
    return surface(f, seg, n, closed_u=True)

put('crf_tank_seat', body([(0.425,1.030,0.905,0.040),(0.360,1.092,0.870,0.098),
                           (0.270,1.105,0.858,0.121),(0.170,1.092,0.858,0.120),
                           (0.080,1.025,0.870,0.092),(0.030,0.960,0.878,0.070)], flat=2.4))
put('crf_tank_seat', body([(0.040,0.950,0.878,0.068),(-0.090,0.898,0.836,0.098),
                           (-0.260,0.884,0.808,0.113),(-0.430,0.880,0.802,0.110),
                           (-0.570,0.876,0.806,0.092),(-0.650,0.866,0.820,0.058)], flat=3.2))

# ------------------------------------------------------------- front end
put_pair('crf_front_end', tube([on_fork(1.135)+[0.115,0,0], on_fork(0.720)+[0.115,0,0]], 0.027))
put_pair('crf_front_end', tube([on_fork(0.770)+[0.125,0,0], on_fork(0.395)+[0.125,0,0]], 0.034))
put('crf_front_end', box([-0.150,1.118,on_fork(1.145)[2]-0.052],
                         [ 0.150,1.170,on_fork(1.145)[2]+0.052]))        # top clamp
put('crf_front_end', box([-0.152,0.968,on_fork(1.000)[2]-0.055],
                         [ 0.152,1.020,on_fork(1.000)[2]+0.055]))        # bottom clamp
put('crf_front_end', tube([[-0.370,1.178,0.292],[-0.130,1.222,0.330],[0.0,1.226,0.336],
                           [0.130,1.222,0.330],[0.370,1.178,0.292]], 0.014))  # handlebar
put('crf_front_end', body([(0.470,1.140,1.020,0.052),(0.430,1.175,0.985,0.092),
                           (0.380,1.160,0.975,0.086),(0.340,1.120,0.985,0.060)], seg=18))

# -------------------------------------------------------------- swingarm
put_pair('crf_swingarm', tube([[0.086,0.470,-0.055],[0.082,0.400,-0.330],
                               [0.076,0.325,-0.720]], [0.040,0.030,0.022]))
put('crf_swingarm', box([-0.086,0.432,-0.175],[0.086,0.462,-0.120]))

# -------------------------------------------------------------- exhaust
put('crf_exhaust', tube([[0.052,0.820,0.170],[0.082,0.700,0.290],[0.112,0.520,0.245],
                         [0.132,0.432,0.020],[0.146,0.500,-0.240],[0.158,0.612,-0.418]], 0.023))
put('crf_exhaust', tube([[0.160,0.618,-0.420],[0.172,0.690,-0.870]], [0.056,0.050]))

# -------------------------------------------------------------- radiator
put_pair('crf_radiator', box([0.112,0.700,0.250],[0.146,0.960,0.365]))

# ----------------------------------------------------------------- chain
CX = -0.162
put('crf_chain', revolve([(0.075,-0.006),(0.108,-0.006),(0.108,0.006),(0.075,0.006)],
                         RA + [CX,0,0], axis=0, seg=26))
put('crf_chain', revolve([(0.028,-0.006),(0.050,-0.006),(0.050,0.006),(0.028,0.006)],
                         np.array([CX,0.470,-0.020]), axis=0, seg=18))
put('crf_chain', tube([[CX,0.518,-0.020],[CX,0.432,-0.720]], 0.0075, seg=6))
put('crf_chain', tube([[CX,0.422,-0.020],[CX,0.218,-0.720]], 0.0075, seg=6))

# ---------------------------------------------------------------- shadow
put('crf_contact_shadow', revolve([(0.0,0.002),(1.15,0.002)],
                                  np.array([0.0,0.0,-0.02]), axis=1, seg=40))

# ---------------------------------------------------------------- panels
def loft(spine, wrap=0.55, nu=16, nv=48):
    pts = np.array(spine, float); nvp = len(pts)
    PHI = np.radians(62.0); SP = np.sin(PHI); CP = np.cos(PHI)
    def f(u, v):
        i = v*(nvp-1); i0=int(min(i,nvp-2)); s=i-i0
        z, y, hw = pts[i0]*(1-s) + pts[i0+1]*s
        th = (2*u-1)*PHI
        return np.array([hw*np.sin(th)/SP,
                         y + hw*wrap*(np.cos(th)-CP)/(1-CP), z])
    return f, nu, nv

def patch(c00, c10, c01, c11, x0, bulge, mirror=False, nu=16, nv=16):
    def f(u, v):
        z = (c00[0]*(1-u)+c10[0]*u)*(1-v) + (c01[0]*(1-u)+c11[0]*u)*v
        y = (c00[1]*(1-u)+c10[1]*u)*(1-v) + (c01[1]*(1-u)+c11[1]*u)*v
        b = (1-(2*u-1)**2)*(1-(2*v-1)**2)
        x = x0 + bulge*b
        return np.array([-x if mirror else x, y, z])
    return f, nu, nv

PANEL_SURF = {
 'panel_front_fender': loft([(1.055,0.690,0.072),(0.980,0.756,0.092),(0.880,0.796,0.104),
                             (0.760,0.806,0.104),(0.645,0.784,0.095),(0.552,0.738,0.078)]),
 'panel_rear_fender_tail': loft([(-0.600,0.872,0.086),(-0.740,0.856,0.100),(-0.880,0.834,0.102),
                                 (-1.000,0.808,0.094),(-1.090,0.786,0.082),(-1.155,0.768,0.066)]),
 'panel_right_shroud': patch((0.140,0.760),(0.330,0.790),(0.115,1.000),(0.370,1.022), 0.136, 0.036),
 'panel_left_shroud':  patch((0.140,0.760),(0.330,0.790),(0.115,1.000),(0.370,1.022), 0.136, 0.036, mirror=True),
 'panel_right_fork_guard': patch((0.625,0.415),(0.735,0.445),(0.520,0.665),(0.630,0.695), 0.130, 0.022, nu=10, nv=14),
 'panel_left_fork_guard':  patch((0.625,0.415),(0.735,0.445),(0.520,0.665),(0.630,0.695), 0.130, 0.022, mirror=True, nu=10, nv=14),
}

# ------------------------------------------------------------- write glTF
MATS = [
 ('mat_tyre',   [0.055,0.055,0.062,1], 0.0, 0.95), ('mat_rim',    [0.70,0.72,0.76,1], 0.90,0.30),
 ('mat_frame',  [0.235,0.255,0.290,1], 0.60,0.45), ('mat_engine', [0.30,0.32,0.345,1],0.80,0.35),
 ('mat_body',   [0.070,0.072,0.082,1], 0.0, 0.55), ('mat_chrome', [0.78,0.80,0.84,1], 0.95,0.18),
 ('mat_dark',   [0.130,0.140,0.160,1], 0.30,0.70), ('mat_shadow', [0.0,0.0,0.0,1],    0.0, 1.0),
]
MAT_OF = {
 'crf_wheel_front':'mat_tyre','crf_wheel_rear':'mat_tyre',
 'crf_rim_front':'mat_rim','crf_rim_rear':'mat_rim',
 'crf_frame':'mat_frame','crf_engine':'mat_engine','crf_tank_seat':'mat_body',
 'crf_front_end':'mat_chrome','crf_swingarm':'mat_rim','crf_exhaust':'mat_chrome',
 'crf_radiator':'mat_dark','crf_chain':'mat_dark','crf_contact_shadow':'mat_shadow',
}

g = {'asset':{'version':'2.0','generator':'crf-garage build_crf250l'},
     'scene':0,'scenes':[{'nodes':[]}],'nodes':[],'meshes':[],'materials':[],
     'accessors':[],'bufferViews':[],'buffers':[{'byteLength':0}]}
BIN = bytearray()

for nm, col, met, rgh in MATS:
    m = {'name':nm,'pbrMetallicRoughness':{'baseColorFactor':col,'metallicFactor':met,
         'roughnessFactor':rgh},'doubleSided':True}
    if nm == 'mat_shadow':
        m['alphaMode']='BLEND'; m['pbrMetallicRoughness']['baseColorFactor']=[0,0,0,0.5]
    g['materials'].append(m)
for p in PANEL_SURF:
    g['materials'].append({'name':'mat_'+p,'doubleSided':True,
        'pbrMetallicRoughness':{'baseColorFactor':[1,1,1,1],'metallicFactor':0.0,
                                'roughnessFactor':0.6}})
MIDX = {m['name']: i for i, m in enumerate(g['materials'])}

def add_bv(arr, target):
    while len(BIN) % 4: BIN.append(0)
    o=len(BIN); raw=arr.tobytes(); BIN.extend(raw)
    g['bufferViews'].append({'buffer':0,'byteOffset':o,'byteLength':len(raw),'target':target})
    return len(g['bufferViews'])-1
def add_acc(bv, count, ctype, atype, mn=None, mx=None):
    a={'bufferView':bv,'componentType':ctype,'count':count,'type':atype}
    if mn is not None: a['min']=mn; a['max']=mx
    g['accessors'].append(a); return len(g['accessors'])-1

def emit(name, P, N, I, T=None, mat=None):
    attrs = {'POSITION': add_acc(add_bv(P,34962), len(P), 5126,'VEC3',
                                 [float(v) for v in P.min(0)],[float(v) for v in P.max(0)]),
             'NORMAL':   add_acc(add_bv(N,34962), len(N), 5126,'VEC3')}
    if T is not None:
        attrs['TEXCOORD_0'] = add_acc(add_bv(T,34962), len(T), 5126,'VEC2')
    prim={'attributes':attrs,'indices':add_acc(add_bv(I,34963), len(I),5125,'SCALAR')}
    if mat is not None: prim['material']=mat
    g['meshes'].append({'name':name,'primitives':[prim]})
    g['nodes'].append({'name':name,'mesh':len(g['meshes'])-1})
    g['scenes'][0]['nodes'].append(len(g['nodes'])-1)

for name, m in parts.items():
    P,N,I = m.arrays()
    emit(name, P, N, I, mat=MIDX[MAT_OF[name]])
    print(f"  {name:22} {len(P):6} verts {len(I)//3:6} tris")

for name, (f, nu, nv) in PANEL_SURF.items():
    Pl, Nl, Il = surface(f, nu, nv)
    T=[]
    for j in range(nv):
        for i in range(nu): T.append([i/(nu-1), j/(nv-1)])
    P=np.array(Pl,np.float32); N=np.array(Nl,np.float32)
    emit(name, P, N, np.array(Il,np.uint32), np.array(T,np.float32), MIDX['mat_'+name])
    print(f"  {name:22} {len(P):6} verts {len(Il)//3:6} tris   UV 0..1")

g['buffers'][0]['byteLength']=len(BIN)
js=json.dumps(g,separators=(',',':')).encode()
while len(js)%4: js+=b' '
while len(BIN)%4: BIN.append(0)
out=(struct.pack('<4sII',b'glTF',2,12+8+len(js)+8+len(BIN))
     +struct.pack('<I4s',len(js),b'JSON')+js
     +struct.pack('<I4s',len(BIN),b'BIN\x00')+bytes(BIN))
open('crf250l-fixed.glb','wb').write(out)
tris=sum(len(m.arrays()[2])//3 for m in parts.values())
print(f"\n  wrote crf250l-fixed.glb  {len(out)//1024} KB   chassis {tris} tris")
