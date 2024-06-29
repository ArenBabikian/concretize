import logging
import os

# TODO I can probably avoid the Vector import from Scenic
from scenic.core.vectors import Vector

ALGO2OBJ = {'ga':['one'],
            'nsga2': ['actors', 'importance', 'categImpo'],
            'nsga3': ['categories', 'none', 'categImpo', 'actors']}

def getMapBoundaries(specifcation, num_obj):
    map_file = specifcation.map_file
    map_name = os.path.basename(map_file)
    bounds = [] # [loX, loY, hiX, hiY]

    # TODO tentatively removed, since the focus is to intgerate the TSE paper first
    # #if we are testing a specific intersection
    # if specifcation.tested_junction != None:
    #     intersection = specifcation.tested_junction
    #     aabb = intersection.getAABB()
    #     bounds = [aabb[0][0], aabb[1][0], aabb[0][1], aabb[1][1]]

    # if we are testing the entire map
    # TODO we might be able to get rid of this entire by checking getAABB() of the network
    # TODO make the first one an elif
    if map_name == "Town01.xodr":
        bounds = [-8, -384, 403, 9]
        bounds = [-8, -225, 196, 9] # small
    elif map_name == "Town02.xodr":
        bounds = [-15, -315, 200, -98]
    elif map_name == "Town03.xodr":
        bounds = [-158, -215, 257, 215]
        bounds = [-158, -215, 41, 64] # small
    elif map_name == "Town04.xodr":
        bounds = [-525, -250, 425, 219]
        bounds = [-32, 112, 425, 219] # small
    elif map_name == "Town05.xodr":
        bounds = [-31, -72, 71, 78]
    elif map_name == "Town10HD.xodr":
        bounds = [-126, -151, 121, 80]
    elif map_name == "Tram05.xodr":
        bounds = [-155, -101, 103, 80]
    elif map_name == "Tram05-mod.xodr":
        bounds = [-140, -160, 215, 70]
    elif map_name == "zalaFullcrop.xodr":
        bounds = [-59, 1337, 211, 1811] # full smart-city section
        # bounds = [-59, 211, 1337, 1811] # smaller version
    else:
        raise Exception(f'Map <{map_name}> is unknown to NSGA')
    loBd, hiBd = [], []
    for _ in range(num_obj):
        # TODO currently hard-coded wrt. the map
        loBd.extend(bounds[:2])
        hiBd.extend(bounds[2:])

    return loBd, hiBd


def handleConstraints(approach, specification):
    actors = specification.actors
    constraints = specification.constraints
    agg_strat = approach.aggregation_strategy
    algo_name = approach.algorithm_name
    
    # validate objective approach
    if agg_strat not in ALGO2OBJ[algo_name]:
        raise Exception(f'Invalid objective functions <{agg_strat}> for algo <{algo_name}>.')

    # obj_funcs in getHeuristic is currently hardcoded
    # exp may be generalised to any function
    # fun = [(lambda x:x**3), (lambda x:x**3), (lambda x:x**2), (lambda x:x**2), (lambda x:x**2)]
    if agg_strat == 'one':
        con2id = [0 for _ in constraints]
        exp = [1]
    elif agg_strat == 'categories':
        con2id = [int(c.type_id/10) for c in constraints]
        exp = [1, 1, 1, 1, 1, 1]
    elif agg_strat == 'actors':
        con2id = [actors.index(c.actors[0]) for c in constraints]
        # TODO: Improve this.
        # c.actors[0].name is now a string.
        # With the previous implementation, con2id = [c.actors[0].id for c in constraints],
        # in search/mhs/utils.py line 166, obj_funcs[con2id[c_id]] will fail
        exp = [1 for _ in range(len(actors))]
    elif agg_strat == 'importance':
        con2id = [int(c.type_id >= 20) for c in constraints]
        exp = [3, 2]
    elif agg_strat == 'categImpo':
        con2id = [int(c.type_id/10) for c in constraints]
        exp = [3, 3, 2, 2, 2, 3]
    elif agg_strat == 'none':
        con2id = [i for i in range(len(constraints))]
        exp = [1 for _ in range(len(constraints))]

    return con2id, exp

# TODO improve coding
def fillInstance(specification, coords):
    for i, actor in enumerate(specification.actors):

        # Notes: coords = [x_a0, y_a0, x_a1, y_a1, ...]
        x_actor = coords[2*i]
        y_actor = coords[2*i + 1]
        # TODO I can probably avoid the ector import here
        pos_actor = Vector(x_actor, y_actor)

        
        # TODO re-integrte this section
        # for handling of maneuvers and road segments within MHS
        # requires:
        # - findClosestwaypoint
        # - type2region
        # - deriveLanePortionAhead
        
        # assignedManeuver = None if i not in specification.actorIdsWithManeuver else specification.actorIdsWithManeuver[i]

        # if actor.snap_to_waypoint:
        #     #     WAYPOINT, NOT MANEUVER
        #     # (places position to closest waypoint, and assigns corresponding heading. If not on a lane, returns same point and heading 0)
        #     #     WAYPOINT,     MANEUVER
        #     # (places position to closest waypoint on lane which allows corresponding maneuevr, and assigns corresponding heading)
        #     pos_actor, currentLane, heading = findClosestWaypoint(specification, pos_actor, assignedManeuver)
        # else:
        #     # (keep point as is)
        #     if assignedManeuver != None:

        #         # NOT WAYPOINT,     MANEUVER
        #         # (Default heading if in a positin where the assigned maneuever is not possible. Otherwise, assign the correct heading)

        #         all_possible_maneuvers = specification.tested_junction.maneuversAt(pos_actor)
        #         # lane_ifAssignedManeuverIsNotPossible = None if len(all_possible_maneuvers) == 0 \
        #         #     else all_possible_maneuvers[0].connectingLane # MAY SAVE SOME TIME
        #         all_possible_maneuvers[:] = [m for m in all_possible_maneuvers if m.type == assignedManeuver]
        #         all_possible_orientations = [m.connectingLane.orientation[pos_actor] for m in all_possible_maneuvers]
        #         all_possible_maneuver_regions = [m.connectingLane for m in all_possible_maneuvers]

        #         if len(all_possible_orientations) == 0:
        #             # disect the implemntation of `specification.network._defaultRoadDirection(v)`
        #             # currentLane = lane_ifAssignedManeuverIsNotPossible # MAY SAVE SOME TIME
        #             currentLane = specification.network.roadAt(v)
        #             heading =  0 if currentLane is None else currentLane.orientation[pos_actor]
        #         else:
        #             heading = all_possible_orientations[0]
        #             currentLane = all_possible_maneuver_regions[0]

        #     else:
        #         # NOT WAYPOINT, NOT MANEUVER 
        #         # (keep point as is, assigns default heading at point)
        #         # currentLane = lane_ifAssignedManeuverIsNotPossible # MAY SAVE SOME TIME
        #         currentLane = specification.network.roadAt(v)
        #         heading = 0 if currentLane is None else currentLane.orientation[pos_actor]

        # tentative
        
        # NOT WAYPOINT, NOT MANEUVER 
        # (keep point as is, assigns default heading at point)
        # currentLane = lane_ifAssignedManeuverIsNotPossible # MAY SAVE SOME TIME
        current_lane = specification.roadmap.roadAt(pos_actor)
        heading = 0 if current_lane is None else current_lane.orientation[pos_actor]

        # Initialize Actor
        actor.position = pos_actor
        actor.heading = heading
        actor.current_lane = current_lane

        # TODO currently removed, not implemented in Scenic either
        # currentLaneAhead = deriveLanePortionAhead(pos_actor, currentLane)


def getHeuristic(specification, x, con2id, exp):

    obj_funcs = [0 for _ in range(len(exp))]
    fillInstance(specification, x)

    ## GET HEURISTIC VALUES
    logging.debug(f'Confirm the getHeuristic function in mhs/utils.py from Scenic.')
    for c_id, c in enumerate(specification.constraints):
        heu_val = c.get_heuristic_value()
        obj_funcs[con2id[c_id]] += heu_val

    out = [of**exp[i] for i, of in enumerate(obj_funcs)]
    # out = [exp[i](of) for i, of in enumerate(obj_funcs)]
    return out
