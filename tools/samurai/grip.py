import bpy, math
from mathutils import Vector, Matrix
import anim, clips
def solve_wrist(arm):
    best=None
    for i in range(72):
        tw=-math.pi+i*(2*math.pi/72); clips.WRIST_R_TWIST[0]=tw
        anim.pose(arm,clips.idle(0))
        pb=arm.pose.bones
        ax=(pb['finger5-1.R'].head-pb['finger2-1.R'].head).normalized()
        sc=-ax.z - 0.3*abs(ax.x)
        if best is None or sc>best[0]: best=(sc,tw)
    clips.WRIST_R_TWIST[0]=best[1]; anim.pose(arm,clips.idle(0))
    pb=arm.pose.bones
    pts=[pb[f'finger{f}-1.R'].head for f in range(2,6)]+[pb[f'finger{f}-2.R'].tail for f in range(2,6)]
    c=sum(pts,Vector())/len(pts)
    ax=(pb['finger5-1.R'].head-pb['finger2-1.R'].head).normalized()
    print('wrist twist',best[1],'grip axis',tuple(round(x,3) for x in ax),'center',tuple(round(x,3) for x in c))
    return c, ax
def to_rest(arm, bone, pts_world):
    """Pontos no espaco da armature com a pose atual -> espaco de repouso do osso (para skin rigido)."""
    pb=arm.pose.bones[bone]; M=arm.data.bones[bone].matrix_local @ pb.matrix.inverted()
    return [M @ Vector(p) for p in pts_world]
