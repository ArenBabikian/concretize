import scenic
import csv
import time

base_dir = 'evaluation/SOSYM25/scenic'
scenario_file_path = base_dir + '/scenic-concrete{actors}.scenic'

configs = [('Town04', 916, 1), ('Town04', 916, 2), ('Town04', 916, 3), ('Town04', 916, 4), 
           ('Town05', 2240, 1), ('Town05', 2240, 2), ('Town05', 2240, 3), ('Town05', 2240, 4)]

required_total_scenes = 2
timeout = 5 # seconds

def should_run():
    return len(generated_scenes) < required_total_scenes and (time.time() - start_time) < timeout

def collision_occurs(scene):
    return True
        
# TODO: calculate distance of vehicles to the intersection point along the centerline
def find_distances_to_collision_point(scene):
    collision_points = {}
    ego_position = scene.egoObject.position
    ego_centerline = scene.egoObject.behavior._kwargs['trajectory'][1].centerline
    for obj in scene.objects:
        if obj.isVehicle and obj != scene.egoObject:
            collision_points[obj] = ego_centerline.intersect(obj.behavior._kwargs['trajectory'][1].centerline)
    print(len(collision_points.values()))

for map, intersection, actors in configs:
    scenario_file = scenario_file_path.format(actors = actors)
    with open(f'{base_dir}/logical-scenarios/{map}_{intersection}_{actors}ac.csv') as f:
        reader = csv.DictReader(f)
        for params in reader:
            params['carla_map'] = map
            start_time = time.time()
            generated_scenes = []
            scenario = scenic.scenarioFromFile(scenario_file, params)
            while should_run():
                scene, n = scenario.generate()
                if collision_occurs(scene):
                    generated_scenes.append(scene)
                print(map, intersection, actors, params)