# Converte um .glb (ex.: TRELLIS.2) em FBX pronto para o Mixamo:
# pe no chao, 1,75 m, malha reduzida, textura base em PNG embutida.
import bpy, sys, os, mathutils, numpy as np
src, dst = sys.argv[-2], sys.argv[-1]
TARGET_TRIS=int(os.environ.get('TRIS','60000')); HEIGHT=1.75
bpy.ops.wm.read_factory_settings(use_empty=True)
(bpy.ops.import_scene.fbx if src.lower().endswith('.fbx') else bpy.ops.import_scene.gltf)(filepath=src)
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
# aplica transformacoes e junta
bpy.ops.object.select_all(action='DESELECT')
for o in meshes: o.select_set(True)
bpy.context.view_layer.objects.active=meshes[0]
if len(meshes)>1: bpy.ops.object.join()
ob=bpy.context.view_layer.objects.active
ob.parent=None
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
for o in list(bpy.context.scene.objects):
    if o.type!='MESH': bpy.data.objects.remove(o)
# gira para ficar de frente (-Y no Blender = frente no FBX/Mixamo)
import math
ob.rotation_euler=(0,0,math.radians(float(os.environ.get('ROTZ','0'))))
bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
# escala e chao
bb=[mathutils.Vector(c) for c in ob.bound_box]
zmin=min(v.z for v in bb); zmax=max(v.z for v in bb); cx=sum(v.x for v in bb)/8; cy=sum(v.y for v in bb)/8
s=HEIGHT/(zmax-zmin)
ob.location=(-cx*s,-cy*s,-zmin*s); ob.scale=(s,s,s)
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
# remove ilhas minusculas (fios soltos, respingos) que confundem o auto-rig
def drop_small_islands(o, min_verts):
    me=o.data; n=len(me.vertices); ne=len(me.edges)
    ed=np.empty(ne*2,dtype=np.int64); me.edges.foreach_get('vertices',ed); ed=ed.reshape(-1,2)
    lab=np.arange(n)
    for _ in range(500):
        m=np.minimum(lab[ed[:,0]],lab[ed[:,1]]); new=lab.copy()
        np.minimum.at(new,ed[:,0],m); np.minimum.at(new,ed[:,1],m); new=new[new]
        if (new==lab).all(): break
        lab=new
    u,inv,cnt=np.unique(lab,return_inverse=True,return_counts=True)
    small=cnt[inv]<min_verts
    import bmesh
    bm=bmesh.new(); bm.from_mesh(me); bm.verts.ensure_lookup_table()
    bmesh.ops.delete(bm,geom=[bm.verts[i] for i in np.where(small)[0]],context='VERTS'); bm.to_mesh(me); bm.free()
    return len(u), int((cnt<min_verts).sum())
# solda vertices duplicados (as UVs ficam por canto, nao se perdem) e reduz triangulos
bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT'); bpy.ops.mesh.remove_doubles(threshold=0.0001); bpy.ops.object.mode_set(mode='OBJECT')
if os.environ.get('CLEAN','0')=='1':
    isl,rem=drop_small_islands(ob,int(os.environ.get('MINISLAND','40'))); print('ISLANDS',isl,'removed',rem)
    bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT'); bpy.ops.mesh.normals_make_consistent(inside=False); bpy.ops.object.mode_set(mode='OBJECT')
tris=sum(len(p.vertices)-2 for p in ob.data.polygons)
if tris>TARGET_TRIS:
    m=ob.modifiers.new('Dec','DECIMATE'); m.ratio=TARGET_TRIS/tris
    bpy.ops.object.modifier_apply(modifier=m.name)
# visualizadores WebGL (como o do Mixamo) usam indice de 16 bits: mais de 65.535 vertices
# por malha e o resto some. Conta os vertices "reais" (separados por costura de UV) e divide
# a malha em faixas de altura ate cada parte ficar abaixo do limite.
def split_count(o):
    me=o.data; n=len(me.loops); vi=np.empty(n,dtype=np.int64); me.loops.foreach_get('vertex_index',vi)
    uv=np.empty(n*2); me.uv_layers.active.data.foreach_get('uv',uv); uv=np.round(uv.reshape(-1,2)*1e5)
    return len(np.unique(np.c_[vi,uv],axis=0))
LIMIT=int(os.environ.get('VLIMIT','10000000'))
sv=split_count(ob)
if os.environ.get('SINGLE','1')=='1':
    while sv>LIMIT:
        m=ob.modifiers.new('Dec2','DECIMATE'); m.ratio=max(0.5,(LIMIT/sv)*0.95); bpy.ops.object.modifier_apply(modifier=m.name); sv=split_count(ob)
parts=1 if os.environ.get('SINGLE','1')=='1' else max(1,int(np.ceil(sv/LIMIT)))
if parts>1:
    me=ob.data; nf=len(me.polygons); cz=np.empty(nf*3); me.polygons.foreach_get('center',cz); cz=cz.reshape(-1,3)[:,2]
    qs=np.quantile(cz,np.linspace(0,1,parts+1)[1:-1])
    band=np.searchsorted(qs,cz)
    for b in range(parts-1,0,-1):
        o=[x for x in bpy.context.scene.objects if x.type=='MESH' and x.name==ob.name][0]
        bpy.ops.object.select_all(action='DESELECT'); o.select_set(True); bpy.context.view_layer.objects.active=o
        m=o.data; k=len(m.polygons); czz=np.empty(k*3); m.polygons.foreach_get('center',czz); czz=czz.reshape(-1,3)[:,2]
        sel=(np.searchsorted(qs,czz)==b)
        bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='DESELECT'); bpy.ops.object.mode_set(mode='OBJECT')
        m.polygons.foreach_set('select',sel); m.update()
        bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.separate(type='SELECTED'); bpy.ops.object.mode_set(mode='OBJECT')
parts_objs=[x for x in bpy.context.scene.objects if x.type=='MESH']
print('SPLIT', sv, '->', [split_count(x) for x in parts_objs])
# textura base -> PNG em disco (Mixamo nao le WebP)
out_dir=os.path.dirname(dst); tex_dir=os.path.join(out_dir,'textures'); os.makedirs(tex_dir,exist_ok=True)
for mat in ob.data.materials:
    nt=mat.node_tree; p=nt.nodes.get('Principled BSDF')
    for n in list(nt.nodes):
        if n.type=='TEX_IMAGE' and n.image:
            linked_base = any(l.to_socket==p.inputs['Base Color'] for l in n.outputs['Color'].links) if p else False
            if not linked_base:
                nt.nodes.remove(n); continue
            img=n.image; path=os.path.join(tex_dir,'base_color.png')
            # copia sem canal alfa: com alfa o Mixamo/Blender tratam a malha como transparente
            w,h=img.size; px=np.empty(w*h*4,dtype=np.float32); img.pixels.foreach_get(px); px[3::4]=1.0
            rgb=bpy.data.images.new('base_color',w,h,alpha=False); rgb.pixels.foreach_set(px)
            # textura em potencia de 2 (2048): o visualizador WebGL do Mixamo falha com 3072 e afins
            T=int(os.environ.get('TEXSIZE','2048'))
            if (w,h)!=(T,T): rgb.scale(T,T)
            sc=bpy.context.scene; sc.render.image_settings.file_format='PNG'; sc.render.image_settings.color_mode='RGB'
            rgb.save_render(path); rgb.filepath=path; rgb.source='FILE'; rgb.reload(); rgb.alpha_mode='NONE'
            n.image=rgb
            for l in list(n.outputs['Alpha'].links): nt.links.remove(l)
    if p: p.inputs['Metallic'].default_value=0.0; p.inputs['Roughness'].default_value=0.7
bpy.ops.export_scene.fbx(filepath=dst, use_selection=False, object_types={'MESH'}, apply_unit_scale=True,
    apply_scale_options='FBX_SCALE_ALL', path_mode='COPY', embed_textures=True, mesh_smooth_type='FACE', axis_forward='-Z', axis_up='Y')
print('RESULT tris', tris, '->', sum(len(p.vertices)-2 for o in bpy.context.scene.objects if o.type=='MESH' for p in o.data.polygons), 'height', HEIGHT)
