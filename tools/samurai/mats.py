# Materiais Principled BSDF pensados para exportar limpo em glTF
# (base, metal, rugosidade, normal, coat -> clearcoat, sheen).
import bpy
T='/tmp/sam/tex/'
_img={}
def img(name, non_color=False):
    if name not in _img:
        im=bpy.data.images.load(T+name); im.colorspace_settings.name='Non-Color' if non_color else 'sRGB'; _img[name]=im
    return _img[name]
def lin(c): return tuple(((x/255)**2.2) for x in c)
def make(name, color, rough=0.8, metal=0.0, normal=None, nstr=1.0, coat=0.0, coat_rough=0.1,
         sheen=0.0, sheen_col=(1,1,1), color_tex=None, vcol=False, alpha=None, spec=0.5):
    m=bpy.data.materials.new(name); m.use_nodes=True
    nt=m.node_tree; p=nt.nodes['Principled BSDF']
    p.inputs['Base Color'].default_value=(*lin(color),1)
    p.inputs['Roughness'].default_value=rough; p.inputs['Metallic'].default_value=metal
    p.inputs['Specular IOR Level'].default_value=spec
    if coat: p.inputs['Coat Weight'].default_value=coat; p.inputs['Coat Roughness'].default_value=coat_rough
    if sheen: p.inputs['Sheen Weight'].default_value=sheen; p.inputs['Sheen Tint'].default_value=(*sheen_col,1)
    if color_tex:
        t=nt.nodes.new('ShaderNodeTexImage'); t.image=img(color_tex)
        if vcol:
            a=nt.nodes.new('ShaderNodeVertexColor'); mix=nt.nodes.new('ShaderNodeMix'); mix.data_type='RGBA'; mix.blend_type='MULTIPLY'
            mix.inputs['Factor'].default_value=1.0
            nt.links.new(t.outputs['Color'],mix.inputs[6]); nt.links.new(a.outputs['Color'],mix.inputs[7])
            nt.links.new(mix.outputs[2],p.inputs['Base Color'])
        else:
            mix=nt.nodes.new('ShaderNodeMix'); mix.data_type='RGBA'; mix.blend_type='MULTIPLY'; mix.inputs['Factor'].default_value=1.0
            mix.inputs[7].default_value=(*lin(color),1)
            nt.links.new(t.outputs['Color'],mix.inputs[6]); nt.links.new(mix.outputs[2],p.inputs['Base Color'])
    elif vcol:
        a=nt.nodes.new('ShaderNodeVertexColor'); nt.links.new(a.outputs['Color'],p.inputs['Base Color'])
    if normal:
        t=nt.nodes.new('ShaderNodeTexImage'); t.image=img(normal,True)
        nm=nt.nodes.new('ShaderNodeNormalMap'); nm.inputs['Strength'].default_value=nstr
        nt.links.new(t.outputs['Color'],nm.inputs['Color']); nt.links.new(nm.outputs['Normal'],p.inputs['Normal'])
    return m
def library():
    L={}
    L['skin']=make('Skin',(214,160,124),rough=0.5,normal='skin_n.png',nstr=0.12,vcol=True,spec=0.45)
    L['cloth']=make('ClothBlack',(28,27,32),rough=0.88,normal='fabric_n.png',nstr=0.6,sheen=0.6,sheen_col=(0.35,0.35,0.42),color_tex='fabric_c.png')
    L['clothD']=make('ClothHakama',(22,21,26),rough=0.9,normal='fabric_n.png',nstr=0.7,sheen=0.7,sheen_col=(0.3,0.3,0.38),color_tex='fabric_c.png')
    L['wrap']=make('Wraps',(34,33,38),rough=0.92,normal='wrap_n.png',nstr=0.9,color_tex='wrap_c.png',sheen=0.4,sheen_col=(0.3,0.3,0.35))
    L['lacq']=make('LacquerRed',(104,24,21),rough=0.46,normal='lacquer_n.png',nstr=0.3,coat=0.55,coat_rough=0.16,spec=0.5)
    L['lacqD']=make('LacquerRedDark',(70,17,15),rough=0.5,normal='lacquer_n.png',nstr=0.3,coat=0.5,coat_rough=0.18)
    L['lacqB']=make('LacquerBlack',(18,15,15),rough=0.35,normal='lacquer_n.png',nstr=0.25,coat=1.0,coat_rough=0.06)
    L['gold']=make('GoldCord',(196,150,70),rough=0.45,metal=0.85,normal='cord_n.png',nstr=1.0)
    L['brass']=make('Brass',(200,160,90),rough=0.28,metal=1.0)
    L['steel']=make('Steel',(215,218,224),rough=0.22,metal=1.0,normal='steel_n.png',nstr=0.3)
    L['iron']=make('IronDark',(70,70,74),rough=0.4,metal=1.0)
    L['wood']=make('WoodShaft',(255,255,255),rough=0.5,normal='wood_n.png',nstr=0.4,color_tex='wood_c.png',coat=0.4,coat_rough=0.25)
    L['tassel']=make('Tassel',(150,26,22),rough=0.85,sheen=0.8,sheen_col=(1,0.4,0.35))
    L['hair']=make('Hair',(20,18,22),rough=0.55,normal='hair_n.png',nstr=0.6,spec=0.35)
    L['eye']=make('Eye',(255,255,255),rough=0.12,color_tex='eye_c.png',coat=1.0,coat_rough=0.02)
    L['sandal']=make('SandalStrap',(120,26,24),rough=0.6)
    L['sole']=make('SandalSole',(62,44,30),rough=0.8,normal='wood_n.png',nstr=0.3)
    L['rope']=make('BlackCord',(20,18,20),rough=0.7,normal='cord_n.png',nstr=1.0)
    c=make('Cornea',(255,255,255),rough=0.02,spec=0.9)
    c.surface_render_method='BLENDED'; c.node_tree.nodes['Principled BSDF'].inputs['Alpha'].default_value=0.12
    L['cornea']=c
    return L
