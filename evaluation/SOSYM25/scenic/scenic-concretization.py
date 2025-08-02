import os
import scenic
import csv
import time

from tqdm import tqdm
from utils import does_actor_pair_collide
import argparse

base_dir = 'evaluation/SOSYM25'
scenario_file_path = base_dir + '/scenic/scenic-concrete{actors}.scenic'
logical_scenario_dir_path = f'{base_dir}/all_output/scenic/logical-scenarios/'

configs = [('Town04', 916, 1, 12), ('Town04', 916, 2, 56), ('Town04', 916, 3, 124), ('Town04', 916, 4, 160), 
           ('Town05', 2240, 1, 8), ('Town05', 2240, 2, 14), ('Town05', 2240, 3, 13), ('Town05', 2240, 4, 6)]
# configs = [('Town04', 916, 4)]
# configs = [('Town05', 2240, 4)]
# configs = [('Town04', 916, 1), ('Town04', 916, 2), ('Town04', 916, 3)]

required_total_scenes = 1
iterations = 10
timeout = 10 # seconds # TODO

def timeout_reached():
    return (time.time() - start_time) >= timeout

def should_run():
    return len(generated_scenes) < required_total_scenes and (time.time() - start_time) < timeout

def all_collisions_occur(scene, threshold):
    ego_actor = scene.egoObject
    for other_actor in scene.objects:
        if not other_actor.isVehicle or other_actor == ego_actor:
            continue

        pair_collision_occurs = does_actor_pair_collide(ego_actor, other_actor, threshold)

        if not pair_collision_occurs:
            return False
    return True

def intitialize_csv(output_file_path):
    if os.path.isfile(output_file_path):
        os.remove(output_file_path)
    with open(output_file_path, 'a', newline='') as f:
        writer = csv.writer(f, delimiter=',')
        header = ['map', 'junction', 'run_id', 'actors', 'logical_scene_number', 'runtime', 'success']
        writer.writerow(header)


def save_times(map, intersection, run_id, actors, logical_scenario_id, runtime, success, output_file_path):
    with open(output_file_path, 'a', newline='') as f:
        writer = csv.writer(f, delimiter=',')
        writer.writerow([map, intersection, run_id, actors, logical_scenario_id, runtime, success])


# MAIN EXECUTION
parser = argparse.ArgumentParser(description='Run Scenic concretization with collision threshold.')
parser.add_argument('--threshold', type=float, default=-1, help='Collision threshold value (float, default: -1)')
args = parser.parse_args()

all_times_path = f'{base_dir}/all_output/scenic/l2c/concretization_times_{args.threshold}.csv'
os.makedirs(os.path.dirname(all_times_path), exist_ok=True)
intitialize_csv(all_times_path)
for map, intersection, actors, n_total_scenarios in configs:
    print(f'Running for {map} {intersection} with {actors} actors. {n_total_scenarios} total scenarios required')
    scenario_file = scenario_file_path.format(actors = actors)
    with open(f'{logical_scenario_dir_path}/{map}_{intersection}_{actors}ac.csv') as f:
        reader = csv.DictReader(f)
        for logical_scenario_id, params in tqdm(enumerate(reader), total=n_total_scenarios):
            params['carla_map'] = map
            # print(map, intersection, actors, params)
            scenario = scenic.scenarioFromFile(scenario_file, params)
            for run_id in range(iterations):
                generated_scenes = []
                start_time = time.time()
                while should_run():
                    scene, n = scenario.generate()
                    if all_collisions_occur(scene, threshold=args.threshold):
                        generated_scenes.append(scene)
                runtime = time.time() - start_time

                if runtime > timeout:
                    runtime = -1.0
                    succeed = False
                else:
                    succeed = True

                save_times(map, intersection, run_id, actors, logical_scenario_id, runtime, succeed, all_times_path)
            
