import json
import logging

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
        self.json_path = args.save_path_statistics

    def generate_stats(self, res):
        data = {}
        data['success'] = res.success
        data['n_solutions'] = res.n_solutions
        data['runtime'] = res.runtime
        data['n_iterations'] = res.n_iterations
        n_constraints = len(res.specification.constraints)
        data['n_constraints'] = n_constraints
        # data['restarts'] = res.restarts # TODO

        all_outcome_data = {}
        for i, outcome in enumerate(res.ordered_outcomes):
            if i>0 and not self.stor_all_outcomes:
                break
            outcome_id = 'outcome_' + str(i)
            outcome_data = {}

            n_satisfactions = n_constraints - outcome.n_violations
            outcome_data['n_satisfactions'] = n_satisfactions
            outcome_data['p_satisfactions'] = -1 if n_constraints == 0 else n_satisfactions/n_constraints
            outcome_data['heuristics'] = {str(k):v for k, v in outcome.constraint2heuristic.items()}
            outcome_data['raw_positions'] = outcome.raw_res
            # TODO missing some hard/soft constraint analysis here. Probably unnecessary
            all_outcome_data[outcome_id] = outcome_data

        data['outcomes'] = all_outcome_data
        # TODO add history data analysis (see scenic>scenarios.py:L537-608)
        return data

    def update(self, run_id, run_res):
        self.global_stats['runs'][run_id] = run_res

    def save(self):
        logging.debug(json.dumps(self.global_stats, indent=2))
        if self.json_path:
            with open(self.json_path, 'w') as f:
                json.dump(self.global_stats, f, indent=2)
            logging.info(f"Saved outcome statistics to {self.json_path}")   

    def generate_update_save(self, run_id, run_res):
        one_run_data = self.generate_stats(run_res)
        self.update(run_id, one_run_data)
        self.save()
