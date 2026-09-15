"""Mesh primitives. Swept and revolved surfaces get smooth normals from the
parametric form; boxes get flat ones, because averaging a box's corners makes
a hard edge look like a dent."""
import numpy as np

class Mesh:
    def __init__(self): self.P=[]; self.N=[]; self.I=[]
    def add(self, P, N, I):
        o = len(self.P)
        self.P.extend(P); self.N.extend(N); self.I.extend([i+o for i in I])
    def arrays(self):
        return (np.array(self.P, np.float32), np.array(self.N, np.float32),
                np.array(self.I, np.uint32))

def _grid_idx(nu, nv, closed_u):
    I=[]
    for j in range(nv-1):
        for i in range(nu if closed_u else nu-1):
            a=j*nu+i; b=j*nu+(i+1)%nu; c=a+nu; d=b+nu
            I += [a,c,b, b,c,d]
    return I

def surface(f, nu, nv, closed_u=False):
    """f(u,v)->xyz sampled on a grid, normals by central difference."""
    P=[]; N=[]
    for j in range(nv):
        for i in range(nu):
            u = i/nu if closed_u else i/(nu-1)
            v = j/(nv-1); e=1e-4
            p = f(u,v)
            du = f((u+e)%1.0 if closed_u else min(u+e,1), v) - f((u-e)%1.0 if closed_u else max(u-e,0), v)
            dv = f(u, min(v+e,1)) - f(u, max(v-e,0))
            n = np.cross(du,dv); ln=np.linalg.norm(n)
            P.append(p); N.append(n/ln if ln>1e-9 else np.array([0.,1.,0.]))
    return P, N, _grid_idx(nu,nv,closed_u)

def revolve(profile, centre, axis=0, seg=28):
    """profile: [(radius, offset-along-axis)], revolved about a world axis."""
    prof = np.array(profile, float)
    n = len(prof)
    a1, a2 = [k for k in (0,1,2) if k != axis]
    def f(u, v):
        th = u*2*np.pi
        i = v*(n-1); i0=int(min(i,n-2)); s=i-i0
        r, off = prof[i0]*(1-s) + prof[i0+1]*s
        p = np.zeros(3); p[axis]=off; p[a1]=r*np.cos(th); p[a2]=r*np.sin(th)
        return p + centre
    return surface(f, seg, n, closed_u=True)

def tube(pts, radius, seg=12):
    """Circular sweep along a polyline, with a parallel-transport frame so the
    tube does not spin about its own axis at each bend."""
    pts = np.array(pts, float); n=len(pts)
    tans=[]
    for i in range(n):
        if i==0: t=pts[1]-pts[0]
        elif i==n-1: t=pts[-1]-pts[-2]
        else: t=pts[i+1]-pts[i-1]
        tans.append(t/np.linalg.norm(t))
    up = np.array([0.,0.,1.])
    if abs(np.dot(tans[0],up))>0.9: up=np.array([1.,0.,0.])
    nrm=[np.cross(tans[0],up)]; nrm[0]/=np.linalg.norm(nrm[0])
    for i in range(1,n):
        v = nrm[i-1] - tans[i]*np.dot(nrm[i-1],tans[i])
        ln=np.linalg.norm(v)
        nrm.append(v/ln if ln>1e-9 else nrm[i-1])
    rad = radius if hasattr(radius,'__len__') else [radius]*n
    def f(u,v):
        th=u*2*np.pi
        i=v*(n-1); i0=int(min(i,n-2)); s=i-i0
        c = pts[i0]*(1-s)+pts[i0+1]*s
        t = tans[i0]*(1-s)+tans[i0+1]*s; t/=np.linalg.norm(t)
        nn = nrm[i0]*(1-s)+nrm[i0+1]*s
        nn = nn - t*np.dot(nn,t); nn/=np.linalg.norm(nn)
        bb = np.cross(t,nn)
        r = rad[i0]*(1-s)+rad[i0+1]*s
        return c + (np.cos(th)*nn + np.sin(th)*bb)*r
    return surface(f, seg, n, closed_u=True)

def box(lo, hi):
    lo=np.array(lo,float); hi=np.array(hi,float)
    c=[[lo[0],lo[1],lo[2]],[hi[0],lo[1],lo[2]],[hi[0],hi[1],lo[2]],[lo[0],hi[1],lo[2]],
       [lo[0],lo[1],hi[2]],[hi[0],lo[1],hi[2]],[hi[0],hi[1],hi[2]],[lo[0],hi[1],hi[2]]]
    faces=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(2,3,7,6),(1,2,6,5),(0,4,7,3)]
    P=[];N=[];I=[]
    for q in faces:
        v=[np.array(c[k]) for k in q]
        n=np.cross(v[1]-v[0], v[2]-v[0]); n/=np.linalg.norm(n)
        o=len(P); P+=v; N+=[n]*4; I+=[o,o+1,o+2,o,o+2,o+3]
    return P,N,I

def mirror_x(P,N,I):
    """Mirroring flips winding, so the index order has to flip with it."""
    P=[np.array([-p[0],p[1],p[2]]) for p in P]
    N=[np.array([-n[0],n[1],n[2]]) for n in N]
    I=[I[i+j] for i in range(0,len(I),3) for j in (0,2,1)]
    return P,N,I
