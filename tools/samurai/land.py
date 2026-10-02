import numpy as np
B=dict(np.load('/tmp/sam/body.npz',allow_pickle=True))
def cvn(p): p=np.asarray(p,float); return np.stack([p[...,0],-p[...,2],p[...,1]],-1)
V=cvn(B['V']); bones=list(B['bones']); H=cvn(B['H']); T=cvn(B['T'])
dom=np.array([bones[i] for i in B['bi'][:,0]])
J={b:H[i] for i,b in enumerate(bones)}; JT={b:T[i] for i,b in enumerate(bones)}
if __name__=='__main__':
    for b in ['root','spine05','spine04','spine03','spine02','spine01','neck01','neck02','neck03','head','clavicle.L','shoulder01.L','upperarm01.L','lowerarm01.L','wrist.L','pelvis.L','upperleg01.L','lowerleg01.L','lowerleg02.L','foot.L','toe.L']:
        m=dom==b; print(f'{b:14s} head {np.round(J[b],3)} tail {np.round(JT[b],3)} n={m.sum()} z[{V[m,2].min() if m.any() else 0:.2f},{V[m,2].max() if m.any() else 0:.2f}]')
    # secao do torso
    for z in [0.95,1.0,1.1,1.2,1.3,1.4,1.45]:
        m=(abs(V[:,2]-z)<0.01)&np.isin(dom,['spine05','spine04','spine03','spine02','spine01','root','pelvis.L','pelvis.R','clavicle.L','clavicle.R'])
        print(z, 'x', np.round([V[m,0].min(),V[m,0].max()],3),'y',np.round([V[m,1].min(),V[m,1].max()],3))
