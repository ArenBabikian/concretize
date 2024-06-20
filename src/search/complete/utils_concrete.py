
import logging
from scenic.domains.driving.roads import Maneuver, ManeuverType, Intersection
import src.search.complete.constants as cst

from scenic.core.regions import EmptyRegion
from scenic.core.vectors import Vector
from shapely.geometry import MultiLineString, LineString

from src.search.complete.utils import fill_concrete_actors

def detect_ego_and_other_actors(c, log=True):
    # validate; ensure that ego actor is involved
    ego_actor, other_actor = None, None
    for a in c.actors:
        if a.is_ego:
            ego_actor = a
        else:
            other_actor = a
    if log:
        if ego_actor is None:
            logging.warning(f'The ego actor not involved in collision constraint <{c}>. This constraint is not considered when deriving the concrete scenario.')
    return ego_actor, other_actor

def get_collisions_in_order(collision_constraints):
    
    ranked_non_ego_by_dist_for_ego = []
    for c in collision_constraints:

        # validate; ensure that ego actor is involved
        ego_actor, other_actor = detect_ego_and_other_actors(c)
        if ego_actor is None:
            continue

        # 1. get collision region
        collision_region = c.coll_region
        assert collision_region != EmptyRegion('')

        # 2. (EGO): Find EGO distances to relevant points (distance is INSIDE junction)
        ego_region = ego_actor.assigned_maneuver_instance.connectingLane
        d_e_en, d_e_mi, d_e_ex = find_dist_to_coll_reg(collision_region, ego_region)
        
        # Step 4 (OTHER): Find OTHER distances to relevant points (distance is INSIDE junction)
        other_region = other_actor.assigned_maneuver_instance.connectingLane
        d_o_en, d_o_mi, d_o_ex = find_dist_to_coll_reg(collision_region, other_region)

        # we include:
        # (1) id of corresponding non_ego vehicle
        # (2) distance for ego from start of intersection to start of collision zone (where it woill wait)
        # (3) distance the non-ego will traverse while ego is waiting
        # TODO : either include the actor or the constraint
        ranked_non_ego_by_dist_for_ego.append({'actor':other_actor, 'dist_to_for_ego':d_e_en, 'dist_in_for_non':d_o_ex-d_o_mi, 'time_to_add':0})

    ranked_non_ego_by_dist_for_ego.sort(key=lambda x:x['dist_to_for_ego'])
    return ranked_non_ego_by_dist_for_ego

def setup_other_actors(collision_constraints, all_collision_stats, tested_junction):
    # TODO optimize this function, potentially merge with get_collisions_in_order()
    
    for c in collision_constraints:

        # validate; ensure that ego actor is involved
        ego_actor, other_actor = detect_ego_and_other_actors(c, False)
        if ego_actor is None:
            continue

        # 1. get collision region
        collision_region = c.coll_region
        assert collision_region != EmptyRegion('')

        # 2. (EGO): Find EGO distances to relevant points (distance is INSIDE junction)
        ego_region = ego_actor.assigned_maneuver_instance.connectingLane
        d_e_entering, d_e_middle, d_e_exitting = find_dist_to_coll_reg(collision_region, ego_region)
        
        # 3. (EGO): Find EGO time to the relevant point
        d_e_relevant = d_e_entering
        t_e_to_relevant = find_time_to_relevant(ego_actor, d_e_relevant, cst.EGO_DIST_BEFORE_JUNC)

        # 4. (OTHER) : find time to add due to other collision regions on the way 
        # NOTE: the non_ego should reach the point_of_interest at the same time as ego reaches the point of interest (i.e. in t_e_to_relevant time) 
        time_to_add_list = [ stats['time_to_add'] for stats in filter(lambda non_ego_stats: non_ego_stats['actor'] == other_actor, all_collision_stats)]
        assert len(time_to_add_list) == 1
        time_to_add_new = time_to_add_list[0] # to consider delays caused by previously occured collisions
        t_o_to_relevant = t_e_to_relevant + time_to_add_new

        # 5. (OTHER): Find OTHER distances to relevant points (distance is INSIDE junction)
        other_region = other_actor.assigned_maneuver_instance.connectingLane
        d_o_entering, d_o_middle, d_o_exitting = find_dist_to_coll_reg(collision_region, other_region)

        # 6. (OTHER) : Select relevant point
        # NOTE we select NON_EGO_MIDDLE point, unless NON_EGO is performing a right turn, in which case, we select NON_EGO_EXITTING
        # TODO maybe only do this if ego is going straight?
        d_o_relevant = d_o_exitting if other_actor.assigned_maneuver_instance.type == ManeuverType.RIGHT_TURN else d_o_middle
        assert isinstance(other_actor.assigned_maneuver_instance, Maneuver)

        # 7. (OTHER) : Find OTHER position from required time
        other_starting_point, other_starting_reg, other_pre_junc_point, other_pre_junc_reg = find_init_position(other_actor, t_o_to_relevant, d_o_relevant, other_region, tested_junction)

        # 8. (OTHER): Set up other actor
        fill_concrete_actors(other_actor, other_starting_point, other_starting_reg, other_pre_junc_point, other_pre_junc_reg)


def find_dist_to_coll_reg(collision_reg, actor_lane):
    cl = actor_lane.centerline

    # get centerline in 
    cl_InColl = cl.intersect(collision_reg)
    cl_len_inColl = cl_InColl.length

    # get relevant points
    pt_start = cl_InColl.points[0]
    ve_start = Vector(pt_start[0], pt_start[1])
    
    d_coll_middle = cl_len_inColl/2
    pt_middle = cl_InColl.pointAlongBy(cl_len_inColl/2) 
    ve_middle = Vector(pt_middle[0], pt_middle[1])

    d_coll_end = cl_len_inColl
    pt_end = cl_InColl.points[-1]
    ve_end = Vector(pt_end[0], pt_end[1])

    # get centerline outside collision region
    cl_OutColl = cl.difference(collision_reg)
    if isinstance(cl_OutColl.lineString, MultiLineString):
        cl_OutColl.lineString = cleanedMultiLineString(cl_OutColl.lineString)
        new_geoms = cl_OutColl.lineString.geoms
        
        assert len(new_geoms) in [1, 2]

        linestring_before_coll = new_geoms[0]
        len_to_CollReg = linestring_before_coll.length
    else:
        # Happens for ego=left, non-ego=straight
        len_to_CollReg = cl_OutColl.length

    # Determine distances
    d_start =  len_to_CollReg
    d_middle = len_to_CollReg+d_coll_middle
    d_end = len_to_CollReg+d_coll_end

    # VALIDATION
    assert cl.pointAlongBy(d_start).distanceTo(ve_start) < cst.LINESTRING_THRESHOLD, \
        f'START ISSUE: pointAlong{cl.pointAlongBy(d_start)}, pointComputed{ve_start}, difference:{cl.pointAlongBy(d_start).distanceTo(ve_start)}'
    assert cl.pointAlongBy(d_middle).distanceTo(ve_middle) < cst.LINESTRING_THRESHOLD, \
        f'MID ISSUE: pointAlong{cl.pointAlongBy(d_middle)}, pointComputed{ve_middle}, difference:{cl.pointAlongBy(d_middle).distanceTo(ve_middle)}'
    assert cl.pointAlongBy(d_end).distanceTo(ve_end) < cst.LINESTRING_THRESHOLD, \
        f'END ISSUE: pointAlong{cl.pointAlongBy(d_end)}, pointComputed{ve_end}, difference:{cl.pointAlongBy(d_end).distanceTo(ve_end)}'

    return d_start, d_middle, d_end

def cleanedMultiLineString(ls):

    new_mls = ls
    # # CLEAN
    # geoms = ls.geoms
    # segs_to_add = []
    # for g in geoms:
    #     if g.length < THRESHOLD:
    #         continue # Too small
    #     if g.coords[0] == g.coords[-1]:
    #         continue # starts and ends at the smae place
    #     segs_to_add.append(g)
    # new_mls = shapely.geometry.MultiLineString(segs_to_add)

    # UNIFY
    if len(new_mls.geoms) > 1:
        all_segs = []

        cur_lane = list(new_mls.geoms[0].coords)
        for i_cur, l_cur in enumerate(new_mls.geoms[:-1].geoms):
            l_next = new_mls.geoms[i_cur + 1]

            cur_last = l_cur.coords[-1]
            next_first = l_next.coords[0]

            if cur_last == next_first:
                cur_lane.extend(l_next.coords[1:])
            else:
                all_segs.append(LineString(cur_lane))
                cur_lane = list(l_cur.coords)
        
        all_segs.append(LineString(cur_lane))  
        new_mls = MultiLineString( all_segs )

    return new_mls
    
def calculate_time_for_man(collision_stats):
    
    dist_in_collision_region = collision_stats['dist_in_for_non']
    colliding_actor = collision_stats['actor']

    actor_length = colliding_actor.length
    actor_speed_in_junction = colliding_actor.speed_profile.speed_in_junction
    # TODO potentially improve this
    # TODO potentially modify the calculation if collision regions are overlapping
    # calculate time for non-ego to finish maneuver (ego decels during this time)
    time_for_prev_man = (dist_in_collision_region + actor_length) / actor_speed_in_junction
    return time_for_prev_man + cst.ACCEL_TIME_PENALTY

def find_time_to_relevant(actor, d_in, d_out):
    return d_in / actor.speed_profile.speed_in_junction + d_out / actor.speed_profile.speed_on_road

def find_init_position(actor, t_total, d_in_junction, lane_inside_junction, tested_junction):
    '''
    Returns (initial position, initial lane, point before junction (if inital point is in junc), lane before junction (if inital point is in junc)
    '''

    t_for_full_man_in_junction = d_in_junction / actor.speed_profile.speed_in_junction
    if t_for_full_man_in_junction >= t_total:
        # Case 1: vehicle must start inside the junction
        d_req_in_junction = t_total * actor.speed_profile.speed_in_junction
        starting_pos = lane_inside_junction.centerline.pointAlongBy(d_in_junction-d_req_in_junction)

        # to prep the return
        lane_before_junc = lane_inside_junction._predecessor
        reg_before_junc = lane_before_junc.sections[-1]
        pre_junc_pos = reg_before_junc.centerline.pointAlongBy(-1)
        
        return starting_pos, lane_inside_junction, pre_junc_pos, lane_before_junc
    else:
        # Case 2: vehicle must start before the junction
        # TODO do this recursively, to avoid the 2 unhandled cases
        # TODO make this more generalizable
        t_before_junc = t_total-t_for_full_man_in_junction
        d_before_junc = t_before_junc * actor.speed_profile.speed_on_road

        lane_before_junc = lane_inside_junction._predecessor
        reg_before_junc = lane_before_junc.sections[-1]

        if d_before_junc <= reg_before_junc.centerline.length:
            starting_pos = reg_before_junc.centerline.pointAlongBy(-d_before_junc)
            return starting_pos, lane_before_junc, None, None
        else:
            # VEHICLE NEEDS TO START 2 ELEMENTS BEFORE INTERSECTION
            d_before_before_junc = d_before_junc - reg_before_junc.centerline.length

            if len(lane_before_junc.sections) > 1:
                logging.error('Not implemented: Complex 1')
                exit()

            lane_before_before_junc = lane_before_junc._predecessor
            if lane_before_before_junc == None:
                # this means that the before_before is a junction
                road_before_junc = lane_before_junc.road
                road_before_before_junc = road_before_junc._predecessor # this is an intersection
                if road_before_before_junc == tested_junction:
                    road_before_before_junc = road_before_junc._successor
                assert isinstance(road_before_before_junc, Intersection)

                # find the preceding straight road
                condition = lambda man: man.type == ManeuverType.STRAIGHT and man.endLane == lane_before_junc
                all_before_befores = [m.connectingLane for m in filter(condition, road_before_before_junc.maneuvers)]
                # for m in road_before_before_junc.maneuvers:
                #     print(m)
                assert len(all_before_befores) == 1, print(f'found {len(all_before_befores)} lanes')

                lane_before_before_junc = all_before_befores[0]

            # COMPUTE DISTANCE IN BEFORE BEFORE ELEMENT
            if d_before_before_junc > lane_before_before_junc.centerline.length:
                logging.error('Not implemented: Complex 2')
                exit()
            
            real_reg_before_before_junc = lane_before_before_junc.sections[-1]
            starting_pos = real_reg_before_before_junc.centerline.pointAlongBy(-d_before_before_junc)
            return starting_pos, lane_before_before_junc, None, None
        
def calculate_timeout(actor, region, t_added_for_collisions):

    dist_in_junc = region.centerline.length
    t_in_junc = dist_in_junc / actor.speed_profile.speed_in_junction
    dist_out_junction = 2*cst.EGO_DIST_BEFORE_JUNC
    t_out_junc = dist_out_junction / actor.speed_profile.speed_on_road

    return int(cst.INITIAL_SECONDS_DELAY + cst.TIME_MULTIPLER * (t_in_junc + t_out_junc  + t_added_for_collisions))
