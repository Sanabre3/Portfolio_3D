import numpy as np, math
from land import V, dom, J, B
G=dict(np.load('/tmp/sam/groups.npz'))
def cvn(p): p=np.asarray(p,float); return np.stack([p[...,0],-p[...,2],p[...,1]],-1)
VF=cvn(B['Vfull'])
EYE={s:VF[G[f'helper-{c}-eye']].mean(0) for s,c in (('L','l'),('R','r'))}
EYER=np.linalg.norm(VF[G['helper-l-eye']]-EYE['L'],axis=1).mean()
def eyes():
    """Ajusta o olho high-poly do MakeHuman (CC0) pelo arquivo .mhclo."""
    lines=[l.split() for l in open('/tmp/sam/mh/eyes/high-poly/high-poly.mhclo')]
    sc={}; refs=[]; on=False
    for a in lines:
        if not a: continue
        if a[0] in ('x_scale','y_scale','z_scale'): sc[a[0][0]]=(int(a[1]),int(a[2]),float(a[3]))
        elif a[0]=='verts': on=True
        elif on and len(a)==9: refs.append(a)
        elif on and len(a)==1 and a[0].isdigit(): refs.append(a)
    Vmh=B['Vfull']  # coords MH em metros
    s={k:abs(Vmh[i][{'x':0,'y':1,'z':2}[k]]-Vmh[j][{'x':0,'y':1,'z':2}[k]])/d for k,(i,j,d) in sc.items()}
    P=[]
    for a in refs:
        if len(a)==1: P.append(Vmh[int(a[0])]); continue
        i=[int(x) for x in a[:3]]; w=[float(x) for x in a[3:6]]; d=np.array([float(x) for x in a[6:9]])
        P.append(sum(w[k]*Vmh[i[k]] for k in range(3))+d*np.array([s['x'],s['y'],s['z']]))
    P=cvn(np.array(P))
    Vo=[];VT=[];Fo=[]
    for l in open('/tmp/sam/mh/eyes/high-poly/high-poly.obj'):
        if l.startswith('vt '): VT.append([float(x) for x in l.split()[1:3]])
        elif l.startswith('f '):
            p=[x.split('/') for x in l.split()[1:]]; Fo.append(([int(q[0])-1 for q in p],[int(q[1])-1 for q in p]))
    return P, [f for f,_ in Fo], [VT[t] for _,ts in Fo for t in ts]
def skin_colors():
    """Cor por vertice: tom base, bochechas, labios, sobrancelha, sombra de barba."""
    base=np.array([0.56,0.31,0.19])
    C=np.tile(base,(len(V),1))
    e=(EYE['L']+EYE['R'])/2
    for s,sx in (('L',1),('R',-1)):
        c=EYE[s]
        # sobrancelha: arco acima do olho
        dx=(V[:,0]-c[0])*sx; arch=0.021+0.006*np.cos(np.clip(dx/0.03,-1.5,1.5))-0.004*(dx>0)*dx/0.03
        d=np.hypot((V[:,2]-(c[2]+arch))/0.0085, dx/0.031)
        front=V[:,1]<c[1]+0.02
        w=np.clip(1.5-d,0,1)*front*(dx>-0.024)
        C=C*(1-0.85*w[:,None])+np.array([0.02,0.015,0.012])*0.85*w[:,None]
        # bochecha
        d=np.hypot((V[:,0]-c[0]-sx*0.01)/0.03,(V[:,2]-c[2]+0.045)/0.025)
        w=np.clip(1-d,0,1)*front*0.25; C=C*(1-w[:,None])+np.array([0.55,0.22,0.16])*w[:,None]
        # palpebra
        d=np.hypot((V[:,0]-c[0])/0.016,(V[:,2]-c[2]-0.004)/0.008); w=np.clip(1-d,0,1)*front*0.35
        C=C*(1-w[:,None])+np.array([0.30,0.16,0.12])*w[:,None]
    # labios
    mz=e[2]-0.072; d=np.hypot(V[:,0]/0.024,(V[:,2]-mz)/0.008); front=V[:,1]<e[1]-0.02
    w=np.clip(1.2-d,0,1)*front*0.6; C=C*(1-w[:,None])+np.array([0.42,0.16,0.13])*w[:,None]
    # barba rala (queixo e mandibula)
    d=((V[:,2]<e[2]-0.075)&(V[:,2]>e[2]-0.14)&(dom=='head')).astype(float)
    w=d*0.12; C=C*(1-w[:,None])+np.array([0.16,0.14,0.14])*w[:,None]
    return np.clip(C,0,1)
