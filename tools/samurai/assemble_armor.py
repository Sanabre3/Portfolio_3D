import bpy, numpy as np, math
from mathutils import Vector, kdtree
from rig import mesh_obj, rigid, add_bone
import armor as A
from land import V, dom, J, JT, B
bones=list(B['bones'])
def plate_obj(name, verts, faces, uvs, mat, arm, bone, thick=0.006, bevel=0.0022, subd=0):
    ob=mesh_obj(name, verts, faces, uvs)
    ob.data.materials.append(mat)
    s=ob.modifiers.new('Solid','SOLIDIFY'); s.thickness=thick; s.offset=1.0; s.use_even_offset=True
    b=ob.modifiers.new('Bevel','BEVEL'); b.width=bevel; b.segments=1; b.limit_method='ANGLE'; b.angle_limit=math.radians(50)
    if subd:
        d=ob.modifiers.new('Sub','SUBSURF'); d.levels=subd; d.render_levels=subd
    rigid(ob, arm, bone)
    # armature depois dos modificadores de forma
    return ob
def cords_obj(name, tubes, mat, arm, bone):
    Vs=[];Fs=[];Us=[];o=0
    for v,f,u in tubes:
        Vs.append(v); Fs+= [tuple(x+o for x in ff) for ff in f]; Us+=u; o+=len(v)
    ob=mesh_obj(name, np.vstack(Vs), Fs, Us); ob.data.materials.append(mat); rigid(ob,arm,bone); return ob

def nearest_weights(ob, arm):
    kd=kdtree.KDTree(len(V))
    for i,p in enumerate(V): kd.insert(Vector(p),i)
    kd.balance()
    for n in bones: ob.vertex_groups.new(name=n)
    for v in ob.data.vertices:
        _,i,_=kd.find(v.co)
        for k in range(4):
            w=B['bw'][i,k]
            if w>1e-4: ob.vertex_groups[bones[B['bi'][i,k]]].add([v.index],float(w),'REPLACE')
    m=ob.modifiers.new('Armature','ARMATURE'); m.object=arm; ob.parent=arm

def build(arm, M):
    out={}
    # ---------------- do (couraca) ----------------
    lames=[]; zt=1.345; H=0.074; ov=0.016
    barrel=None
    tubes=[]
    for i in range(5):
        zb=zt-H
        tht,Rt,yct=A.profile(zt,clearance=0.030); thb,Rb,ycb=A.profile(zb,clearance=0.030)
        ref=A.profile(1.30,clearance=0.030)[1]
        Rt=np.maximum(Rt,ref*0.9); Rb=np.maximum(Rb,ref*0.9)
        Rt+=0.004*i; Rb+=0.004*i+0.006
        v,f,u=A.ring_band(zt,zb,Rt,Rb,yct,ycb,tht,rows=3)
        bone='spine02' if zt>1.24 else ('spine03' if zt>1.17 else 'spine04')
        plate_obj(f'Do_{i}',v,f,u,M['lacq'] if i else M['lacq'],arm,bone)
        # nos cruzados curtos na emenda com a lamela de baixo
        for k in range(14):
            t=-math.pi+(k+0.5)*2*math.pi/14
            r=np.interp(t,thb,Rb,period=2*np.pi)+0.0072
            p0=np.array([math.sin(t)*r, ycb-math.cos(t)*r, zb+0.012])
            tan=np.array([math.cos(t),math.sin(t),0]); up=np.array([0,0,1.])
            tubes.append(A.tube([p0-tan*0.008+up*0.007, p0+tan*0.008-up*0.007],0.0027,5))
            tubes.append(A.tube([p0+tan*0.008+up*0.007, p0-tan*0.008-up*0.007],0.0027,5))
        lames.append((zt,zb)); zt=zb+ov
    cords_obj('DoCords',tubes,M['gold'],arm,'spine02')
    # peitoral e costas (munaita / oshitsuke)
    th,R1,yc1=A.profile(1.335,clearance=0.034); _,R2,yc2=A.profile(1.47,clearance=0.030)
    R1=np.maximum(R1,A.profile(1.30,clearance=0.034)[1]*0.9)+0.012
    v,f,u=A.ring_band(1.475,1.315,R2+0.012,R1,yc2,yc1,th,span=(-1.02,1.02),rows=4)
    plate_obj('Munaita',v,f,u,M['lacq'],arm,'spine02',thick=0.008)
    v,f,u=A.ring_band(1.50,1.315,R2+0.010,R1,yc2,yc1,th,span=(math.pi-1.0,math.pi+1.0),rows=4)
    plate_obj('Oshitsuke',v,f,u,M['lacq'],arm,'spine02',thick=0.008)
    # tiras sobre os ombros (watagami)
    sh=np.isin(dom,['clavicle.L','clavicle.R','spine01','shoulder01.L','shoulder01.R','spine02'])&(V[:,2]<1.555)
    for s,sx in (('L',1),('R',-1)):
        x=0.125*sx; pts=[]
        y_front=yc2-np.interp(math.atan2(x,0.12),th,R2)-0.004; y_back=yc2+np.interp(math.atan2(x,-0.12),th,R2)
        for y in np.linspace(y_front+0.01,y_back-0.01,9):
            m=sh&(abs(V[:,0]-x)<0.02)&(abs(V[:,1]-y)<0.02)
            z=V[m,2].max()+0.016 if m.any() else 1.50
            pts.append((x,y,min(max(z,1.47),1.545)))
        P=np.array(pts); vv=[];ff=[];uu=[]
        for i,p in enumerate(P):
            vv+= [p+np.array([0.026,0,-0.004]), p-np.array([0.026,0,0.004])]
        for i in range(len(P)-1): ff.append((2*i,2*i+1,2*i+3,2*i+2)); uu+=[(0,i*.3),(1,i*.3),(1,(i+1)*.3),(0,(i+1)*.3)]
        plate_obj('Watagami_'+s,np.array(vv),ff,uu,M['lacq'],arm,'spine01',thick=0.007)
        # botoes dourados na ligacao
        for p in (P[0],P[-1]):
            ring=[(p[0]+0.012*math.cos(a), p[1]+ (-0.012 if p is P[0] else 0.012), p[2]-0.012+0.012*math.sin(a)) for a in np.linspace(0,2*math.pi,9)]
    # ---------------- cinto e kusazuri ----------------
    thb,Rb,ycb=A.profile(1.0,clearance=0.028,src=np.isin(dom,A.TORSO))
    _,Rb2,_=A.profile(1.05,clearance=0.028)
    Rbelt=np.maximum(Rb,Rb2)
    v,f,u=A.ring_band(1.055,0.975,Rbelt+0.006,Rbelt+0.01,ycb,ycb,thb,rows=3)
    plate_obj('Belt',v,f,u,M['lacqD'],arm,'spine05',thick=0.007)
    ring=[(math.sin(t)*(np.interp(t,thb,Rbelt)+0.02),ycb-math.cos(t)*(np.interp(t,thb,Rbelt)+0.02),1.016) for t in np.linspace(-math.pi,math.pi,97)]
    cords_obj('BeltCord',[A.tube(ring,0.0045,6)],M['gold'],arm,'spine05')
    panels=[('F',-0.40,0.40,5),('FL',0.36,1.06,5),('L',1.0,1.86,6),('BL',1.8,2.72,5),('B',2.66,3.62,5),('BR',-2.72,-1.8,5),('R',-1.86,-1.0,6),('FR',-1.06,-0.36,5)]
    zb0=0.99; bones_added=[]
    for name,a,b,n in panels:
        mid=(a+b)/2; rmid=np.interp(mid,thb,Rbelt,period=2*np.pi)+0.018
        head=(math.sin(mid)*rmid, ycb-math.cos(mid)*rmid, zb0)
        tail=(math.sin(mid)*(rmid+0.08), ycb-math.cos(mid)*(rmid+0.08), zb0-0.36)
        bn='kusazuri_'+name; add_bone(arm,bn,head,tail,'root',roll_vec=(math.sin(mid),-math.cos(mid),0)); bones_added.append(bn)
        tubes=[]; zt=zb0; Hh=0.082
        for i in range(n):
            zb=zt-Hh; d0=(zb0-zt); d1=(zb0-zb)
            Rt=Rbelt+0.018+d0*0.24+0.004*i; Rbb=Rbelt+0.018+d1*0.24+0.004*i+0.006
            v,f,u=A.ring_band(zt,zb,Rt,Rbb,ycb,ycb,thb,span=(a,b),rows=3)
            plate_obj(f'Kusazuri_{name}_{i}',v,f,u,M['lacq'],arm,bn,thick=0.006)
            # nos dourados no topo de cada placa
            cnt=max(2,int((b-a)*np.interp(mid,thb,Rt,period=2*np.pi)/0.07))
            for k in range(cnt):
                t=a+(k+0.5)*(b-a)/cnt; r=np.interp(t,thb,Rt,period=2*np.pi)+0.0075+ (zb0-zt+0.012)*0.0
                for dz in (0,):
                    p0=np.array([math.sin(t)*r, ycb-math.cos(t)*r, zt-0.012])
                    tan=np.array([math.cos(t),math.sin(t),0])
                    tubes.append(A.tube([p0-tan*0.009+np.array([0,0,0.006]), p0+tan*0.009-np.array([0,0,0.006])],0.0028,5))
                    tubes.append(A.tube([p0+tan*0.009+np.array([0,0,0.006]), p0-tan*0.009-np.array([0,0,0.006])],0.0028,5))
            zt=zb+0.012
        cords_obj(f'KusazuriCords_{name}',tubes,M['gold'],arm,bn)
    out['kusazuri']=bones_added
    # ---------------- sode (ombreiras) ----------------
    for s,sx in (('L',1),('R',-1)):
        bh=np.array(J['upperarm01.'+s]); el=np.array(J['lowerarm01.'+s])
        a=(el-bh)/np.linalg.norm(el-bh)                 # eixo do braco (repouso, em A)
        lat=np.array([sx*1.0,0,0]); lat=lat-a*np.dot(lat,a); lat/=np.linalg.norm(lat)   # lado de fora
        fr=np.cross(a,lat); fr*= -1 if fr[1]>0 else 1  # frente (-Y)
        tubes=[]; st=-0.075; Hh=0.066
        for i in range(5):
            c=bh+a*st+lat*(0.062+0.010*i)
            w=0.25+0.012*i
            v,f,u=A.frame_plate(c, fr, a, lat, w, Hh, bend_r=0.16, rows=3, cols=12, flare=0.01)
            # frame_plate desce em -v; aqui v=a aponta para o cotovelo, entao usamos -a
            v,f,u=A.frame_plate(c, fr, -a, lat, w, Hh, bend_r=0.12, rows=3, cols=14, flare=0.008)
            plate_obj(f'Sode_{s}_{i}',v,f,u,M['lacq'],arm,'upperarm01.'+s,thick=0.006)
            for k in range(4):
                fx=(k+0.5)/4-0.5; ang=fx*w/0.12
                p=c+fr*math.sin(ang)*0.12+lat*((math.cos(ang)-1)*0.12+0.0075)+a*0.012
                tubes.append(A.tube([p-fr*0.009-a*0.006,p+fr*0.009+a*0.006],0.0026,5))
                tubes.append(A.tube([p+fr*0.009-a*0.006,p-fr*0.009+a*0.006],0.0026,5))
            st+=Hh-0.012
        cords_obj('SodeCords_'+s,tubes,M['gold'],arm,'upperarm01.'+s)
        # kote: faixas laqueadas no antebraco (logo abaixo do cotovelo e no punho)
        wr=np.array(J['wrist.'+s]); fa=(wr-el)/np.linalg.norm(wr-el)
        for nm,t0,t1,bone in (('elbow',0.02,0.16,'lowerarm01.'+s),('cuff',0.78,0.95,'lowerarm02.'+s)):
            L=np.linalg.norm(wr-el); rows=[]
            vv=[];ff=[];uu=[]; nseg=20
            e1=np.cross(fa,[0,0,1.]); e1/=np.linalg.norm(e1); e2=np.cross(fa,e1)
            for j,t in enumerate((t0,t1)):
                c=el+fa*L*t
                m=np.isin(dom,['lowerarm01.'+s,'lowerarm02.'+s,'wrist.'+s])&(abs((V-c)@fa)<0.015)
                d=V[m]-c; d-=np.outer(d@fa,fa); r=np.linalg.norm(d,axis=1).max()+0.009
                for k in range(nseg):
                    ang=2*math.pi*k/nseg; vv.append(c+(e1*math.cos(ang)+e2*math.sin(ang))*r*(1+0.04*j))
            for k in range(nseg):
                ff.append((k,(k+1)%nseg,nseg+(k+1)%nseg,nseg+k)); uu+=[(k/nseg,0),((k+1)/nseg,0),((k+1)/nseg,1),(k/nseg,1)]
            plate_obj(f'Kote_{nm}_{s}',np.array(vv),ff,uu,M['lacq'],arm,bone,thick=0.006)
    # ---------------- gola alta ----------------
    nk=np.isin(dom,['neck01','neck02','spine01'])
    vv=[];ff=[];uu=[]; nseg=32; zs=[1.545,1.585,1.625,1.648]
    for j,z in enumerate(zs):
        m=nk&(abs(V[:,2]-z)<0.012); P=V[m]; yc=(P[:,1].min()+P[:,1].max())/2
        th=np.arctan2(P[:,0],-(P[:,1]-yc)); r=np.hypot(P[:,0],P[:,1]-yc)
        for k in range(nseg):
            t=-math.pi+2*math.pi*k/nseg; sel=abs(((th-t+math.pi)%(2*math.pi))-math.pi)<0.35
            rr=(r[sel].max() if sel.any() else r.max())+0.013+0.004*j
            vv.append((math.sin(t)*rr, yc-math.cos(t)*rr, z))
    for j in range(len(zs)-1):
        for k in range(nseg):
            a=j*nseg+k; b=j*nseg+(k+1)%nseg; ff.append((a,b,b+nseg,a+nseg)); uu+=[(k/nseg*6,j*.5),((k+1)/nseg*6,j*.5),((k+1)/nseg*6,(j+1)*.5),(k/nseg*6,(j+1)*.5)]
    col=mesh_obj('Collar',np.array(vv),ff,uu); col.data.materials.append(M['cloth'])
    sm=col.modifiers.new('Solid','SOLIDIFY'); sm.thickness=0.006; sm.offset=1
    nearest_weights(col, arm)
    return out
