# Rig + clipes Idle/Walk/Run para o modelo A, sem Mixamo. Saida: GLB com Draco.
import bpy, sys, math, numpy as np
from mathutils import Vector, Quaternion
src, dst = sys.argv[-2], sys.argv[-1]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.context.scene.render.fps = 30
bpy.ops.import_scene.fbx(filepath=src)
ao=[o for o in bpy.context.scene.objects if o.type=='ARMATURE'][0]
ob=[o for o in bpy.context.scene.objects if o.type=='MESH'][0]
P='mixamorig:'
# ---- pesos do cabelo: acima do quadril e fora dos bracos, so coluna/pescoco/cabeca ----
hipz=ao.data.bones[P+'Hips'].head_local.z
shx=abs(ao.data.bones[P+'LeftArm'].head_local.x)
allowed={P+n for n in ['Hips','Spine','Spine1','Spine2','Neck','Head','LeftShoulder','RightShoulder']}
names={g.index:g.name for g in ob.vertex_groups}
fixed=0
for v in ob.data.vertices:
    if v.co.z>hipz+0.02 and abs(v.co.x)<shx*0.95:
        bad=[g for g in v.groups if names[g.group] not in allowed and g.weight>0]
        if bad:
            keep=sum(g.weight for g in v.groups if names[g.group] in allowed)
            for g in bad: ob.vertex_groups[names[g.group]].remove([v.index])
            if keep<1e-4:
                grp=ob.vertex_groups.get(P+'Spine2') if v.co.z>hipz+0.3 else ob.vertex_groups.get(P+'Spine')
                grp.add([v.index],1.0,'REPLACE')
            fixed+=1
print('HAIRFIX',fixed)
X=(1,0,0); Y=(0,1,0); Z=(0,0,1)
def q(bone, axis, ang):
    M=ao.data.bones[P+bone].matrix_local.to_3x3().inverted()
    return Quaternion((M@Vector(axis)).normalized(), ang)
def pose(spec):
    for b in ao.pose.bones: b.rotation_mode='QUATERNION'; b.rotation_quaternion=Quaternion(); b.location=(0,0,0)
    for bone,rots in spec.items():
        qq=Quaternion()
        for ax,a in rots: qq=qq@q(bone,ax,a)
        ao.pose.bones[P+bone].rotation_quaternion=qq
    bpy.context.view_layer.update()
def lowest():
    # ponto mais baixo da malha deformada (sola real da bota), nao estimativa pelos ossos
    dg=bpy.context.evaluated_depsgraph_get(); ev=ob.evaluated_get(dg); me=ev.to_mesh()
    n=len(me.vertices); co=np.empty(n*3); me.vertices.foreach_get('co',co); ev.to_mesh_clear()
    return float(co[2::3].min())
rest_low=None
S=math.sin
DOWN=math.radians(72)
def base(ph, amp, run):
    s=S(ph); s2=S(ph+math.pi)
    return {
     'LeftArm':[(Y,DOWN),(X,-0.45*amp*(1+run)*s2)], 'RightArm':[(Y,-DOWN),(X,-0.45*amp*(1+run)*s)],
     'LeftForeArm':[(Z,0.25+0.35*amp*max(0,-s2)+0.9*run)], 'RightForeArm':[(Z,-(0.25+0.35*amp*max(0,-s)+0.9*run))],
    }
def idle(ph):
    b=S(ph); d=base(0,0,0)
    d['LeftArm'][0]=(Y,DOWN-0.03*b); d['RightArm'][0]=(Y,-DOWN+0.03*b)
    d.update({'Spine1':[(X,-0.015*b)],'Spine2':[(X,-0.02*b)],'Head':[(Z,0.06*S(ph+1.2))],
              'LeftUpLeg':[(Y,-0.04)],'RightUpLeg':[(Y,0.03),(X,0.04)],'RightLeg':[(X,0.06)]})
    return d
def loco(stride, knee, lift, lean, run):
    def f(ph):
        s=S(ph); s2=S(ph+math.pi); d=base(ph,1,run)
        kL=max(0,-S(ph-0.9)); kR=max(0,-S(ph+math.pi-0.9))
        d.update({'LeftUpLeg':[(X,-stride*s)],'RightUpLeg':[(X,-stride*s2)],
                  'LeftLeg':[(X,knee*kL+0.05)],'RightLeg':[(X,knee*kR+0.05)],
                  'LeftFoot':[(X,-lift*max(0,S(ph+0.4))+0.1*max(0,-s))],'RightFoot':[(X,-lift*max(0,S(ph+math.pi+0.4))+0.1*max(0,-s2))],
                  'Hips':[(Z,0.08*s)],'Spine':[(X,-lean),(Z,-0.05*s)],'Spine1':[(Z,-0.04*s)],'Spine2':[(Z,-0.03*s)],
                  'Neck':[(X,lean*0.6)],'Head':[(Z,0.03*s)]})
        return d
    return f
def make(name, n, fn):
    act=bpy.data.actions.new(name); act.use_fake_user=True
    ao.animation_data_create(); ao.animation_data.action=act
    Mh=ao.data.bones[P+'Hips'].matrix_local.to_3x3().inverted()
    for fr in range(n+1):
        pose(fn(2*math.pi*fr/n))
        dz=lowest()-rest_low
        ao.pose.bones[P+'Hips'].location=Mh@Vector((0,0,-dz))
        for b in ao.pose.bones: b.keyframe_insert('rotation_quaternion',frame=fr)
        ao.pose.bones[P+'Hips'].keyframe_insert('location',frame=fr)
    tr=ao.animation_data.nla_tracks.new(); tr.name=name; tr.strips.new(name,0,act); ao.animation_data.action=None
pose({}); rest_low=lowest()
make('Idle',120,idle); make('Walk',32,loco(0.34,0.85,0.3,0.03,0.0)); make('Run',22,loco(0.62,1.5,0.45,0.15,1.0))
pose({})
bpy.ops.export_scene.gltf(filepath=dst, export_format='GLB', export_animations=True, export_animation_mode='NLA_TRACKS',
    export_skins=True, export_force_sampling=True, export_draco_mesh_compression_enable=True, export_draco_mesh_compression_level=7,
    export_image_format='WEBP', export_image_quality=88)
print('DONE')
