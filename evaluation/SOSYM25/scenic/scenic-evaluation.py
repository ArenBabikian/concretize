import json
import os
import scenic
import time
import csv

class ScenicEval():
    
    def __init__(self, scenario_file, map, intersection, actors, required_unique_scenes, timeout):
        self.scenario_file = scenario_file
        self.map = map
        self.intersection = intersection
        self.actors = actors
        self.required_unique_scenes = required_unique_scenes
        self.timeout = timeout
        self.generated_scenes = []
        self.unique_scenes = set()
        self.total_runtime = -1

    def all_scenarios_found(self):
        return len(self.unique_scenes) >= self.required_unique_scenes

    def timeout_reached(self):
        return (time.time() - self.start_time) >= self.timeout
    
    def should_run(self):
        # return (time.time() - self.start_time) < self.timeout
        return not self.all_scenarios_found() and not self.timeout_reached()

    def extract_trajectory(vehicle):
        return tuple(lane.uid for lane in vehicle.behavior._kwargs['trajectory'])

    def normalize_scene(scene):
        ego_traj = ScenicEval.extract_trajectory(scene.egoObject)

        other_trajs = [
            ScenicEval.extract_trajectory(obj)
            for obj in scene.objects
            if obj.isVehicle and obj != scene.egoObject
        ]

        other_trajs_sorted = tuple(sorted(other_trajs))

        return (ego_traj, other_trajs_sorted)
    
    def generate(self):
        self.start_time = time.time()
        self.scenario = scenic.scenarioFromFile(self.scenario_file, 
                                           {'carla_map':self.map, 'intersection_uid':'intersection' + str(self.intersection)})
        while self.should_run():
            scene, num_iterations = self.scenario.generate()
            generation_time = time.time() - self.start_time
            prev_size = len(self.unique_scenes)
            self.unique_scenes.add(ScenicEval.normalize_scene(scene))
            new_size = len(self.unique_scenes)
            if new_size > prev_size:
                self.generated_scenes.append((scene, generation_time, num_iterations))

        if self.timeout_reached():
            self.total_runtime = self.timeout
        else:
            self.total_runtime = time.time() - self.start_time
        
        return self.generated_scenes, self.unique_scenes

    def save_generation_time_to_file(self, path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', newline='') as f:
            writer = csv.writer(f, delimiter=',')
            header = ['number', 'time(s)', 'iterations']
            writer.writerow(header)
            for i, (_, time, iterations) in enumerate(self.generated_scenes):
                writer.writerow([i, time, iterations])
    
    def save_logical_scenarios_to_file(self, path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', newline='') as f:
            writer = csv.writer(f, delimiter=',')
            header = []
            for i in range(actors):
                header.append(f'actor{i}_startLane')
                header.append(f'actor{i}_connectingLane')
                header.append(f'actor{i}_endLane')
            writer.writerow(header)
            for scene in self.unique_scenes:
                lanes = []
                for lane in scene[0]:
                    lanes.append(lane)
                for other_path in scene[1]:
                    for lane in other_path:
                        lanes.append(lane)
                writer.writerow(lanes)

    def save_times(self, output_file_path):
        # Load or initialize output JSON
        if os.path.exists(output_file_path):
            with open(output_file_path, 'r') as outfile:
                try:
                    output_data = json.load(outfile)
                except json.JSONDecodeError:
                    output_data = {}
        else:
            output_data = {}

        j_id = str(self.intersection)
        n_ac = str(self.actors)

        # Ensure nested structure
        if j_id not in output_data:
            output_data[j_id] = {}
        if n_ac not in output_data[j_id]:
            output_data[j_id][n_ac] = {}

        # Update the output data with the timing values
        output_data[j_id][n_ac]['f2l-time'] = self.total_runtime
        output_data[j_id][n_ac]['f2l-required-unique-scenes'] = self.required_unique_scenes
        output_data[j_id][n_ac]['f2l-generated-scenes'] = len(self.generated_scenes)
        output_data[j_id][n_ac]['f2l-success-rate'] = len(self.unique_scenes) / self.required_unique_scenes  if self.required_unique_scenes > 0 else -1.0
        # output_data[j_id][n_ac]['l2c-time-median'] = l2c_median
        # output_data[j_id][n_ac]['l2c-success-rate'] = 1.0

        # Write back to output file
        with open(output_file_path, 'w') as outfile:
            json.dump(output_data, outfile, indent=2)

base_dir = 'evaluation/SOSYM25/scenic'
scenario_file_path = base_dir + '/scenic-maneuvers{actors}.scenic'
timeout = 20 # seconds

all_times_path = f'{base_dir}/output/times-f2l.json'

configs = [('Town04', 916, 1, 12), ('Town04', 916, 2, 56), ('Town04', 916, 3, 124), ('Town04', 916, 4, 160), 
           ('Town05', 2240, 1, 8), ('Town05', 2240, 2, 14), ('Town05', 2240, 3, 13), ('Town05', 2240, 4, 6)]
for map, intersection, actors, required in configs:
    eval = ScenicEval(scenario_file=scenario_file_path.format(actors=actors), map=map, intersection=intersection, actors=actors, required_unique_scenes=required, timeout=timeout)
    scenes, unique_scenes = eval.generate()
    eval.save_logical_scenarios_to_file(f"{base_dir}/logical-scenarios/{map}_{intersection}_{actors}ac.csv")
    eval.save_generation_time_to_file(f"{base_dir}/output/generation_time_{map}_{intersection}_{actors}ac.csv")
    eval.save_times(all_times_path)
    print("With ", actors, "actors, out of ", required, " possible unique scenes we found ", len(unique_scenes), " with a total of ", len(scenes), " scenes generated")
