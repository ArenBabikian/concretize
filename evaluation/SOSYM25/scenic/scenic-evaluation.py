import scenic
from datetime import datetime

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
        return len(self.unique_scenes) < self.required_unique_scenes and (datetime.now() - self.start_time).total_seconds() < self.timeout

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
        scenario = scenic.scenarioFromFile(self.scenario_file, 
                                           {'carla_map':self.map, 'intersection_uid':'intersection' + str(self.intersection)})
        self.start_time = datetime.now()
        while self.should_run():
            scene, num_iterations = scenario.generate()
            generation_time = datetime.now() - self.start_time
            self.generated_scenes.append((scene, generation_time))
            prev_size = len(self.unique_scenes)
            self.unique_scenes.add(ScenicEval.normalize_scene(scene))
            new_size = len(self.unique_scenes)
            if new_size > prev_size:
                print("+ ", generation_time, " ", num_iterations)
            else:
                print("- ", generation_time, " ", num_iterations)
        return self.generated_scenes, self.unique_scenes

base_dir = 'evaluation/SOSYM25'
scenario_file_path = base_dir + '/scenic-maneuvers{actors}.scenic'
timeout = 5

configs = [('Town04', 916, 1, 12), ('Town04', 916, 2, 56), ('Town04', 916, 3, 248), ('Town04', 916, 4, 1208), 
           ('Town05', 2240, 1, 8), ('Town05', 2240, 2, 14), ('Town05', 2240, 3, 26), ('Town05', 2240, 4, 62)]
for map, intersection, actors, required in configs:
    eval = ScenicEval(scenario_file=scenario_file_path.format(actors=actors), map=map, intersection=intersection, required_unique_scenes=required, timeout=timeout)
    scenes, unique_scenes = eval.generate()
    print("With ", actors, "actors, out of ", required, " possible unique scenes we found ", len(unique_scenes), " with a total of ", len(scenes), " scenes generated")
