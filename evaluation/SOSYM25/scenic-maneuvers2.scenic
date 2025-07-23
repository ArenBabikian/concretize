param map = localPath('../../maps/Town04.xodr')
param carla_map = 'Town04'
model scenic.domains.driving.model

DISTANCE_TO_INTERSECTION1 = Uniform(15, 20) * -1
DISTANCE_TO_INTERSECTION2 = Uniform(10, 15) * -1
SAFETY_DISTANCE = 20
BRAKE_INTENSITY = 1.0

intersec = filter(lambda i: i.uid == "intersection916", network.intersections)[0]

startLane = Uniform(*intersec.incomingLanes)
ego_maneuver = Uniform(*startLane.maneuvers)
ego_trajectory = [ego_maneuver.startLane, ego_maneuver.connectingLane, ego_maneuver.endLane]

csm = Uniform(*ego_maneuver.conflictingManeuvers)
crossing_startLane = csm.startLane
crossing_car_trajectory = [csm.startLane, csm.connectingLane, csm.endLane]

ego_spwPt = startLane.centerline[-1]
csm_spwPt = crossing_startLane.centerline[-1]

ego = Car following roadDirection from ego_spwPt for DISTANCE_TO_INTERSECTION1,
		with behavior FollowTrajectoryBehavior(trajectory = ego_trajectory)

crossing_car = Car following roadDirection from csm_spwPt for DISTANCE_TO_INTERSECTION2,
				with behavior FollowTrajectoryBehavior(trajectory = crossing_car_trajectory)

require eventually (distance to crossing_car) < 2