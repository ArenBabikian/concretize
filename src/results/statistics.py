import json
import logging
from pathlib import Path

class Statistics_Manager:

    def __init__(self, args, specification):
        global_stats = {}
        global_stats['map'] = args.map
        global_stats['num_actors'] = len(specification.actors)
        global_stats['approach'] = args.approach
        global_stats['input_file_path'] = args.specification
        global_stats['runs'] = {}
        self.global_stats = global_stats

        self.stor_all_outcomes = args.store_all_outcomes
        self.json_path = Path(args.output_directory) / args.save_statistics_file

    def generate_stats(self, res):
        res.update_stats_map(self.stor_all_outcomes)

    def update(self, run_id, run_res):
        self.global_stats['runs'][run_id] = run_res

    def save(self):
        logging.debug(json.dumps(self.global_stats, indent=2))
        if self.json_path:
            with open(self.json_path, 'w') as f:
                json.dump(self.global_stats, f, indent=2)
            logging.info(f"Updated outcome statistics to {self.json_path}")   

    def generate_update_save(self, run_id, run_res):
        self.generate_stats(run_res)
        self.update(run_id, run_res.stats_map)
        self.save()
