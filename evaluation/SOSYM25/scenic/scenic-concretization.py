import json
import os
import statistics
import scenic
import csv
import time

base_dir = 'evaluation/SOSYM25/scenic'
scenario_file_path = base_dir + '/scenic-concrete{actors}.scenic'

configs = [('Town04', 916, 1), ('Town04', 916, 2), ('Town04', 916, 3), ('Town04', 916, 4), 
           ('Town05', 2240, 1), ('Town05', 2240, 2), ('Town05', 2240, 3), ('Town05', 2240, 4)]

required_total_scenes = 2
timeout = 5 # seconds

def timeout_reached():
    return (time.time() - start_time) >= timeout

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

def initialize_times_json(output_file_path, j_id, n_ac):

    # Load or initialize output JSON
    if os.path.exists(output_file_path):
        with open(output_file_path, 'r') as outfile:
            try:
                output_data = json.load(outfile)
            except json.JSONDecodeError:
                output_data = {}
    else:
        output_data = {}

    j_id = str(j_id)
    n_ac = str(n_ac)

    # Ensure nested structure
    if j_id not in output_data:
        output_data[j_id] = {}
    if n_ac not in output_data[j_id]:
        output_data[j_id][n_ac] = {}
    output_data[j_id][n_ac]['l2c-successes'] = []
    output_data[j_id][n_ac]['l2c-times-of-successes'] = []
    output_data[j_id][n_ac]['agg-l2c-success-rate'] = -1.0
    output_data[j_id][n_ac]['agg-l2c-time-median-of-successes'] = -1.0

    with open(output_file_path, 'w') as outfile:
        json.dump(output_data, outfile, indent=2)

def save_times(scenario_runtime, success, output_file_path, j_id, n_ac):
    # Load or initialize output JSON
    with open(output_file_path, 'r') as outfile:
        try:
            output_data = json.load(outfile)
        except json.JSONDecodeError:
            output_data = {}

    j_id = str(j_id)
    n_ac = str(n_ac)

    # Update the output data with success rate values
    output_data[j_id][n_ac]['l2c-successes'].append(success)

    num_successes = sum(output_data[j_id][n_ac]['l2c-successes'])
    num_attempts = len(output_data[j_id][n_ac]['l2c-successes'])
    output_data[j_id][n_ac]['agg-l2c-success-rate'] = num_successes / num_attempts if num_attempts > 0 else -1.0

    # Update the output data with the timing values
    if success:
        output_data[j_id][n_ac]['l2c-times-of-successes'].append(scenario_runtime)

    all_successes = output_data[j_id][n_ac]['l2c-times-of-successes']
    output_data[j_id][n_ac]['agg-l2c-time-median-of-successes'] = statistics.median(all_successes) if all_successes else -1.0

    # Write back to output file
    with open(output_file_path, 'w') as outfile:
        json.dump(output_data, outfile, indent=2)


all_times_path = f'{base_dir}/output/times-l2c.json'

for map, intersection, actors in configs:
    initialize_times_json(all_times_path, intersection, actors)
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

            if timeout_reached():
                scenario_runtime = timeout
                succeed = 0.0
            else:
                scenario_runtime = time.time() - start_time
                succeed = 1.0

            save_times(scenario_runtime, succeed, all_times_path, intersection, actors)
            
