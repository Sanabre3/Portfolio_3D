# Clipes de locomocao gravados como keyframes. Eixos no espaco da armature (Blender):
# +X = esquerda do personagem, -Y = frente, +Z = cima.
import bpy, math
from mathutils import Vector, Quaternion, Matrix
from rig import qaxis
X=(1,0,0); Y=(0,1,0); Z=(0,0,1)

def compose(arm, bone, rots):
    q=Quaternion()
    for axis,ang in rots: q=q @ qaxis(arm,bone,axis,ang)
    return q

def clear(arm):
    for b in arm.pose.bones:
        b.rotation_mode='QUATERNION'; b.rotation_quaternion=Quaternion(); b.location=(0,0,0)

def aim(arm, name, d, twist=0.0):
    """Orienta o osso para a direcao d (espaco da armature) com rotacao minima a partir
    da orientacao que ele teria carregado pelo pai; twist gira em torno do proprio eixo."""
    bpy.context.view_layer.update()
    pb=arm.pose.bones[name]; bone=arm.data.bones[name]
    Rr=bone.matrix_local.to_3x3()
    if pb.parent:
        Pp=pb.parent.matrix.to_3x3(); Pr=bone.parent.matrix_local.to_3x3()
        R0=Pp @ Pr.inverted() @ Rr
    else: R0=Rr
    y0=R0.col[1].normalized(); d=Vector(d).normalized()
    q=y0.rotation_difference(d)
    R=(Quaternion(d,twist).to_matrix() @ q.to_matrix() @ R0)
    # rotacao local = R0^-1 R, expressa no frame de repouso do osso
    loc=(R0.inverted() @ R).to_quaternion()
    pb.rotation_quaternion=loc
    bpy.context.view_layer.update()

def local(arm, name, axis, ang):
    pb=arm.pose.bones[name]; pb.rotation_quaternion=pb.rotation_quaternion @ Quaternion(Vector(axis),ang)

def curl(arm, s, amount, thumb):
    for f in range(2,6):
        for j,k in ((1,1.0),(2,1.35),(3,0.95)): local(arm,f'finger{f}-{j}.{s}',(1,0,0),amount*k)
    local(arm,f'finger1-2.{s}',(1,0,0),thumb*0.7); local(arm,f'finger1-3.{s}',(1,0,0),thumb*0.6)

def ground(arm, sole=0.075):
    pb=arm.pose.bones; lows=[]
    for s in 'LR':
        lows += [pb['foot.'+s].head.z-sole, pb['toe.'+s].tail.z-0.012, pb['toe.'+s].head.z-0.03]
    return min(lows)

def pose(arm, spec):
    clear(arm)
    for bone,rots in spec.get('rot',{}).items():
        arm.pose.bones[bone].rotation_quaternion=compose(arm,bone,rots)
    for name,d,tw in spec.get('aim',[]): aim(arm,name,d,tw)
    for name,q in spec.get('q',{}).items(): arm.pose.bones[name].rotation_quaternion=q
    curl(arm,'R',spec.get('curlR',1.25),1.0); curl(arm,'L',spec.get('curlL',0.55),0.35)
    bpy.context.view_layer.update()

def make_clip(arm, name, nframes, fn, grounded=True):
    act=bpy.data.actions.new(name); act.use_fake_user=True
    arm.animation_data_create(); arm.animation_data.action=act
    rb=arm.data.bones['root'].matrix_local.to_3x3().inverted()
    for f in range(nframes+1):
        spec=fn((f/nframes)*2*math.pi)
        pose(arm,spec)
        dz=ground(arm) if grounded else 0
        arm.pose.bones['root'].location=rb @ Vector((0,0,-dz+spec.get('bob',0)))
        for b in arm.pose.bones: b.keyframe_insert('rotation_quaternion',frame=f)
        arm.pose.bones['root'].keyframe_insert('location',frame=f)
    tr=arm.animation_data.nla_tracks.new(); tr.name=name; tr.strips.new(name,0,act)
    arm.animation_data.action=None
    return act
