
from scenic.core.regions import PolylineRegion
from scenic.domains.driving.roads import ManeuverType

from shapely.geometry import Point
from scenic.core.vectors import Vector

def fill_logical_actors(specification):
    for actor in specification.actors:

        # TODO clean this up, speciually the 'current_lane' computation
        pos_raw = actor.position
        if pos_raw is None:
            #position is unspecified, place at start of assigned maneuver lane
            m = actor.assigned_maneuver_instance.connectingLane
            pos_actor = m.centerline.pointAlongBy(5)
        else:
            pos_actor = Vector(pos_raw[0], pos_raw[1])

        # current_lane s complicated for the junction case
        # current_lane = specification.roadmap.roadAt(pos_actor)
        current_lane = actor.assigned_maneuver_instance.connectingLane
        heading = 0 if current_lane is None else current_lane.orientation[pos_actor]

        # Initialize Actor
        actor.position = pos_actor
        actor.heading = heading
        actor.current_lane = current_lane

def fill_concrete_actors(actor, pos, current_region, pre_junc_pos=None, pre_junc_lane=None):
    pos = Vector(pos[0], pos[1])
    actor.position = pos
    actor.heading = current_region.orientation[pos]

    # set the exact path as a Polyline
    path = None
    lane_in_junction = actor.current_lane
    post_junc_cl = lane_in_junction._successor.centerline
    if pre_junc_lane == None:
        # actor is outside
        in_junc_cl = lane_in_junction.centerline
        # assert len(cl.points) == 2, f'Only works for straight roads. road has {len(cl.points)} points'
        pre_junc_cl = PolylineRegion([pos, lane_in_junction.centerline.points[0]])
        path = PolylineRegion.unionAll([pre_junc_cl, in_junc_cl, post_junc_cl])
    else:
        # actor is inside
        if actor.assigned_maneuver_instance.type == ManeuverType.STRAIGHT:
            in_junc_cl = PolylineRegion([pos, lane_in_junction.centerline.points[-1]])
        else:
            in_junc_cl = get_sub_line(lane_in_junction.centerline, pos)
        path = PolylineRegion.unionAll([in_junc_cl, post_junc_cl])

    actor.assign_exact_path_for_vis = path

    # TODO below
    # TODO
    # TODO
    # TODO
    # THIS IS SUS
    if pre_junc_pos != None:
        actor.pre_junc_position = Vector(pre_junc_pos[0], pre_junc_pos[1])
        actor.pre_junc_heading = pre_junc_lane.orientation[pre_junc_pos]


def get_sub_line(line, pos):
    smallest_d = float('inf')
    best_i = -1
    for i, p in enumerate(line.points):
        d = Point(p).distance(Point(pos))
        if d < smallest_d:
            smallest_d = d
            best_i = i
    return PolylineRegion(points=line.points[best_i:])
