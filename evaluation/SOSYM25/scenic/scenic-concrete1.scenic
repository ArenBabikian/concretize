param map = localPath('../../../maps/' + globalParameters.carla_map + '.xodr')
model scenic.domains.driving.model

DISTANCE_TO_INTERSECTION1 = -5


actor0_startLane = filter(lambda i: i.uid == globalParameters.actor0_startLane, network.lanes)[0]
actor0_connectingLane = filter(lambda i: i.uid == globalParameters.actor0_connectingLane, network.lanes)[0]
actor0_endLane = filter(lambda i: i.uid == globalParameters.actor0_endLane, network.lanes)[0]

ego_trajectory = [actor0_startLane, actor0_connectingLane, actor0_endLane]
ego_spwPt = actor0_startLane.centerline[-1]

ego = Car following roadDirection from ego_spwPt for DISTANCE_TO_INTERSECTION1,
		with behavior FollowTrajectoryBehavior(trajectory = ego_trajectory)