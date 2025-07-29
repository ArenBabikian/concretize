import os
import scenic
import time
import csv

class ScenicEval():
    
    def __init__(self, scenario_file, map, intersection, required_unique_scenes, timeout):
        self.scenario_file = scenario_file
        self.map = map
        self.intersection = intersection
        self.required_unique_scenes = required_unique_scenes
        self.timeout = timeout
        self.generated_scenes = []
        self.unique_scenes = set()
    
    def should_run(self):
        return len(self.unique_scenes) < self.required_unique_scenes and (time.time() - self.start_time) < self.timeout

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

base_dir = 'evaluation/SOSYM25/scenic'
scenario_file_path = base_dir + '/scenic-maneuvers{actors}.scenic'
timeout = 5 # seconds

configs = [('Town04', 916, 1, 12), ('Town04', 916, 2, 56), ('Town04', 916, 3, 248), ('Town04', 916, 4, 1208), 
           ('Town05', 2240, 1, 8), ('Town05', 2240, 2, 14), ('Town05', 2240, 3, 26), ('Town05', 2240, 4, 62)]
for map, intersection, actors, required in configs:
    eval = ScenicEval(scenario_file=scenario_file_path.format(actors=actors), map=map, intersection=intersection, required_unique_scenes=required, timeout=timeout)
    scenes, unique_scenes = eval.generate()
    eval.save_logical_scenarios_to_file(f"{base_dir}/logical-scenarios/{map}_{intersection}_{actors}ac.csv")
    eval.save_generation_time_to_file(f"{base_dir}/output/generation_time_{map}_{intersection}_{actors}ac.csv")
    print("With ", actors, "actors, out of ", required, " possible unique scenes we found ", len(unique_scenes), " with a total of ", len(scenes), " scenes generated")
