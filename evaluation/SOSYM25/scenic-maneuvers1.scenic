param map = localPath('../../maps/Town04.xodr')
param carla_map = 'Town04'
model scenic.domains.driving.model

DISTANCE_TO_INTERSECTION1 = Uniform(15, 20) * -1
SAFETY_DISTANCE = 20
BRAKE_INTENSITY = 1.0

intersec = filter(lambda i: i.uid == "intersection916", network.intersections)[0]

startLane = Uniform(*intersec.incomingLanes)
ego_maneuver = Uniform(*startLane.maneuvers)
ego_trajectory = [ego_maneuver.startLane, ego_maneuver.connectingLane, ego_maneuver.endLane]

ego_spwPt = startLane.centerline[-1]

ego = Car following roadDirection from ego_spwPt for DISTANCE_TO_INTERSECTION1,
		with behavior FollowTrajectoryBehavior(trajectory = ego_trajectory)