import math
import scenic
from shapely.geometry.point import Point
import sys
import os
from scenic.core.object_types import Object
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from src.search.complete.utils_concrete import find_dist_to_coll_reg

# Equivalent to the Complete parameters
IN_SPEED = 3  # m/s
OUT_SPEED = 4  # m/s
ACTOR_WIDTH = 2
ACTOR_LENGTH = 5
ACTOR_CORNER_DIST = math.hypot(ACTOR_WIDTH / 2, ACTOR_LENGTH / 2)

def find_time_to_relevant(d_in, d_out):
    # print(f"{d_in/IN_SPEED} + {d_out/OUT_SPEED} = {d_in/IN_SPEED + d_out/OUT_SPEED}")
    return d_in / IN_SPEED + d_out / OUT_SPEED

def get_dist_from_cur_to_end(point, region):
    cl = region.centerline  # centerline of connectingLane
    ls = cl.lineString  # lineString of connectingLane
    return ls.length - ls.project(point)

def get_dist_from_start_to_cur(point, region):
    cl = region.centerline  # centerline of connectingLane
    ls = cl.lineString  # lineString of connectingLane
    return ls.project(point)

def does_actor_pair_collide(ego_actor, other_actor, threshold=-1):
    #######
    # SETUP
    #######
    ego_traj_seq = ego_actor.behavior._kwargs['trajectory']
    ego_position = ego_actor.position
    ego_point = Point(ego_position[0], ego_position[1])

    ego_pre_region = ego_traj_seq[0]
    ego_coll_region = ego_traj_seq[1]

    other_traj_seq = other_actor.behavior._kwargs['trajectory']
    other_position = other_actor.position
    other_point = Point(other_position[0], other_position[1])

    other_pre_region = other_traj_seq[0]
    other_coll_region = other_traj_seq[1]

    ########
    # EGO
    
    # (EGO-0) Ego pre-junc segment
    ego_dist_pre = get_dist_from_cur_to_end(ego_point, ego_pre_region)

    # (EGO-1) Ego in-junc segment
    d_e_entering, d_e_middle, d_e_exitting = find_dist_to_coll_reg(other_coll_region, ego_coll_region)
    ego_dist_in = d_e_entering

    t_ego = find_time_to_relevant(ego_dist_in, ego_dist_pre)

    ##########
    # NON-EGO

    # Get target point of interest

    # Hard-coded for now
    right_turn_maneuver_ids = ["road968_lane0", "road955_lane0", "road943_lane0", "road988_lane0", "road2241_lane0", "road2292_lane0" ]

    d_o_entering, d_o_middle, d_o_exitting = find_dist_to_coll_reg(ego_coll_region, other_coll_region)
    other_region_id = other_coll_region.id
    d_point_of_interest = d_o_exitting if other_region_id in right_turn_maneuver_ids else d_o_middle

    if other_position in other_pre_region:
        # We are PRE JUNCTION
        
        # PRE-DIST
        oth_dist_pre = get_dist_from_cur_to_end(other_point, other_pre_region)

        # IN-DIST
        oth_dist_in = d_point_of_interest
    elif other_position in other_coll_region:
        # We are IN JUNCTION
        
        # PRE-DIST
        oth_dist_pre = 0

        # IN-DIST
        d_start_to_cur = get_dist_from_start_to_cur(other_point, other_coll_region)

        oth_dist_in = d_point_of_interest - d_start_to_cur  # distance from start of connectingLane to the current position of the other actor
    else:
        raise ValueError("Other actor's position is not in any relevant region")
    
    t_other = find_time_to_relevant(oth_dist_in, oth_dist_pre)
    
    # COLLISION CONDITION
    # In the ideal case, t_ego and t_other should be equal (this would make the scenrio equivalent to what Complete would output)
    # Nevertheless, we allow for a margin of error d, s.t. a scenario is considered to be colliding if at the moment where ego reaches its intended point, at least one part of the other actor is on its inteded point

    d_threshold = threshold if threshold >= 0 else ACTOR_CORNER_DIST
    d_other_overshoot = abs(t_other - t_ego) * IN_SPEED  # how much the other actor overshoots the ego actor's time
    collision_occurs = d_other_overshoot < d_threshold

    # print('------')
    return collision_occurs
    
