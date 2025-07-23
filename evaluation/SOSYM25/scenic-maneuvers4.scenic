param map = localPath('../../maps/Town04.xodr')
param carla_map = 'Town04'
model scenic.domains.driving.model

DISTANCE_TO_INTERSECTION1 = Uniform(15, 20) * -1
DISTANCE_TO_INTERSECTION2 = Uniform(10, 15) * -1
DISTANCE_TO_INTERSECTION3 = Uniform(10, 15) * -1
DISTANCE_TO_INTERSECTION4 = Uniform(10, 15) * -1
SAFETY_DISTANCE = 20
BRAKE_INTENSITY = 1.0

intersec = filter(lambda i: i.uid == "intersection916", network.intersections)[0]

startLane = Uniform(*intersec.incomingLanes)
ego_maneuver = Uniform(*startLane.maneuvers)
ego_trajectory = [ego_maneuver.startLane, ego_maneuver.connectingLane, ego_maneuver.endLane]

csm = Uniform(*ego_maneuver.conflictingManeuvers)
crossing_startLane = csm.startLane
crossing_car_trajectory = [csm.startLane, csm.connectingLane, csm.endLane]

csm2 = Uniform(*ego_maneuver.conflictingManeuvers)
crossing_startLane2 = csm2.startLane
crossing_car_trajectory2 = [csm2.startLane, csm2.connectingLane, csm2.endLane]

csm3 = Uniform(*ego_maneuver.conflictingManeuvers)
crossing_startLane3 = csm3.startLane
crossing_car_trajectory3 = [csm3.startLane, csm3.connectingLane, csm3.endLane]

require (crossing_startLane != crossing_startLane2)
require (crossing_startLane != crossing_startLane3)
require (crossing_startLane2 != crossing_startLane3)

ego_spwPt = startLane.centerline[-1]
csm_spwPt = crossing_startLane.centerline[-1]
csm_spwPt2 = crossing_startLane2.centerline[-1]
csm_spwPt3 = crossing_startLane3.centerline[-1]

ego = Car following roadDirection from ego_spwPt for DISTANCE_TO_INTERSECTION1,
		with behavior FollowTrajectoryBehavior(trajectory = ego_trajectory)

crossing_car = Car following roadDirection from csm_spwPt for DISTANCE_TO_INTERSECTION2,
				with behavior FollowTrajectoryBehavior(trajectory = crossing_car_trajectory)

crossing_car2 = Car following roadDirection from csm_spwPt2 for DISTANCE_TO_INTERSECTION3,
				with behavior FollowTrajectoryBehavior(trajectory = crossing_car_trajectory2)

crossing_car3 = Car following roadDirection from csm_spwPt3 for DISTANCE_TO_INTERSECTION4,
				with behavior FollowTrajectoryBehavior(trajectory = crossing_car_trajectory3)

# require eventually (distance to crossing_car) < 2