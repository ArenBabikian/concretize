import scenic
from datetime import datetime

class ScenicEval():
    
    def __init__(self, scenario_file, size, required_unique_scenes, timeout):
        self.scenario_file = scenario_file
        self.size = size
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
        scenario = scenic.scenarioFromFile(self.scenario_file)
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
scenario_file_path = '{basedir}/scenic-maneuvers{actors}.scenic'
timeout = 20

sizes = [(1, 12), (2, 56), (3, 248), (4, 1208)]
for size, required in sizes:
    eval = ScenicEval(scenario_file=scenario_file_path.format(basedir=base_dir, actors=size), size=size, required_unique_scenes=required, timeout=timeout)
    scenes, unique_scenes = eval.generate()
    print("With ", size, "actors, out of ", required, " possible unique scenes we found ", len(unique_scenes), " with a total of ", len(scenes), " scenes generated")
