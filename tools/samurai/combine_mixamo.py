# Junta o personagem do Mixamo + animacoes num GLB so, com clipes no lugar (in place),
# um ciclo de caminhada extraido do "Start Walking" e (opcional) a lanca presa nas costas.
import bpy, sys, os, math, json, numpy as np
# Parametros por variavel de ambiente (padrao = personagem atual):
#   MX_FBX   personagem exportado do Mixamo (T-pose, com skin)
#   MX_OUT   nome do .glb gerado
#   MX_LANCA 0 = sem lanca/borla/alca (avatar dev)
# Ex.: MX_FBX=dev_mixamo.fbx MX_OUT=dev.glb MX_LANCA=0 python3.11 combine_mixamo.py
ENTRADA=os.environ.get('MX_FBX','personagem_cabelo_curto_mixamo1.fbx')
SAIDA=os.environ.get('MX_OUT','personagem.glb')
LANCA=os.environ.get('MX_LANCA','1')!='0'
sys.path.insert(0,'/tmp/sam')
from mathutils import Vector, Quaternion, Matrix
D='/tmp/mx5/'; P='mixamorig:'
bpy.ops.wm.read_factory_settings(use_empty=True); bpy.context.scene.render.fps=30
bpy.ops.import_scene.fbx(filepath=D+ENTRADA)
tgt=[o for o in bpy.context.scene.objects if o.type=='ARMATURE'][0]; tgt.name='Personagem'
mesh=[o for o in bpy.context.scene.objects if o.type=='MESH'][0]
for o in list(bpy.context.scene.objects):
    if o.type not in ('ARMATURE','MESH'): bpy.data.objects.remove(o)
for a in list(bpy.data.actions): bpy.data.actions.remove(a)

def sample(path):
    """Importa a animacao e le, quadro a quadro, rotacao local de cada osso e posicao do quadril."""
    before=set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=D+path)
    new=[o for o in bpy.data.objects if o not in before]
    src=[o for o in new if o.type=='ARMATURE'][0]
    act=src.animation_data.action; f0,f1=map(int,act.frame_range)
    names=[b.name for b in src.pose.bones]
    R=[];L=[];W=[]
    for f in range(f0,f1+1):
        bpy.context.scene.frame_set(f)
        R.append([tuple(src.pose.bones[n].rotation_quaternion) for n in names])
        L.append(tuple(src.pose.bones[P+'Hips'].location))
        W.append(tuple(src.matrix_world@src.pose.bones[P+'Hips'].head))
    for o in new: bpy.data.objects.remove(o)
    bpy.data.actions.remove(act)
    return names,np.array(R),np.array(L),np.array(W)

RM={}
def write(name, names, R, L, W, inplace=True, loop=True, rootmotion=False):
    n=len(R)
    if rootmotion:
        # tira o caminho horizontal inteiro do quadril (o codigo do jogo aplica esse deslocamento)
        # e guarda a distancia percorrida para a frente (-Y no Blender) em cada quadro
        drift=L[-1]-L[0]; hor=np.abs(drift)>0.3*np.abs(drift).max()
        u=np.zeros(3); u[hor]=drift[hor]; u/=np.linalg.norm(u)+1e-9
        Lw=L-np.outer((L-L[0])@u,u)
        d=[round(float(-(W[i][1]-W[0][1])),4) for i in range(n)]
        RM[name]={'d':d,'duration':(n-1)/30.0}
        L=Lw; inplace=False
    # remove o deslocamento horizontal (tendencia linear) do quadril: animacao no lugar
    Lw=L.copy()
    dist=0.0
    if inplace:
        dW=W[-1]-W[0]; dist=float(np.hypot(dW[0],dW[1]))
        t=np.linspace(0,1,n)[:,None]
        drift=L[-1]-L[0]
        # canais horizontais = os que acumulam deslocamento (no espaco local do quadril)
        hor=np.abs(drift)>0.3*np.abs(drift).max() if np.abs(drift).max()>1e-6 else np.zeros(3,bool)
        Lw[:,hor]=L[:,hor]-(L[0,hor]+drift[hor]*t[:,0][:,None])
    act=bpy.data.actions.new(name); act.use_fake_user=True
    tgt.animation_data_create(); tgt.animation_data.action=act
    for fi in range(n):
        for bi,bn in enumerate(names):
            pb=tgt.pose.bones.get(bn)
            if not pb: continue
            pb.rotation_mode='QUATERNION'; pb.rotation_quaternion=Quaternion(R[fi,bi])
            pb.keyframe_insert('rotation_quaternion',frame=fi)
        hp=tgt.pose.bones[P+'Hips']; hp.location=Vector(Lw[fi]); hp.keyframe_insert('location',frame=fi)
    tr=tgt.animation_data.nla_tracks.new(); tr.name=name; st=tr.strips.new(name,0,act)
    tgt.animation_data.action=None
    dur=(n-1)/30.0
    return dict(frames=n, duration=dur, speed=(dist/dur if inplace and dur>0 else 0))

meta={}
names,R,L,W=sample('Idle.fbx'); meta['Idle']=write('Idle',names,R,L,W,inplace=False)
names,R,L,W=sample('Looking_Around.fbx'); meta['LookAround']=write('LookAround',names,R,L,W,inplace=False)
names,R,L,W=sample('Running.fbx'); meta['Run']=write('Run',names,R,L,W)
# ciclo de caminhada: melhor par de quadros (i,j) na segunda metade do Start Walking
names,R,L,W=sample('Start_Walking.fbx')
n=len(R); best=None
Q=R/np.linalg.norm(R,axis=2,keepdims=True)
for i in range(n//3, n-24):
    for j in range(i+24, min(n, i+44)):
        d=1-np.abs((Q[i]*Q[j]).sum(1)).clip(0,1)
        score=d.mean()
        if best is None or score<best[0]: best=(score,i,j)
_,i,j=best; print('WALK loop frames',i,j,'score',best[0])
meta['Walk']=write('Walk',names,R[i:j+1],L[i:j+1],W[i:j+1])
meta['Walk']['from']=[int(i),int(j)]
names,R,L,W=sample('Female_Stop_Walking.fbx'); meta['StopWalkF']=write('StopWalkF',names,R,L,W,rootmotion=True)
names,R,L,W=sample('Stop_Walking.fbx'); meta['StopWalk']=write('StopWalk',names,R,L,W,rootmotion=True)
names,R,L,W=sample('Walking_Turn_180.fbx'); meta['TurnWalk']=write('TurnWalk',names,R,L,W,rootmotion=True)
names,R,L,W=sample('Running_Turn_180.fbx'); meta['TurnRun']=write('TurnRun',names,R,L,W,rootmotion=True)
tgt['rootmotion']=json.dumps(RM)
print('META',json.dumps(meta)); print('RM',{k:(v['d'][-1],v['duration']) for k,v in RM.items()})
json.dump(meta,open(D+'clips.json','w'))

if LANCA:
    # ---- lanca nas costas ----
    import mats, spear, armor as A
    M=mats.library()
    bpy.context.view_layer.update()
    dg=bpy.context.evaluated_depsgraph_get(); me=mesh.evaluated_get(dg).to_mesh()
    co=np.array([(mesh.matrix_world@v.co)[:] for v in me.vertices]); mesh.evaluated_get(dg).to_mesh_clear()
    H=co[:,2].max()
    band=co[(co[:,2]>0.62*H)&(co[:,2]<0.72*H)&(np.abs(co[:,0])<0.12)]
    back_y=band[:,1].max()   # costas = +Y (frente do personagem = -Y)
    L_SPEAR=1.75
    ANG=math.radians(34)
    low=Vector((0.30, back_y+0.07, 0.40*H)); up=low+Vector((-math.sin(ANG)*L_SPEAR, 0.03, math.cos(ANG)*L_SPEAR))
    axis=(up-low).normalized()
    e1=axis.cross(Vector((0,1,0))).normalized(); e2=axis.cross(e1)
    parts=spear.parts(r=0.015, z_butt=0.0, z_top=L_SPEAR-0.45)
    def place(V): return [tuple(low+e1*v[0]+e2*v[1]+axis*v[2]) for v in V]
    from rig import mesh_obj
    matmap={'shaft':'wood','butt':'iron','collar':'brass','collar2':'brass','blade':'steel','knot':'tassel'}
    spine=P+'Spine2'
    # osso da borla (mola no jogo), filho do Spine2
    bpy.context.view_layer.objects.active=tgt; bpy.ops.object.mode_set(mode='EDIT')
    eb=tgt.data.edit_bones; Minv=tgt.matrix_world.inverted()
    zt=float(parts['knot'][0][:,2].max()); th=place([(0,0,zt),(0,0,zt-0.16)])
    b=eb.new('tassel'); b.head=Minv@Vector(th[0]); b.tail=Minv@Vector((th[0][0],th[0][1],th[0][2]-0.16)); b.parent=eb[spine]
    bpy.ops.object.mode_set(mode='OBJECT')
    def add_rigid(name, V, F, U, mat, bone, smooth=True):
        ob=mesh_obj(name,V,F,U,smooth=smooth); ob.data.materials.append(mat)
        ob.vertex_groups.new(name=bone).add(list(range(len(ob.data.vertices))),1.0,'REPLACE')
        m=ob.modifiers.new('Armature','ARMATURE'); m.object=tgt
        # coordenadas ja estao no mundo; parenteia mantendo a posicao
        mw=ob.matrix_world.copy(); ob.parent=tgt; ob.matrix_parent_inverse=tgt.matrix_world.inverted()
        return ob
    for k,(v,f,u) in parts.items():
        if k=='tassel': continue
        add_rigid('Lanca_'+k, place(v), f, u, M[matmap[k]], spine, smooth=(k!='blade'))
    for zc in (0.55, 1.0):
        v,f,u=spear.cyl(zc-0.05,zc+0.05,0.0175,0.0175,16,6,(1,6)); add_rigid('Lanca_faixa',place(v),f,u,M['wrap'],spine)
    v,f,u=parts['tassel']; add_rigid('Lanca_borla',place(v),f,u,M['tassel'],'tassel')
    # alca de couro cruzando o peito (do ombro direito ao quadril esquerdo)
    strap=[]
    for t in np.linspace(0,1,24):
        ang=-math.pi+t*2*math.pi
        strap.append(None)
    chest=co[(co[:,2]>0.60*H)&(co[:,2]<0.78*H)]
    def surf(x,z,front):
        m=(np.abs(co[:,0]-x)<0.03)&(np.abs(co[:,2]-z)<0.03)
        if not m.any(): return None
        return co[m,1].min()-0.012 if front else co[m,1].max()+0.012
    pts=[]
    for t in np.linspace(0,1,12):
        x=-0.13+0.30*t; z=0.79*H-0.24*H*t; y=surf(x,z,True)
        if y is not None: pts.append((x,y,z))
    if len(pts)>4:
        v,f,u=A.tube(pts,0.012,6); add_rigid('Alca',[tuple(p) for p in v],f,u,M['sole'],spine)
    # junta malhas por material
    meshes=[o for o in bpy.context.scene.objects if o.type=='MESH' and o!=mesh]
    groups={}
    for o in meshes: groups.setdefault(o.data.materials[0].name,[]).append(o)
    for nm,obs in groups.items():
        if len(obs)<2: continue
        bpy.ops.object.select_all(action='DESELECT')
        for o in obs: o.select_set(True)
        bpy.context.view_layer.objects.active=obs[0]; bpy.ops.object.join(); obs[0].name='Lanca_'+nm
for pb in tgt.pose.bones: pb.rotation_quaternion=Quaternion(); pb.location=(0,0,0)
bpy.ops.export_scene.gltf(filepath=D+SAIDA, export_format='GLB', export_animations=True, export_animation_mode='NLA_TRACKS',
    export_skins=True, export_extras=True, export_force_sampling=True, export_draco_mesh_compression_enable=True, export_draco_mesh_compression_level=7,
    export_image_format='WEBP', export_image_quality=88)
print('DONE')
