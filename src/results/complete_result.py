

from src.model.specification import Specification_Instance
from src.results.result import Result
from src.search.complete import utils


class Complete_Result(Result):

    def __init__(self, approach, specification):
        super().__init__(approach, specification)

    def extend_stats_map(self, _):
        self.stats_map['junction'] = str(self.raw_res.junction)
        self.stats_map['log_theory'] = self.raw_res.junction.theoretical_n_scenarios
        self.stats_map['log_evaluated'] = self.raw_res.num_evaluated_logical_solutions
        self.stats_map['log_colliding'] = self.raw_res.num_colliding_logical_solutions
        self.stats_map['con_no_init_overlap'] = self.raw_res.num_no_init_overlap_concrete_solutions
        self.stats_map['con_valid'] = self.raw_res.num_valid_concrete_solutions

        all_outcome_data = {}
        for i, outcome in enumerate(self.all_solutions):
            # outcome is a Specification_Instance
            outcome_id = 'outcome_' + str(i)
            outcome_data = {}
            outcome_data['is_concrete_solution'] = outcome.is_concrete_solution

            man_ass = {str(actor): None if actor.position is None else actor.assigned_maneuver_instance.connectingLane.id for actor in outcome.actors}
            outcome_data['maneuver_assignment'] = man_ass

            all_outcome_data[outcome_id] = outcome_data

        self.stats_map['outcomes'] = all_outcome_data

    def update(self, specification=None):
        if specification:
            self.specification = specification
        # `complete` mode only returns a single `Result` object at a time since it only makes one (deterministic) run

        instance = Specification_Instance(self.specification)
        utils.fill_logical_actors(instance)

        self.all_solutions.append(instance)
        self.ordered_outcomes.append(instance)
