param map = localPath('../../../maps/' + globalParameters.carla_map + '.xodr')
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
crossing_car_trajectory = [csm.startLane, csm.connectingLane, csm.endLane]

crossing_starting_lane = Uniform(csm.startLane, csm.connectingLane)
crossing_car = Car on crossing_starting_lane.centerline,
				with behavior FollowTrajectoryBehavior(trajectory = crossing_car_trajectory)

csm2 = Uniform(*ego_maneuver.conflictingManeuvers)
crossing_car_trajectory2 = [csm2.startLane, csm2.connectingLane, csm2.endLane]

require (csm != csm2)

crossing_starting_lane2 = Uniform(csm2.startLane, csm2.connectingLane)
crossing_car2 = Car on crossing_starting_lane2.centerline,
				with behavior FollowTrajectoryBehavior(trajectory = crossing_car_trajectory2)