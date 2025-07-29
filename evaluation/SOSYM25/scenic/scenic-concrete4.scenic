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

actor1_startLane = filter(lambda i: i.uid == globalParameters.actor1_startLane, network.lanes)[0]
actor1_connectingLane = filter(lambda i: i.uid == globalParameters.actor1_connectingLane, network.lanes)[0]
actor1_endLane = filter(lambda i: i.uid == globalParameters.actor1_endLane, network.lanes)[0]

crossing_car_trajectory = [actor1_startLane, actor1_connectingLane, actor1_endLane]

crossing_starting_lane = actor1_startLane.union(actor1_connectingLane)
crossing_car = Car on crossing_starting_lane,
				with behavior FollowTrajectoryBehavior(trajectory = crossing_car_trajectory)

actor2_startLane = filter(lambda i: i.uid == globalParameters.actor2_startLane, network.lanes)[0]
actor2_connectingLane = filter(lambda i: i.uid == globalParameters.actor2_connectingLane, network.lanes)[0]
actor2_endLane = filter(lambda i: i.uid == globalParameters.actor2_endLane, network.lanes)[0]

crossing_car_trajectory2 = [actor2_startLane, actor2_connectingLane, actor2_endLane]

crossing_starting_lane2 = actor2_startLane.union(actor2_connectingLane)
crossing_car2 = Car on crossing_starting_lane2,
				with behavior FollowTrajectoryBehavior(trajectory = crossing_car_trajectory2)

actor3_startLane = filter(lambda i: i.uid == globalParameters.actor3_startLane, network.lanes)[0]
actor3_connectingLane = filter(lambda i: i.uid == globalParameters.actor3_connectingLane, network.lanes)[0]
actor3_endLane = filter(lambda i: i.uid == globalParameters.actor3_endLane, network.lanes)[0]

crossing_car_trajectory3 = [actor3_startLane, actor3_connectingLane, actor3_endLane]

crossing_starting_lane3 = actor3_startLane.union(actor3_connectingLane)
crossing_car3 = Car on crossing_starting_lane3,
				with behavior FollowTrajectoryBehavior(trajectory = crossing_car_trajectory2)