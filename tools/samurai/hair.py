# Cabelo em mechas: cada mecha e um tubo achatado que nasce no couro cabeludo,
# segue o fluxo da regiao (franja para frente e sobre o olho direito, laterais para baixo,
# topo para tras) e e empurrado para fora de um elipsoide da cabeca para ganhar volume.
import numpy as np, math
from land import V, dom, J
from face import EYE
rng=np.random.default_rng(3)
H=V[dom=='head']
eye_z=EYE['L'][2]; eye_y=EYE['L'][1]
top=H[H[:,2]>eye_z-0.01]
C=np.array([0, (top[:,1].min()+top[:,1].max())/2, eye_z+0.01])
R=np.array([np.abs(top[:,0]).max(), (top[:,1].max()-top[:,1].min())/2, top[:,2].max()-C[2]])
def inside(p, pad):
    q=(p-C)/(R+pad); return np.linalg.norm(q)
def push_out(p, pad):
    q=(p-C)/(R+pad); n=np.linalg.norm(q)
    if n<1: p=C+q/n*(R+pad)
    return p
def scalp_mask():
    rel=V-C
    front=-rel[:,1]/R[1]           # 1 na frente
    side=np.abs(rel[:,0])/R[0]
    z=V[:,2]
    hairline=np.where(front>0.55, eye_z+0.058-0.03*side**2, eye_z+0.005)
    m=(dom=='head')&(z>hairline)
    # atras das orelhas desce ate a nuca
    back=rel[:,1]>0.01
    m|=(dom=='head')&back&(z>eye_z-0.085)&(np.abs(rel[:,0])<R[0]*0.95)
    # costeletas na frente da orelha
    m|=(dom=='head')&(side>0.82)&(z>eye_z-0.045)&(rel[:,1]>-0.045)&(rel[:,1]<0.0)
    return m
def strand(p0, n0, kind):
    if kind=='fringe':  L=rng.uniform(0.07,0.11); flow=np.array([0.55,-0.45,-0.8])
    elif kind=='fringeR': L=rng.uniform(0.13,0.17); flow=np.array([-0.35,-0.35,-1.0])
    elif kind=='top':   L=rng.uniform(0.10,0.15); flow=np.array([np.sign(p0[0])*0.35,0.55,-0.5])
    elif kind=='side':  L=rng.uniform(0.08,0.12); flow=np.array([np.sign(p0[0])*0.15,0.05,-1.0])
    elif kind=='burn':  L=rng.uniform(0.05,0.07); flow=np.array([0,0.05,-1.0])
    else:               L=rng.uniform(0.09,0.14); flow=np.array([0,0.25,-1.0])
    flow=flow/np.linalg.norm(flow)
    n=9; pts=[p0]; d=n0*0.9+flow*0.5+rng.normal(0,0.08,3); d/=np.linalg.norm(d)
    pad=0.012+0.02*rng.random()
    for i in range(1,n):
        t=i/(n-1)
        d=d*0.6+flow*(0.32+0.4*t)+rng.normal(0,0.12,3)*t
        d/=np.linalg.norm(d)
        p=pts[-1]+d*L/(n-1)
        if p[2]>eye_z-0.10: p=push_out(p,pad*(0.6+0.8*t))
        pts.append(p)
    return np.array(pts), n0
def clump_mesh(P, n0, w0, th0, sides=5):
    verts=[];faces=[];uvs=[]; n=len(P)
    for i in range(n):
        d=P[min(i+1,n-1)]-P[max(i-1,0)]; d/=np.linalg.norm(d)+1e-9
        a=np.cross(d,n0);
        if np.linalg.norm(a)<1e-4: a=np.cross(d,[1,0,0])
        a/=np.linalg.norm(a); b=np.cross(d,a)
        t=i/(n-1); w=w0*(1-t**2.4)+0.0008; th=th0*(1-t**1.5)+0.0006
        for k in range(sides):
            ang=2*math.pi*k/sides; verts.append(P[i]+a*math.cos(ang)*w+b*math.sin(ang)*th)
    for i in range(n-1):
        for k in range(sides):
            a_=i*sides+k; b_=i*sides+(k+1)%sides; faces.append((a_,b_,b_+sides,a_+sides))
            uvs+=[(k/sides,i/(n-1)),((k+1)/sides,i/(n-1)),((k+1)/sides,(i+1)/(n-1)),(k/sides,(i+1)/(n-1))]
    return verts,faces,uvs
def build(Nrm, count=380):
    m=scalp_mask(); idx=np.where(m)[0]
    rel=V[idx]-C
    Vs=[];Fs=[];Us=[]
    def add(p0,n0,kind,w,th):
        P,n0=strand(p0,n0,kind); v,f,u=clump_mesh(P,n0,w,th); o=len(Vs)
        Vs.extend(v); Fs.extend([tuple(x+o for x in ff) for ff in f]); Us.extend(u)
    pick=rng.choice(idx, size=min(count,len(idx)), replace=False)
    for vi in pick:
        p=V[vi]; r=p-C; n0=Nrm[vi]
        front=-r[1]/R[1]; side=abs(r[0])/R[0]
        if front>0.45 and p[2]>eye_z+0.03: kind='fringeR' if p[0]<-0.005 else 'fringe'
        elif side>0.8 and p[2]<eye_z+0.02: kind='burn'
        elif side>0.7: kind='side'
        elif r[1]>0.02 and p[2]<eye_z+0.05: kind='back'
        else: kind='top'
        add(p+n0*0.002,n0,kind,rng.uniform(0.013,0.021),rng.uniform(0.0028,0.0042))
    # franja extra sobre o olho direito
    fr=idx[(-(V[idx,1]-C[1])/R[1]>0.5)&(V[idx,0]<0.02)&(V[idx,2]>eye_z+0.04)]
    for vi in rng.choice(fr,size=min(40,len(fr)),replace=False):
        add(V[vi]+Nrm[vi]*0.002,Nrm[vi],'fringeR',rng.uniform(0.008,0.013),0.0035)
    return np.array(Vs),Fs,Us,m
def brows(Nrm):
    Vs=[];Fs=[];Us=[]
    for s,sx in (('L',1),('R',-1)):
        c=EYE[s]
        for k in range(16):
            u=k/15; x=c[0]+sx*(-0.021+u*0.048); z=c[2]+0.021+0.006*math.sin(u*math.pi*0.9)-0.004*u
            m=(dom=='head')&(np.abs(V[:,0]-x)<0.006)&(np.abs(V[:,2]-z)<0.006)&(V[:,1]<c[1]+0.01)
            if not m.any(): continue
            vi=np.where(m)[0][np.argmin(V[m,1])]
            p0=V[vi]+Nrm[vi]*0.0012; d=np.array([sx*1.0,0,0.35*(1-u)-0.25*u]); d/=np.linalg.norm(d)
            for j in range(2):
                q0=p0+np.array([0,0,(j-0.5)*0.0035])
                P=np.array([q0+d*0.0045*i+Nrm[vi]*0.0008*i*(1-i/4) for i in range(4)])
                v,f,uu=clump_mesh(P,Nrm[vi],0.0022,0.0007,sides=3); o=len(Vs)
                Vs.extend(v); Fs.extend([tuple(x+o for x in ff) for ff in f]); Us.extend(uu)
    return np.array(Vs),Fs,Us
