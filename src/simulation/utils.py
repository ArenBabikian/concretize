
import math
import carla
from src.model.actor import Car, Pedestrian
from scenic.core.vectors import Vector


def fix_map(client, world_name, ip, port):
    cur_world = client.get_world().get_map().name

    if cur_world != f"Carla/Maps/{world_name}":
        client.load_world(world_name)
        client = carla.Client(ip, port)
        client.set_timeout(3.0)

def spawn_fixed_actors(world, actor):

    if isinstance(actor, Pedestrian):
        bp = world.get_blueprint_library().find("walker.pedestrian.0001")
    elif isinstance(actor, Car):
        bp = world.get_blueprint_library().find("vehicle.bmw.grandtourer")

        # TODO get color
        color = '128,64,0'
        bp.set_attribute("color", color)

    loc = posToCarlaLocation(actor.position)
    rot = posToCarlaRotation(actor.heading)
    tr = carla.Transform(loc, rot)
    # tr = world.get_map().get_waypoint(loc).transform  # Migt cause issues with pedestrian
    # tr.location = tr.location + carla.Location(0,0,20)

    # TODO not sure if return is correct
    return world.spawn_actor(bp, tr)

def fix_spectator(world, xs, ys):
    minx, maxx = min(xs), max(xs)
    miny, maxy = min(ys), max(ys)

    cam_x = (maxx+minx)/2
    cam_y = (maxy+miny)/2
    if len(xs) == 1:
        cam_z = 10
    else:
        cam_z = max(abs(maxx-minx), abs(maxy-miny))

    loc = carla.Location(x=cam_x, y=cam_y, z=cam_z)
    rot = carla.Rotation(pitch=-88.99, yaw=0.01, roll=-179.99) # camera pointing down
    return world.get_spectator().set_transform(carla.Transform(loc, rot))

def posToCarlaLocation(pos, z=None):
    if isinstance(pos, Vector):
        x, y = pos.x, pos.y
    elif isinstance(pos, list):
        x, y = pos[0], pos[1]
    else:
        raise Exception("Invalid position type")
    return carla.Location(x, -y, 5)

def posToCarlaRotation(heading):
	yaw = math.degrees(-heading) - 90
	return carla.Rotation(yaw=yaw)

def destroy_all_actors(world):
    vehicles = world.get_actors().filter('vehicle.*')
    pedestrians = world.get_actors().filter('walker.*')
    for actor in vehicles:
        actor.destroy()
    for actor in pedestrians:
        actor.destroy()