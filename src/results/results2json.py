import json
import logging

def generate_json(res, store_all_solutions, file_path=None):

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
        if i>0 and not store_all_solutions:
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

    if file_path:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        logging.info(f"Saved outcome statistics to {file_path}")   

    return data
