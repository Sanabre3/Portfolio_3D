# Converte a malha base CC0 do MakeHuman (hm08) em um corpo masculino atletico,
# com esqueleto de jogo reduzido e pesos colapsados. Saida: body.npz
import json, numpy as np
D='mh/'
V=[];VT=[];F=[];FT=[];grp=[];cur=None
for l in open(D+'3dobjs/base.obj'):
    if l.startswith('v '): V.append([float(x) for x in l.split()[1:4]])
    elif l.startswith('vt '): VT.append([float(x) for x in l.split()[1:3]])
    elif l.startswith('g '): cur=l.split()[1]
    elif l.startswith('f '):
        p=[x.split('/') for x in l.split()[1:]]
        F.append([int(a[0])-1 for a in p]); FT.append([int(a[1])-1 for a in p]); grp.append(cur)
V=np.array(V); VT=np.array(VT)
def target(path,w):
    for l in open(D+'targets/macrodetails/'+path):
        if l[0]=='#' or not l.strip(): continue
        a=l.split(); V[int(a[0])]+=w*np.array([float(x) for x in a[1:4]])
target('asian-male-young.target',1.0)
target('universal-male-young-maxmuscle-averageweight.target',0.6)
target('height/male-young-averagemuscle-averageweight-maxheight.target',0.3)

sk=json.load(open(D+'rigs/default.mhskel'))
J={k:V[v].mean(0) for k,v in sk['joints'].items()}
bones=sk['bones']
W=json.load(open(D+'rigs/default_weights.mhw'))['weights']

keep=['root','spine05','spine04','spine03','spine02','spine01','neck01','neck02','neck03','head','jaw']
for s in 'LR':
    keep+=[b+'.'+s for b in ['clavicle','shoulder01','upperarm01','upperarm02','lowerarm01','lowerarm02','wrist',
        'finger1-1','finger1-2','finger1-3']+[f'finger{i}-{j}' for i in range(2,6) for j in (1,2,3)]+
        ['pelvis','upperleg01','upperleg02','lowerleg01','lowerleg02','foot']]
def target_bone(b):
    if b.startswith('toe') : return 'toe.'+b[-1]
    while b not in keep: b=bones[b]['parent']
    return b
head={b:J[bones[b]['head']] for b in bones}; tail={b:J[bones[b]['tail']] for b in bones}
out_b=keep+['toe.L','toe.R']
H={b:head[b] for b in keep}; T={b:tail[b] for b in keep}
for s in 'LR':
    hs=[head[f'toe{i}-1.{s}'] for i in range(1,6)]; ts=[tail[f'toe{i}-1.{s}'] for i in range(1,6)]
    H['toe.'+s]=np.mean(hs,0); T['toe.'+s]=np.mean(ts,0)+ (np.mean(ts,0)-np.mean(hs,0))*1.5
par={b:(None if bones[b]['parent'] is None else target_bone(bones[b]['parent'])) for b in keep}
par['toe.L']='foot.L'; par['toe.R']='foot.R'
# plano de rotacao -> normal (para o roll do osso)
def pn(b):
    p=[J[x] for x in sk['planes'][bones[b]['rotation_plane']]]
    n=np.cross(p[1]-p[0],p[2]-p[1]); return n/ (np.linalg.norm(n)+1e-9)
N={b:pn(b) for b in keep}; N['toe.L']=N['foot.L']; N['toe.R']=N['foot.R']
# pesos colapsados
Wd={}
for b,lst in W.items():
    tb=target_bone(b)
    for vi,w in lst: Wd.setdefault(vi,{}); Wd[vi][tb]=Wd[vi].get(tb,0)+w
# so a malha do corpo
body=[i for i,g in enumerate(grp) if g=='body']
used=sorted({v for i in body for v in F[i]}); remap={v:i for i,v in enumerate(used)}
BF=[[remap[v] for v in F[i]] for i in body]; BFT=[FT[i] for i in body]
S=0.1  # decimetro -> metro
BV=V[used]*S
# chao em y=0
y0=BV[:,1].min(); BV[:,1]-=y0
bi=np.zeros((len(used),4),int); bw=np.zeros((len(used),4))
for new,old in enumerate(used):
    d=sorted(Wd.get(old,{'root':1}).items(),key=lambda x:-x[1])[:4]; s=sum(w for _,w in d)
    for k,(b,w) in enumerate(d): bi[new,k]=out_b.index(b); bw[new,k]=w/s
sh=lambda P: (P*S - np.array([0,y0,0]))
np.savez('body.npz',V=BV,F=np.array(BF,dtype=object),FT=np.array(BFT,dtype=object),VT=VT,bi=bi,bw=bw,
  bones=np.array(out_b),H=np.array([sh(H[b]) for b in out_b]),T=np.array([sh(T[b]) for b in out_b]),
  N=np.array([N[b] for b in out_b]),par=np.array([par[b] or '' for b in out_b]),
  old_index=np.array(used), Vfull=(V*S-np.array([0,y0,0])))
print('verts',len(BV),'faces',len(BF),'height',BV[:,1].max(),'bones',len(out_b))
print('head y',sh(H['head'])[1],'wrist L',sh(H['wrist.L']), 'foot',sh(H['foot.L']))
