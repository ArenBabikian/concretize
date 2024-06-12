
from scenic.core.vectors import Vector

def fill_actors(specification):
    for actor in specification.actors:

        # TODO clean this up, speciually the 'current_lane' computation
        pos_raw = actor.position
        if pos_raw is None:
            #position is unspecified, place at start of assigned maneuver lane
            m = actor.assigned_maneuver_instance.connectingLane
            pos_actor = m.centerline.pointAlongBy(5)
        else:
            pos_actor = Vector(pos_raw[0], pos_raw[1])

        # current_lane s complicated for the junction case
        # current_lane = specification.roadmap.roadAt(pos_actor)
        current_lane = actor.assigned_maneuver_instance.connectingLane
        heading = 0 if current_lane is None else current_lane.orientation[pos_actor]

        # Initialize Actor
        actor.position = pos_actor
        actor.heading = heading
        actor.current_lane = current_lane
