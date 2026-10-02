# Monta um esqueleto com nomes do Mixamo (mixamorig:*) sobre um personagem em pose T,
# faz o skinning e exporta FBX. O Mixamo reconhece o rig e pula a etapa de marcadores.
import bpy, sys, numpy as np, mathutils, os
src,dst=sys.argv[-2],sys.argv[-1]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=src)
ob=[o for o in bpy.context.scene.objects if o.type=='MESH'][0]
bpy.context.view_layer.objects.active=ob; ob.select_set(True)
bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
co=np.array([v.co[:] for v in ob.data.vertices]); H=co[:,2].max()
def band(z0,z1): return co[(co[:,2]>z0)&(co[:,2]<z1)]
# linha dos bracos: pontos bem afastados do centro
far=co[np.abs(co[:,0])>0.30*H]
armZ=np.median(far[:,2]); armY=np.median(far[:,1])
tipL=co[:,0].max(); tipR=co[:,0].min()
# largura do tronco logo abaixo da axila
t=band(armZ-0.10*H,armZ-0.06*H); t=t[np.abs(t[:,0])<0.25*H]
half=np.percentile(np.abs(t[:,0]),95)
def yc(z0,z1):
    b=band(z0,z1); b=b[np.abs(b[:,0])<0.12*H]; return float(np.median(b[:,1])) if len(b) else 0.0
# pernas: centros esquerdo/direito na altura do joelho
k=band(0.26*H,0.30*H); legx=float(np.median(np.abs(k[:,0][np.abs(k[:,0])<0.2*H])))
print('armZ',round(armZ,3),'tips',round(tipR,3),round(tipL,3),'torso half',round(half,3),'legx',round(legx,3))
hip=0.53*H
J={
 'Hips':(0,yc(hip-0.03,hip+0.03),hip),
 'Spine':(0,yc(0.60*H-.02,0.60*H+.02),0.60*H),
 'Spine1':(0,yc(0.67*H-.02,0.67*H+.02),0.67*H),
 'Spine2':(0,yc(0.74*H-.02,0.74*H+.02),0.74*H),
 'Neck':(0,yc(armZ+0.02,armZ+0.06),armZ+0.045*H),
 'Head':(0,yc(0.87*H,0.90*H),0.875*H),
 'HeadTop_End':(0,yc(0.95*H,0.98*H),H),
}
for s,sx in (('Left',1),('Right',-1)):
    tip=tipL if sx>0 else tipR
    sh=sx*(half*0.55); arm=sx*(half-0.01*H); wr=tip-sx*0.10*H; el=(arm+wr)/2
    J[s+'Shoulder']=(sh,armY,armZ+0.01*H); J[s+'Arm']=(arm,armY,armZ)
    J[s+'ForeArm']=(el,armY+0.01*H,armZ); J[s+'Hand']=(wr,armY,armZ)
    J[s+'HandEnd']=(tip,armY,armZ)
    J[s+'UpLeg']=(sx*legx*0.9,J['Hips'][1],hip-0.03*H); J[s+'Leg']=(sx*legx,yc(0.27*H,0.29*H)-0.01*H,0.28*H)
    J[s+'Foot']=(sx*legx,yc(0.04*H,0.07*H)+0.01*H,0.055*H); J[s+'ToeBase']=(sx*legx,J[s+'Foot'][1]-0.07*H,0.015*H)
    J[s+'Toe_End']=(sx*legx,J[s+'Foot'][1]-0.12*H,0.015*H)
chain=[('Hips',None,'Spine'),('Spine','Hips','Spine1'),('Spine1','Spine','Spine2'),('Spine2','Spine1','Neck'),('Neck','Spine2','Head'),('Head','Neck','HeadTop_End')]
for s in ('Left','Right'):
    chain+=[(s+'Shoulder','Spine2',s+'Arm'),(s+'Arm',s+'Shoulder',s+'ForeArm'),(s+'ForeArm',s+'Arm',s+'Hand'),(s+'Hand',s+'ForeArm',s+'HandEnd'),
            (s+'UpLeg','Hips',s+'Leg'),(s+'Leg',s+'UpLeg',s+'Foot'),(s+'Foot',s+'Leg',s+'ToeBase'),(s+'ToeBase',s+'Foot',s+'Toe_End')]
arm=bpy.data.armatures.new('Armature'); ao=bpy.data.objects.new('Armature',arm); bpy.context.scene.collection.objects.link(ao)
bpy.context.view_layer.objects.active=ao; bpy.ops.object.mode_set(mode='EDIT')
P='mixamorig:'
for n,par,tail in chain:
    e=arm.edit_bones.new(P+n); e.head=J[n]; e.tail=J[tail]
    if (e.tail-e.head).length<1e-3: e.tail=e.head+mathutils.Vector((0,0,0.05))
for n,par,tail in chain:
    if par: arm.edit_bones[P+n].parent=arm.edit_bones[P+par]
bpy.ops.object.mode_set(mode='OBJECT')
# skinning automatico (bone heat); vertices sem peso recebem o osso mais proximo
bpy.ops.object.select_all(action='DESELECT'); ob.select_set(True); ao.select_set(True); bpy.context.view_layer.objects.active=ao
bpy.ops.object.parent_set(type='ARMATURE_AUTO')
bones=[b for b in arm.bones]
segs=[(np.array(b.head_local),np.array(b.tail_local)) for b in bones]
def nearest_bone(p):
    best=None
    for i,(a,b) in enumerate(segs):
        ab=b-a; t=np.clip(np.dot(p-a,ab)/max(np.dot(ab,ab),1e-9),0,1); d=np.linalg.norm(p-(a+ab*t))
        if best is None or d<best[0]: best=(d,i)
    return bones[best[1]].name
empty=0
for v in ob.data.vertices:
    if sum(g.weight for g in v.groups)<1e-4:
        name=nearest_bone(np.array(v.co[:])); vg=ob.vertex_groups.get(name) or ob.vertex_groups.new(name=name)
        vg.add([v.index],1.0,'REPLACE'); empty+=1
print('RIG bones',len(bones),'verts sem peso preenchidos',empty,'de',len(ob.data.vertices))
bpy.ops.export_scene.fbx(filepath=dst, object_types={'MESH','ARMATURE'}, add_leaf_bones=False, path_mode='COPY', embed_textures=True,
    apply_unit_scale=True, apply_scale_options='FBX_SCALE_ALL', axis_forward='-Z', axis_up='Y', mesh_smooth_type='FACE', bake_anim=False)
