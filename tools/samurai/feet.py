# Sandalias: sola sob cada pe e tiras vermelhas saindo do vao entre os dedos.
import numpy as np, math
from land import V, dom
import armor as A
def hull(pts):
    pts=sorted(map(tuple,pts))
    def cross(o,a,b): return (a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0])
    lo=[];up=[]
    for p in pts:
        while len(lo)>=2 and cross(lo[-2],lo[-1],p)<=0: lo.pop()
        lo.append(p)
    for p in reversed(pts):
        while len(up)>=2 and cross(up[-2],up[-1],p)<=0: up.pop()
        up.append(p)
    return np.array(lo[:-1]+up[:-1])
def sandals():
    out=[]
    for s,sx in (('L',1),('R',-1)):
        m=np.isin(dom,['foot.'+s,'toe.'+s])&(V[:,2]<0.035)
        P=V[m]; h=hull(P[:,:2]); c=h.mean(0)
        ang=np.arctan2(h[:,1]-c[1],h[:,0]-c[0]); o=np.argsort(ang); h=h[o]; ang=ang[o]
        T=np.linspace(-math.pi,math.pi,40,endpoint=False)
        rr=np.interp(T,ang,np.hypot(h[:,0]-c[0],h[:,1]-c[1]),period=2*math.pi)+0.009
        ring=np.c_[c[0]+np.cos(T)*rr, c[1]+np.sin(T)*rr]
        verts=[];faces=[];uvs=[]; n=len(ring)
        for z in (0.0,0.016):
            for p in ring: verts.append((p[0],p[1],z))
        verts.append((c[0],c[1],0.0)); verts.append((c[0],c[1],0.016))
        for i in range(n):
            j=(i+1)%n; faces.append((i,j,n+j,n+i)); faces.append((2*n,j,i)); faces.append((2*n+1,n+i,n+j))
        for f in faces:
            for vi in f: uvs.append((verts[vi][0]*10,verts[vi][1]*10))
        out.append(('Sole_'+s,np.array(verts),faces,uvs,'sole'))
        toes=V[np.isin(dom,['toe.'+s])]
        x0=toes[:,0].min() if sx>0 else toes[:,0].max(); x1=toes[:,0].max() if sx>0 else toes[:,0].min()
        gx=x0+(x1-x0)*0.3; gy=toes[:,1].min()+0.03
        A_=np.array([gx,gy,0.02]); tubes=[]
        for side in (0,1):
            bx=(toes[:,0].min()-0.004) if side==0 else (toes[:,0].max()+0.004)
            Bp=np.array([bx, gy+0.075, 0.018]); pts=[]
            for t in np.linspace(0,1,8):
                p=A_*(1-t)+Bp*t
                mm=np.isin(dom,['foot.'+s,'toe.'+s])&(np.hypot(V[:,0]-p[0],V[:,1]-p[1])<0.012)
                ztop=V[mm,2].max()+0.007 if mm.any() else p[2]
                if 0.05<t<0.95: p[2]=max(p[2],ztop)
                pts.append(p.copy())
            tubes.append(A.tube(pts,0.0045,6))
        out.append(('Strap_'+s,tubes,None,None,'sandal'))
    return out
