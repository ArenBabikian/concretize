import scenic.core.geometry as geom

def position_helper(src_pos, src_head, tgt_pos, angle):
    a = geom.viewAngleToPoint(tgt_pos[:2], src_pos[:2], src_head)
    real_ang = abs(a)
    inRange = real_ang - angle < 0
    return 0 if inRange else real_ang - angle