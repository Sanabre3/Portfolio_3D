# Camadas de roupa derivadas da propria topologia do corpo: mesma malha, deslocada.
# Por compartilhar vertices com o corpo, herdam os pesos exatos e deformam sem esticar.
import numpy as np, math
from land import V, bones, dom, J, JT, B
F=[list(f) for f in B['F']]; FT=[list(f) for f in B['FT']]; VT=B['VT']
bi=B['bi']; bw=B['bw']
def vnormals(V,F):
    N=np.zeros_like(V)
    for f in F:
        p=V[f]; n=np.cross(p[1]-p[0],p[2]-p[0]);
        if len(f)==4: n+=np.cross(p[2]-p[0],p[3]-p[0])
        N[f]+=n
    return N/ (np.linalg.norm(N,axis=1,keepdims=True)+1e-9)
N=vnormals(V,F)
def isin(names): return np.isin(dom,names)
SPINE=['spine05','spine04','spine03','spine02','spine01','root']
ARM=lambda s:[b+'.'+s for b in ['clavicle','shoulder01','upperarm01','upperarm02','lowerarm01','lowerarm02']]
LEG=lambda s:[b+'.'+s for b in ['pelvis','upperleg01','upperleg02','lowerleg01','lowerleg02']]
def sstep(a,b,x): t=np.clip((x-a)/(b-a),0,1); return t*t*(3-2*t)

def layer(mask, newV, uvscale=1.0, uvfn=None):
    """Extrai faces com todos os vertices em mask. Devolve verts, faces, uvs por canto, bi, bw, indices originais."""
    fs=[i for i,f in enumerate(F) if mask[f].all()]
    used=sorted({v for i in fs for v in F[i]}); rm={v:k for k,v in enumerate(used)}
    faces=[[rm[v] for v in F[i]] for i in fs]
    if uvfn is None: uvs=[VT[t]*uvscale for i in fs for t in FT[i]]
    else: uvs=[uvfn(v) for i in fs for v in F[i]]
    return dict(V=newV[used],F=faces,UV=uvs,bi=bi[used],bw=bw[used],idx=np.array(used),faces_src=fs)

def gi():
    m=(isin(SPINE+['neck01','neck02']+ARM('L')+ARM('R')) & (V[:,2]>0.88)) | (isin(['upperarm01.L','upperarm01.R']))
    m &= ~((dom=='neck01')&(V[:,2]>1.635)) & ~(dom=='neck02')
    off=np.where(isin(['neck01']),0.013,0.010)
    off=off+np.where(isin(ARM('L')+ARM('R')),0.004,0)
    return layer(m, V+N*off[:,None], uvscale=38)

def hakama():
    z=V[:,2]
    m=isin(LEG('L')+LEG('R')+['spine05','root']) & (z<1.10) & (z>0.235)
    out=V.copy()
    for s,sx in (('L',1),('R',-1)):
        hip=J['upperleg01.'+s]; ank=J['foot.'+s]
        sel=m&((V[:,0]*sx)>-0.02)
        p=V[sel]; t=np.clip((hip[2]-p[:,2])/(hip[2]-ank[2]),0,1)
        axis=hip[None,:]+(ank-hip)[None,:]*t[:,None]
        r=p-axis; r[:,2]=0; rl=np.linalg.norm(r,axis=1,keepdims=True)+1e-6; rd=r/rl
        # centro do tronco para a parte alta
        rt=p.copy(); rt[:,1]-=0.0; rt[:,0]-=0; rt[:,2]=0; rtl=np.linalg.norm(rt,axis=1,keepdims=True)+1e-6; rtd=rt/rtl
        wl=sstep(0.97,0.86,p[:,2])[:,None]
        d=rd*wl+rtd*(1-wl); d/=np.linalg.norm(d,axis=1,keepdims=True)+1e-9
        zz=p[:,2]
        E=np.interp(zz,[0.235,0.27,0.33,0.40,0.53,0.66,0.80,0.90,1.10],[0.022,0.05,0.085,0.095,0.085,0.06,0.028,0.012,0.010])
        inward=np.clip(-d[:,0]*sx,0,1)       # lado voltado para a outra perna
        E=E*(1-0.7*inward**1.5)*(wl[:,0]*1+ (1-wl[:,0])*1)
        th=np.arctan2(d[:,0]*sx,-d[:,1])
        pleat=0.012*(0.5-0.5*np.cos(th*9))*sstep(0.85,0.5,zz)
        out[sel]=p+d*(E+pleat)[:,None]+N[sel]*0.008
    return layer(m,out,uvscale=38)

def kyahan():
    z=V[:,2]; m=isin(['lowerleg01.L','lowerleg01.R','lowerleg02.L','lowerleg02.R','foot.L','foot.R'])&(z>0.075)&(z<0.36)
    def uv(v):
        s='L' if V[v,0]>0 else 'R'; c=J['lowerleg02.'+s]
        a=math.atan2(V[v,0]-c[0],V[v,1]-c[1]); return (a/(2*math.pi)*6, V[v,2]*18)
    return layer(m, V+N[:,None][:,0]*0.009, uvfn=uv)

def tabi():
    z=V[:,2]; m=isin(['foot.L','foot.R','toe.L','toe.R','lowerleg02.L','lowerleg02.R'])&(z<0.11)
    return layer(m, V+N*0.0045, uvscale=38)

def gloves():
    m=isin(['wrist.L','wrist.R','lowerarm02.L','lowerarm02.R'])
    for s in 'LR':
        # corta antes dos nos dos dedos
        w=J['wrist.'+s]; k=np.mean([J[f'finger{f}-1.{s}'] for f in range(2,6)],0)
        ax=(k-w)/np.linalg.norm(k-w); t=(V-w)@ax
        m&=~(((dom=='wrist.'+s))&(t>np.linalg.norm(k-w)*0.9))
    m&=~isin([f'finger1-{j}.{s}' for s in 'LR' for j in (2,3)])
    return layer(m, V+N*0.0032, uvscale=38)

def hidden_body_faces(covers):
    """Faces do corpo totalmente escondidas por roupa -> removidas (evita atravessar e economiza triangulos)."""
    hide=set()
    for L,keep_border in covers:
        src=set(L['faces_src'])
        vs=np.zeros(len(V),bool); vs[L['idx']]=True
        # borda da camada: vertices de faces fora dela
        border=np.zeros(len(V),bool)
        for i,f in enumerate(F):
            if i not in src and vs[f].any(): border[f]=True
        for i in src:
            if not border[F[i]].any(): hide.add(i)
    return hide
