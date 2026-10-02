# Pecas rigidas da armadura construidas sobre o perfil real do corpo.
import numpy as np, math
from land import V, dom, J, JT
TORSO=['spine05','spine04','spine03','spine02','spine01','root','pelvis.L','pelvis.R','upperleg01.L','upperleg01.R','clavicle.L','clavicle.R','neck01']
tm=np.isin(dom,TORSO)
def profile(z, nth=64, band=0.02, yc=None, clearance=0.0, smooth=6, src=None):
    """Raio maximo do corpo por angulo em torno de (0,yc) na altura z. theta=0 -> frente (-Y), +pi/2 -> esquerda (+X)."""
    m=(src if src is not None else tm)&(abs(V[:,2]-z)<band)
    P=V[m]
    if yc is None: yc=(P[:,1].min()+P[:,1].max())/2
    th=np.arctan2(P[:,0],-(P[:,1]-yc)); r=np.hypot(P[:,0],P[:,1]-yc)
    bins=np.linspace(-np.pi,np.pi,nth+1); R=np.zeros(nth)
    for i in range(nth):
        s=(th>=bins[i])&(th<bins[i+1]); R[i]=r[s].max() if s.any() else 0
    # preenche buracos e suaviza (circular)
    for _ in range(3):
        z0=R==0; R[z0]=np.maximum(np.roll(R,1),np.roll(R,-1))[z0]
    smooth=max(3,smooth*2//3); k=np.ones(smooth)/smooth
    for _ in range(3): R=np.maximum(R, np.convolve(np.r_[R[-smooth:],R,R[:smooth]],k,'same')[smooth:-smooth]*0+R)
    Rs=np.convolve(np.r_[R[-smooth:],R,R[:smooth]],k,'same')[smooth:-smooth]
    R=np.maximum(R,Rs)
    Rs=np.convolve(np.r_[R[-smooth:],R,R[:smooth]],k,'same')[smooth:-smooth]
    return (bins[:-1]+bins[1:])/2, Rs+clearance, yc

def ring_band(zt, zb, Rt, Rb, yct, ycb, th, span=None, rows=3, flare=0.0):
    """Faixa (lamela) entre duas alturas. span=(a,b) em rad para faixa parcial (frente/costas)."""
    if span is None: ths=np.linspace(-np.pi,np.pi,len(th)+1); closed=True
    else: ths=np.linspace(span[0],span[1],max(8,int(len(th)*(span[1]-span[0])/(2*np.pi))+2)); closed=False
    def R_at(Rv,t): return np.interp((t+np.pi)%(2*np.pi)-np.pi, th, Rv, period=2*np.pi)
    verts=[];uv=[]
    n=len(ths)-(1 if closed else 0)
    for j in range(rows):
        f=j/(rows-1); z=zt+(zb-zt)*f; yc=yct+(ycb-yct)*f
        for t in ths[:n]:
            r=R_at(Rt,t)*(1-f)+R_at(Rb,t)*f + flare*f**2
            verts.append((math.sin(t)*r, yc-math.cos(t)*r, z))
    # uv por comprimento de arco
    faces=[]
    for j in range(rows-1):
        for i in range(n if closed else n-1):
            a=j*n+i; b=j*n+(i+1)%n; faces.append((a,b,b+n,a+n))
    V_=np.array(verts)
    uvs=[]
    for f in faces:
        for vi in f:
            p=V_[vi]; t=math.atan2(p[0],-(p[1]-yct)); uvs.append((t*0.2*8, p[2]*8))
    return V_,faces,uvs

def tube(points, radius, sides=6, closed=False):
    P=np.array(points); verts=[]; faces=[]; uvs=[]
    n=len(P); up=np.array([0,0,1.])
    for i in range(n):
        d=P[min(i+1,n-1)]-P[max(i-1,0)]; d/=np.linalg.norm(d)+1e-9
        a=np.cross(d,up);
        if np.linalg.norm(a)<1e-3: a=np.cross(d,[1,0,0])
        a/=np.linalg.norm(a); b=np.cross(d,a)
        r=radius(i/(n-1)) if callable(radius) else radius
        for k in range(sides):
            ang=2*math.pi*k/sides; verts.append(P[i]+(a*math.cos(ang)+b*math.sin(ang))*r)
    for i in range(n-1):
        for k in range(sides):
            a=i*sides+k; b=i*sides+(k+1)%sides; faces.append((a,b,b+sides,a+sides))
            uvs += [(k/sides,i*0.3),((k+1)/sides,i*0.3),((k+1)/sides,(i+1)*0.3),(k/sides,(i+1)*0.3)]
    return np.array(verts),faces,uvs

def frame_plate(center, u, v, w, width, height, bend_r, rows=3, cols=10, flare=0.0):
    """Placa curva: arco em torno do eixo v (altura). u=direcao lateral, w=normal para fora."""
    verts=[];faces=[];uvs=[]
    for j in range(rows):
        fy=j/(rows-1)
        for i in range(cols):
            fx=i/(cols-1)-0.5; ang=fx*width/bend_r
            p=center + u*math.sin(ang)*bend_r + w*(math.cos(ang)-1)*bend_r - v*fy*height + w*flare*fy**2
            verts.append(p)
    for j in range(rows-1):
        for i in range(cols-1):
            a=j*cols+i; faces.append((a,a+1,a+cols+1,a+cols))
    for f in faces:
        for vi in f: uvs.append(((vi%cols)/cols*width*8,(vi//cols)/rows*height*8))
    return np.array(verts),faces,uvs
