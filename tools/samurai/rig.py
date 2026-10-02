# Utilitarios Blender: conversao de eixo (MakeHuman Y-up/+Z frente -> Blender Z-up/-Y frente),
# criacao de malha, armature e pesos.
import bpy, bmesh, numpy as np
from mathutils import Vector, Matrix, Quaternion

def cv(p):  # mh (x,y,z) -> blender (x,-z,y)
    p=np.asarray(p,float); return np.stack([p[...,0],-p[...,2],p[...,1]],-1)

def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)

def mesh_obj(name, verts, faces, uvs=None, smooth=True, coll=None):
    me=bpy.data.meshes.new(name)
    me.from_pydata([tuple(v) for v in verts],[],[tuple(f) for f in faces])
    me.update()
    if uvs is not None:
        uv=me.uv_layers.new(name='UVMap')
        uv.data.foreach_set('uv', np.asarray(uvs,float).ravel())
    if smooth:
        me.shade_smooth() if hasattr(me,'shade_smooth') else [setattr(p,'use_smooth',True) for p in me.polygons]
    ob=bpy.data.objects.new(name,me)
    (coll or bpy.context.scene.collection).objects.link(ob)
    return ob

def build_armature(B):
    arm=bpy.data.armatures.new('Rig'); ob=bpy.data.objects.new('Samurai',arm)
    bpy.context.scene.collection.objects.link(ob)
    bpy.context.view_layer.objects.active=ob; ob.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    eb={}
    for n,h,t,nrm in zip(B['bones'],B['H'],B['T'],B['N']):
        e=arm.edit_bones.new(n); e.head=Vector(cv(h)); e.tail=Vector(cv(t))
        if (e.tail-e.head).length<1e-3: e.tail=e.head+Vector((0,0,0.03))
        e.align_roll(Vector(cv(nrm))); eb[n]=e
    for n,p in zip(B['bones'],B['par']):
        if p: eb[n].parent=eb[p]; eb[n].use_connect=False
    bpy.ops.object.mode_set(mode='OBJECT')
    return ob

def add_bone(armob, name, head, tail, parent, roll_vec=(0,-1,0)):
    bpy.context.view_layer.objects.active=armob
    bpy.ops.object.mode_set(mode='EDIT')
    e=armob.data.edit_bones.new(name); e.head=Vector(head); e.tail=Vector(tail)
    e.align_roll(Vector(roll_vec)); e.parent=armob.data.edit_bones[parent]
    bpy.ops.object.mode_set(mode='OBJECT')

def skin(ob, armob, bone_names, bi, bw):
    for n in bone_names: ob.vertex_groups.new(name=n)
    for v in range(len(bi)):
        for k in range(bi.shape[1]):
            if bw[v,k]>1e-4: ob.vertex_groups[bone_names[bi[v,k]]].add([v],float(bw[v,k]),'REPLACE')
    m=ob.modifiers.new('Armature','ARMATURE'); m.object=armob
    ob.parent=armob

def rigid(ob, armob, bone):
    ob.vertex_groups.new(name=bone).add(list(range(len(ob.data.vertices))),1.0,'REPLACE')
    m=ob.modifiers.new('Armature','ARMATURE'); m.object=armob; ob.parent=armob

def rest_rot(armob, bone):
    return armob.data.bones[bone].matrix_local.to_3x3()

def qaxis(armob, bone, axis, ang):
    """Rotacao em torno de um eixo do espaco da armature (Blender), expressa no frame local do osso."""
    a=rest_rot(armob,bone).inverted() @ Vector(axis)
    return Quaternion(a.normalized(), ang)
