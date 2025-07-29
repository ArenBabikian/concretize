param map = localPath('../../maps/' + globalParameters.carla_map + '.xodr')
model scenic.domains.driving.model

DISTANCE_TO_INTERSECTION1 = -5

intersec = filter(lambda i: i.uid == globalParameters.intersection_uid, network.intersections)[0]

startLane = Uniform(*intersec.incomingLanes)
ego_maneuver = Uniform(*startLane.maneuvers)
ego_trajectory = [ego_maneuver.startLane, ego_maneuver.connectingLane, ego_maneuver.endLane]
ego_spwPt = startLane.centerline[-1]

ego = Car following roadDirection from ego_spwPt for DISTANCE_TO_INTERSECTION1,
		with behavior FollowTrajectoryBehavior(trajectory = ego_trajectory)

csm = Uniform(*ego_maneuver.conflictingManeuvers)
crossing_startLane = csm.startLane
crossing_car_trajectory = [csm.startLane, csm.connectingLane, csm.endLane]

crossing_starting_lane = csm.startLane.union(csm.connectingLane)
crossing_car = Car on crossing_starting_lane,
				with behavior FollowTrajectoryBehavior(trajectory = crossing_car_trajectory)

csm2 = Uniform(*ego_maneuver.conflictingManeuvers)
crossing_startLane2 = csm2.startLane
crossing_car_trajectory2 = [csm2.startLane, csm2.connectingLane, csm2.endLane]

require (crossing_startLane != crossing_startLane2)

crossing_starting_lane2 = csm2.startLane.union(csm2.connectingLane)
crossing_car2 = Car on crossing_starting_lane2,
				with behavior FollowTrajectoryBehavior(trajectory = crossing_car_trajectory2)

csm3 = Uniform(*ego_maneuver.conflictingManeuvers)
crossing_startLane3 = csm3.startLane
crossing_car_trajectory3 = [csm3.startLane, csm3.connectingLane, csm3.endLane]

require (crossing_startLane != crossing_startLane3)
require (crossing_startLane2 != crossing_startLane3)

crossing_starting_lane3 = csm3.startLane.union(csm3.connectingLane)
crossing_car3 = Car on crossing_starting_lane3,
				with behavior FollowTrajectoryBehavior(trajectory = crossing_car_trajectory3)