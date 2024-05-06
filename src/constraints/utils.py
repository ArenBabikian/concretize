import inspect
import scenic.core.geometry as geom

from src.model.road_components import Drivable_Type, Junction_Type, Map_Element_Instance, Map_Element_Type, Road_Type

def position_helper(src_pos, src_head, tgt_pos, angle):
    a = geom.viewAngleToPoint(tgt_pos[:2], src_pos[:2], src_head)
    real_ang = abs(a)
    inRange = real_ang - angle < 0
    return 0 if inRange else real_ang - angle

def distance_helper(src_pos, tgt_pos, lb, ub):
    delta = ((src_pos[0] - tgt_pos[0])**2 + (src_pos[1] - tgt_pos[1])**2)**0.5
    if delta < lb:
        return lb - delta
    elif ub is not None and delta > ub:
        return delta - ub
    else:
        return 0

def get_container(target, roadmap):

    if isinstance(target, Map_Element_Type):
        if isinstance(target, Road_Type):
            return roadmap.roadRegion # All roads (not part of an intersection).
        elif isinstance(target, Junction_Type):
            return roadmap.intersectionRegion # All intersections
        elif isinstance(target, Drivable_Type):
            # has to be after its subtypes
            return roadmap.drivableRegion # All sidewalks union all crossings.
        else:
            raise Exception(f'Unhandled target type <{target}>')
        # TYPE2REGION = {
        #     'default': scenario.containerOfObject(vi), # Default region wrt. actor type
        #     'drivable': network.drivableRegion, # All lanes union all intersections.
        #     'walkable': network.walkableRegion, # All sidewalks union all crossings.
        #     'road': network.roadRegion, # All roads (not part of an intersection).
        #     'lane': network.laneRegion, # All lanes
        #     'intersection': network.intersectionRegion, # All intersections.
        #     'crossing': network.crossingRegion, # All pedestrian crossings.
        #     'sidewalk': network.sidewalkRegion, # All sidewalks
        #     'curb': network.curbRegion, # All curbs of ordinary roads.
        #     'shoulder': network.shoulderRegion # All shoulders (by default, includes parking lanes).
        # }
    elif isinstance(target, Map_Element_Instance):
        raise Exception(f'Unhandled target type <{target}>')
    else:
        raise Exception(f'Unhandled target type <{target}>')
