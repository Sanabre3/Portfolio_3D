import math
from mathutils import Vector
from anim import X,Y,Z
S=math.sin; C=math.cos
V=lambda *a: Vector(a).normalized()
WRIST_R_TWIST=[0.0]   # calculado no build para deixar o eixo do punho vertical

def arms(ph, sw, amp, run01):
    s2=S(ph+math.pi)
    # direito: porta a lanca. Braco junto ao corpo, antebraco a frente.
    ua_R=V(-0.17, 0.10-0.03*S(ph)*amp, -1)
    fa_R=V(0.16, -0.92, 0.36+0.1*run01)
    # esquerdo: balanco contralateral
    a=sw*s2
    ua_L=V(0.14+0.06*run01, -S(a)*1.0, -C(a))
    bend=0.35+0.45*max(0,-s2)*amp+0.9*run01
    fa_L=V(0.05, -S(a+bend), -C(a+bend))
    return [('upperarm01.R',ua_R,0.0),('lowerarm01.R',fa_R,0.0),('wrist.R',fa_R,WRIST_R_TWIST[0]),
            ('upperarm01.L',ua_L,0.0),('lowerarm01.L',fa_L,0.0),('wrist.L',V(0.02,-S(a+bend*1.1),-C(a+bend*1.1)),0.0)]

def idle(ph):
    b=S(ph)
    return {'rot':{'spine03':[(X,-0.012*b)],'spine02':[(X,-0.018*b)],'neck01':[(X,0.01*b)],
       'head':[(Z,0.07*S(ph+1.2)),(X,0.02)],
       'spine05':[(Y,0.025),(Z,0.03)],
       'upperleg01.L':[(X,-0.05),(Y,-0.06)],'upperleg01.R':[(X,0.04),(Y,0.05)],
       'lowerleg01.L':[(X,0.12)],'lowerleg01.R':[(X,0.03)],
       'foot.L':[(X,-0.07),(Y,0.06)],'foot.R':[(X,-0.06),(Y,-0.05)]},
       'aim':arms(0,0.03*b,0,0)}

def locomotion(stride, knee, lift, lean, armsw, run01):
    def f(ph):
        s=S(ph); s2=S(ph+math.pi)
        kL=max(0,-S(ph-0.9)); kR=max(0,-S(ph+math.pi-0.9))
        return {'rot':{
           'upperleg01.L':[(X,-stride*s)],'upperleg01.R':[(X,-stride*s2)],
           'lowerleg01.L':[(X,knee*kL+0.06)],'lowerleg01.R':[(X,knee*kR+0.06)],
           'foot.L':[(X,-lift*max(0,S(ph+0.4))+0.12*max(0,-s))],'foot.R':[(X,-lift*max(0,S(ph+math.pi+0.4))+0.12*max(0,-s2))],
           'toe.L':[(X,-0.3*max(0,-S(ph-0.3)))],'toe.R':[(X,-0.3*max(0,-S(ph+math.pi-0.3)))],
           'spine05':[(Z,0.09*s),(Y,0.035*s)],'spine04':[(X,-lean)],'spine03':[(Z,-0.06*s)],'spine02':[(Z,-0.05*s)],
           'neck01':[(Z,0.05*s),(X,lean*0.6)],'head':[(Z,0.03*s)]},
           'aim':arms(ph,armsw,1,run01)}
    return f
walk=locomotion(0.34,0.85,0.30,0.04,0.40,0.0)
run=locomotion(0.72,1.65,0.5,0.17,0.75,1.0)
