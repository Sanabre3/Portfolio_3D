import sys; sys.path.insert(0,'/tmp/sam')
import bpy, numpy as np, math
from mathutils import Vector, Matrix
from rig import *
import anim, clips, grip, mats, cloth, land, assemble_armor, face, hair, spear, feet
OUT=sys.argv[-1] if sys.argv[-1].endswith('.glb') else '/tmp/sam/test.glb'
reset()
B=land.B; bones=list(B['bones'])
bpy.context.scene.render.fps=30
arm=build_armature(B)
M=mats.library()
def put(name, L, mat):
    ob=mesh_obj(name, L['V'], L['F'], L['UV'])
    skin(ob, arm, bones, L['bi'], L['bw']); ob.data.materials.append(mat); return ob
def put_rigid(name, V, F, U, mat, bone, smooth=True):
    ob=mesh_obj(name, V, F, U, smooth=smooth); ob.data.materials.append(mat); rigid(ob,arm,bone); return ob

# ---- roupa derivada do corpo ----
G=cloth.gi(); Hk=cloth.hakama(); Ky=cloth.kyahan(); Tb=cloth.tabi(); Gl=cloth.gloves()
hide=cloth.hidden_body_faces([(G,1),(Hk,1),(Ky,1),(Tb,1),(Gl,1)])
fs=[i for i in range(len(cloth.F)) if i not in hide]
used=sorted({v for i in fs for v in cloth.F[i]}); rm={v:k for k,v in enumerate(used)}
bodyL=dict(V=land.V[used],F=[[rm[v] for v in cloth.F[i]] for i in fs],UV=[cloth.VT[t]*40 for i in fs for t in cloth.FT[i]],bi=cloth.bi[used],bw=cloth.bw[used])
body=put('Body',bodyL,M['skin'])
SC=face.skin_colors()[used]
col=body.data.color_attributes.new('Col','FLOAT_COLOR','POINT')
col.data.foreach_set('color', np.c_[SC,np.ones(len(SC))].ravel())
put('Gi',G,M['cloth']); put('Hakama',Hk,M['clothD']); put('Kyahan',Ky,M['wrap']); put('Tabi',Tb,M['cloth']); put('Gloves',Gl,M['wrap'])

# ---- olhos ----
P,EF,EU=face.eyes()
o=0; eyeF=[];eyeU=[];corF=[];corU=[]
for f in EF:
    uv=EU[o:o+len(f)]; o+=len(f)
    if all(u[0]>0.85 and u[1]<0.15 for u in uv): corF.append(f); corU+=uv
    else: eyeF.append(f); eyeU+=uv
put_rigid('Eyes',P,eyeF,eyeU,M['eye'],'head')
put_rigid('Cornea',P,corF,corU,M['cornea'],'head')

# ---- cabelo ----
HV,HF,HU,scalp=hair.build(cloth.N)
put_rigid('Hair',HV,HF,HU,M['hair'],'head')
cap=cloth.layer(scalp, land.V+cloth.N*0.004, uvscale=30)
capob=put('HairCap',cap,M['hair'])
BV,BF,BU=hair.brows(cloth.N)
put_rigid('Brows',BV,BF,BU,M['hair'],'head')

# ---- sandalias ----
for name,a,b,c_,mk in feet.sandals():
    if name.startswith('Sole'):
        ob=mesh_obj(name,a,b,c_); ob.data.materials.append(M['sole'])
    else:
        ob=assemble_armor.cords_obj(name,a,M['sandal'],arm,'foot.L'); ob.modifiers.clear(); ob.vertex_groups.clear()
    assemble_armor.nearest_weights(ob,arm)
# ---- armadura ----
AR=assemble_armor.build(arm,M)

# ---- lanca na mao direita ----
c,ax=grip.solve_wrist(arm)
up=-Vector(ax).normalized(); e1=up.cross(Vector((1,0,0))).normalized(); e2=up.cross(e1)
z_grip=1.21
def place(Vl):
    return [c+e1*v[0]+e2*v[1]+up*(v[2]-z_grip) for v in Vl]
PARTS=spear.parts()
matmap={'shaft':'wood','butt':'iron','collar':'brass','collar2':'brass','blade':'steel','knot':'tassel','tassel':'tassel'}
for k,(v,f,u) in PARTS.items():
    if k=='tassel': continue
    rest=grip.to_rest(arm,'wrist.R',place(v))
    put_rigid('Spear_'+k,[tuple(p) for p in rest],f,u,M[matmap[k]],'wrist.R',smooth=(k!='blade'))
# empunhaduras
for zc in (z_grip, z_grip+0.42, z_grip-0.55):
    v,f,u=spear.cyl(zc-0.05,zc+0.05,0.0185,0.0185,16,6,(1,6))
    rest=grip.to_rest(arm,'wrist.R',place(v)); put_rigid('SpearWrap',[tuple(p) for p in rest],f,u,M['wrap'],'wrist.R')
# borla com osso proprio (mola no jogo)
v,f,u=PARTS['tassel']
zt=spear.parts()['knot'][0][:,2].max()
th=grip.to_rest(arm,'wrist.R',place([(0,0,zt),(0,0,zt-0.16)]))
add_bone(arm,'tassel',tuple(th[0]),tuple(th[1]),'wrist.R')
rest=grip.to_rest(arm,'wrist.R',place(v)); put_rigid('Tassel',[tuple(p) for p in rest],f,u,M['tassel'],'tassel')

# ---- animacoes ----
anim.clear(arm)
anim.make_clip(arm,'Idle',120,clips.idle)
anim.make_clip(arm,'Walk',32,clips.walk)
anim.make_clip(arm,'Run',22,clips.run)
anim.clear(arm)
# ---- juntar malhas por material (menos draw calls no navegador) ----
bpy.ops.object.mode_set(mode='OBJECT') if bpy.context.object and bpy.context.object.mode!='OBJECT' else None
meshes=[o for o in bpy.data.objects if o.type=='MESH']
for o in meshes:
    bpy.ops.object.select_all(action='DESELECT'); bpy.context.view_layer.objects.active=o; o.select_set(True)
    for m in list(o.modifiers):
        if m.type!='ARMATURE': bpy.ops.object.modifier_apply(modifier=m.name)
groups={}
for o in meshes: groups.setdefault(o.data.materials[0].name,[]).append(o)
for name,obs in groups.items():
    if len(obs)<2: continue
    bpy.ops.object.select_all(action='DESELECT')
    for o in obs: o.select_set(True)
    bpy.context.view_layer.objects.active=obs[0]; bpy.ops.object.join(); obs[0].name=name
tris=0
for o in bpy.data.objects:
    if o.type=='MESH':
        dg=bpy.context.evaluated_depsgraph_get(); me=o.evaluated_get(dg).to_mesh(); me.calc_loop_triangles(); tris+=len(me.loop_triangles)
print('TRIS',tris,'objects',len([o for o in bpy.data.objects if o.type=='MESH']))
bpy.ops.export_scene.gltf(filepath=OUT, export_format='GLB', export_animations=True, export_animation_mode='NLA_TRACKS',
    export_skins=True, export_yup=True, export_force_sampling=True, export_apply=True, export_draco_mesh_compression_enable=True, export_draco_mesh_compression_level=7, export_draco_position_quantization=14, export_draco_normal_quantization=10, export_draco_texcoord_quantization=12, export_image_format='WEBP', export_image_quality=88)
print('done')
