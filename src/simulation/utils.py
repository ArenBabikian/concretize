
import math
import carla
from src.model.actor import Car, Pedestrian
from scenic.domains.driving.roads import ManeuverType
from scenic.core.vectors import Vector
import matplotlib.pyplot as plt
import pandas as pd


def fix_map(client, world_name, ip, port):
    cur_world = client.get_world().get_map().name

    if cur_world != f"Carla/Maps/{world_name}":
        try:
            client.load_world(world_name)
        except:
            raise Exception(f"World {world_name} not found")
        client = carla.Client(ip, port)
        client.set_timeout(3.0)

def spawn_fixed_actors(world, actor):

    if isinstance(actor, Pedestrian):
        bp = world.get_blueprint_library().find("walker.pedestrian.0001")
    elif isinstance(actor, Car):
        # bp = world.get_blueprint_library().find("vehicle.bmw.grandtourer")
        bp = world.get_blueprint_library().find("vehicle.tesla.model3")

        c = actor.color.default
        if not c.startswith("#"):
            color = "(0,0,0)"
        else:                
            r = int(c[1:3], 16)
            g = int(c[3:5], 16)
            b = int(c[5:7], 16)
            color = carla.Color(r=r, g=g, b=b)
            color = f"({r},{g},{b})"
        # TODO red color not showing up well in simulation
        bp.set_attribute("color", str(color))

    loc = posToCarlaLocation(actor.position)
    rot = posToCarlaRotation(actor.heading)
    tr = carla.Transform(loc, rot)
    # tr = world.get_map().get_waypoint(loc).transform  # Migt cause issues with pedestrian
    # tr.location = tr.location + carla.Location(0,0,20)

    return world.spawn_actor(bp, tr)

def fix_spectator(world, junction, xs, ys):
    if junction:
        j = junction.junction_in_network
        aabb = j.getAABB()
        minx, maxx = aabb[0][0], aabb[1][0]
        miny, maxy = -aabb[0][1], -aabb[1][1] # TEMP
        c_add = 0
    else:
        minx, maxx = min(xs), max(xs)
        miny, maxy = min(ys), max(ys)
        c_add = 5

    cam_x = (maxx+minx)/2
    cam_y = (maxy+miny)/2
    if junction is None and len(xs) == 1:
        cam_z = 10
    else:
        cam_z = max(abs(maxx-minx), abs(maxy-miny))+c_add

    loc = carla.Location(x=cam_x, y=cam_y, z=cam_z)
    rot = carla.Rotation(pitch=270, yaw=270, roll=0) # camera pointing down
    return world.get_spectator().set_transform(carla.Transform(loc, rot))

def posToCarlaLocation(pos, z=None):
    if isinstance(pos, Vector):
        x, y = pos.x, pos.y
    elif isinstance(pos, list):
        x, y = pos[0], pos[1]
    else:
        raise Exception("Invalid position type")
    return carla.Location(x, -y, 2)

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

def get_type_string(type):
    if type == ManeuverType.LEFT_TURN:
        return "Left Turn"
    if type == ManeuverType.RIGHT_TURN:
        return "Right Turn"
    if type == ManeuverType.STRAIGHT:
        return "Straight"
    if type == ManeuverType.U_TURN:
        return "U Turn"

def agg_attempt_collision_near_miss(data):
    d = {}
    d['attempts'] = data['collision_occured'].count()
    d['collision'] = data['collision_occured'].sum()
    return pd.Series(d)

def generate_and_save_figure(df, groupby, further_group, file_name, xlabel, save_dir):

    
    if further_group:
        df = df[df['ego_maneuver_type'] == further_group]
        if len(df) == 0:
            return
    df_agg = df.groupby([groupby]).apply(agg_attempt_collision_near_miss)

    fig, ax = plt.subplots(figsize=(4, 4))
    categories = df_agg.index

    colors = ['#2ca02c', '#B3233B']
    attributes = ['attempts', 'collision']
    labels = ['Success', 'Collision']

    data = df_agg[attributes].values

    # NORMALIZE DATA
    # for i, d in enumerate(data):
    #     d2 = d / d.max() * 100
    #     data[i] = d2

    # Create positions for bars
    x = range(len(categories))
    x_positions = []
    for i in range(len(attributes)):
        x_positions.append([j for j in x])

    # Create the bars
    for i in range(len(attributes)):
        plt.bar(x_positions[i], data[:, i], label=labels[i], color=colors[i % len(colors)])

    # Add axis titles
    ax.set_ylabel('Percentage of simulation runs')
    plt.xticks([i for i in x], categories)
    ax.set_xlabel(xlabel)

    plt.tight_layout(pad=0.25)
    plt.legend()

    # Save the plot
    plt.savefig(f'{save_dir}/{file_name}.png')
