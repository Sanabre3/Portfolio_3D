# Yari: haste de madeira, empunhaduras, colar de latao, lamina de secao em losango, borla e ponteira.
import numpy as np, math
def cyl(z0,z1,r0,r1,sides=16,rings=2,uvk=(1,1)):
    V=[];F=[];U=[]
    for j in range(rings):
        t=j/(rings-1); z=z0+(z1-z0)*t; r=r0+(r1-r0)*t
        for k in range(sides):
            a=2*math.pi*k/sides; V.append((math.cos(a)*r,math.sin(a)*r,z))
    for j in range(rings-1):
        for k in range(sides):
            a=j*sides+k; b=j*sides+(k+1)%sides; F.append((a,b,b+sides,a+sides))
            U+=[(k/sides*uvk[0],(z0+(z1-z0)*j/(rings-1))*uvk[1]),((k+1)/sides*uvk[0],(z0+(z1-z0)*j/(rings-1))*uvk[1]),((k+1)/sides*uvk[0],(z0+(z1-z0)*(j+1)/(rings-1))*uvk[1]),(k/sides*uvk[0],(z0+(z1-z0)*(j+1)/(rings-1))*uvk[1])]
    # tampas
    c0=len(V); V.append((0,0,z0)); c1=len(V); V.append((0,0,z1))
    for k in range(sides):
        F.append((c0,(k+1)%sides,k)); U+=[(0.5,0.5)]*3
        o=(rings-1)*sides; F.append((c1,o+k,o+(k+1)%sides)); U+=[(0.5,0.5)]*3
    return np.array(V),F,U
def blade(z0,L,w,th,n=10):
    V=[];F=[];U=[]
    for j in range(n):
        t=j/(n-1); ww=w*(1-t**1.3)*(1+0.25*math.sin(t*math.pi)*(t<0.3))+0.0004; tt=th*(1-t)+0.0003
        z=z0+L*t
        for (x,y) in ((ww,0),(0,tt),(-ww,0),(0,-tt)): V.append((x,y,z))
    for j in range(n-1):
        for k in range(4):
            a=j*4+k; b=j*4+(k+1)%4; F.append((a,b,b+4,a+4)); U+=[(k/4,j/(n-1)),((k+1)/4,j/(n-1)),((k+1)/4,(j+1)/(n-1)),(k/4,(j+1)/(n-1))]
    V.append((0,0,z0)); c=len(V)-1
    for k in range(4): F.append((c,(k+1)%4,k)); U+=[(0.5,0)]*3
    V.append((0,0,z0+L+0.002)); c=len(V)-1; o=(n-1)*4
    for k in range(4): F.append((c,o+k,o+(k+1)%4)); U+=[(0.5,1)]*3
    return np.array(V),F,U
def tassel(z, n=22, L=0.15, rng=np.random.default_rng(5)):
    V=[];F=[];U=[]
    for i in range(n):
        a=2*math.pi*i/n+rng.normal(0,0.1); r=0.018+rng.random()*0.004
        top=np.array([math.cos(a)*r,math.sin(a)*r,z]); ll=L*(0.8+0.3*rng.random())
        pts=[top+np.array([math.cos(a)*0.01*s, math.sin(a)*0.01*s, -ll*s]) for s in np.linspace(0,1,5)]
        for j,p in enumerate(pts):
            for k in range(4):
                b=2*math.pi*k/4; rr=0.0028*(1-j/5)+0.0006
                V.append(p+np.array([math.cos(b)*rr,math.sin(b)*rr,0]))
        o=i*20
        for j in range(4):
            for k in range(4):
                a_=o+j*4+k; b_=o+j*4+(k+1)%4; F.append((a_,b_,b_+4,a_+4)); U+=[(0,0),(1,0),(1,1),(0,1)]
    return np.array(V),F,U
def parts(r=0.0165, z_butt=0.0, z_top=2.12):
    P={}
    P['shaft']=cyl(z_butt+0.06, z_top, r*1.02, r*0.94, 16, 12, (1,0.8))
    P['butt']=cyl(z_butt, z_butt+0.065, r*1.12, r*1.08, 16, 3)
    P['collar']=cyl(z_top-0.01, z_top+0.07, r*1.22, r*1.1, 16, 3)
    P['collar2']=cyl(z_top-0.06, z_top-0.035, r*1.18, r*1.18, 16, 2)
    P['blade']=blade(z_top+0.07, 0.36, 0.025, 0.008)
    P['knot']=cyl(z_top-0.105, z_top-0.065, r*1.35, r*1.5, 12, 3)
    P['tassel']=tassel(z_top-0.08)
    return P
