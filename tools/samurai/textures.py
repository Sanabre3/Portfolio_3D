# Texturas procedurais tileaveis (numpy -> PNG).
import numpy as np
from PIL import Image
R=np.random.default_rng(7)
def save(a,name,mode='RGB'):
    a=np.clip(a,0,1); Image.fromarray((a*255).astype(np.uint8),mode).save('/tmp/sam/tex/'+name); return '/tmp/sam/tex/'+name
def fnoise(n, scale, octaves=4, seed=0):
    """ruido fractal periodico via FFT"""
    rng=np.random.default_rng(seed); acc=np.zeros((n,n))
    for o in range(octaves):
        f=scale*2**o; k=np.fft.fftfreq(n)*n
        kx,ky=np.meshgrid(k,k); r=np.sqrt(kx**2+ky**2)+1e-6
        spec=(rng.normal(size=(n,n))+1j*rng.normal(size=(n,n)))*np.exp(-(r/f)**2)*(r>0.5)
        a=np.real(np.fft.ifft2(spec)); a=(a-a.mean())/(a.std()+1e-9); acc+=a/(2**o)
    return acc/np.abs(acc).max()
def height_to_normal(h, strength):
    gx=(np.roll(h,-1,1)-np.roll(h,1,1))*0.5*strength; gy=(np.roll(h,-1,0)-np.roll(h,1,0))*0.5*strength
    n=np.stack([-gx,gy,np.ones_like(h)],-1); n/=np.linalg.norm(n,axis=-1,keepdims=True)
    return n*0.5+0.5
def build():
    out={}
    n=512; y,x=np.mgrid[0:n,0:n]/n
    k=48; wx=np.sin(2*np.pi*k*x); wy=np.sin(2*np.pi*k*y)
    over=(np.floor(k*x)+np.floor(k*y))%2
    h=np.where(over>0, np.abs(wx)**0.6, np.abs(wy)**0.6)*0.7 + fnoise(n,40,3,1)*0.25 + fnoise(n,6,2,2)*0.08
    out['fabric_n']=save(height_to_normal(h,2.2),'fabric_n.png')
    out['fabric_c']=save(np.repeat((0.80+0.20*h/h.max())[...,None],3,-1),'fabric_c.png')
    h=fnoise(n,30,3,3)*0.3
    for i in range(60):
        x0,y0=R.random(2); a=R.random()*np.pi; L=0.05+R.random()*0.2
        t=np.linspace(0,1,400); px=((x0+np.cos(a)*L*t)*n).astype(int)%n; py=((y0+np.sin(a)*L*t)*n).astype(int)%n
        h[py,px]-=0.6*R.random()
    out['lacquer_n']=save(height_to_normal(h,1.2),'lacquer_n.png')
    h=fnoise(n,70,3,4)*0.6 - (fnoise(n,120,1,5)>0.55)*0.5
    out['skin_n']=save(height_to_normal(h,1.6),'skin_n.png')
    m=1024; yy,xx=np.mgrid[0:m,0:256]; xx=xx/256.
    n1=fnoise(256,4,2,6); n2=fnoise(256,2,1,7)
    g=np.sin((xx*6+n1[np.arange(m)%256]*0.8+ n2[(np.arange(m)//4)%256]*0.5)*2*np.pi*3)
    base=np.array([0.20,0.11,0.06]); dark=np.array([0.10,0.05,0.03]); t=(g*0.5+0.5)[...,None]
    wood=base*(1-t)+dark*t; wood*=(0.9+0.1*fnoise(256,30,2,8)[np.arange(m)%256])[...,None]
    out['wood_c']=save(wood**(1/2.2),'wood_c.png'); out['wood_n']=save(height_to_normal(g*0.3,1.0),'wood_n.png')
    d=(x+y)*14; band=np.abs(np.sin(np.pi*d))**0.5; h=band*0.8+fnoise(n,60,2,9)*0.2
    out['wrap_n']=save(height_to_normal(h,3.0),'wrap_n.png'); out['wrap_c']=save(np.repeat((0.7+0.3*band)[...,None],3,-1),'wrap_c.png')
    d=(x*3+y*10); h=np.abs(np.sin(np.pi*d))**0.7; out['cord_n']=save(height_to_normal(h,3.0),'cord_n.png')
    hs=np.sin(x*2*np.pi*90+fnoise(n,8,2,11)*3)*0.5 + fnoise(n,50,2,12)*0.5
    hs=np.tile(hs[:1,:],(n,1))*0.7+fnoise(n,20,2,13)*0.1; out['hair_n']=save(height_to_normal(hs,2.0),'hair_n.png')
    h=np.tile(fnoise(n,80,2,14)[:1,:],(n,1))*0.4+fnoise(n,40,2,15)*0.1; out['steel_n']=save(height_to_normal(h,0.8),'steel_n.png')
    # olho: layout do high-poly do MakeHuman -> iris no centro de cada circulo UV
    e=1024; yy,xx=np.mgrid[0:e,0:e]; u=xx/e; v=1-yy/e
    col=np.zeros((e,e,3)); col[:]=np.array([0.90,0.87,0.84]); fn=fnoise(e,12,2,16)
    for cu,cv_ in ((0.287,0.306),(0.712,0.706)):
        r=np.hypot(u-cu,v-cv_); th=np.arctan2(v-cv_,u-cu)
        vein=np.clip((r-0.19)/0.07,0,1)[...,None]*np.array([0,0.10,0.12]); mm=r<0.26; col[mm]-=vein[mm]
        fib=0.5+0.5*np.sin(th*90+fn*5)
        iris=np.array([0.20,0.115,0.06])[None,None,:]*(0.55+0.7*fib[...,None])*(1.25-np.clip(r,0,0.16)[...,None]/0.16*0.5)
        mi=r<0.152; col[mi]=iris[mi]; ring=(r>0.132)&(r<0.160); col[ring]*=0.45; col[r<0.052]=0.015
    out['eye_c']=save(col,'eye_c.png')
    return out
if __name__=='__main__': print(len(build()))
