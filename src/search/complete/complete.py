
import logging
from src.model.constraints.behavior_constraints import Behavior_Con, Does_Maneuver_Con
from src.model.constraints.danger_constraints import Danger_Con
from src.model.constraints.junction import Junction
from src.model.constraints.static_constraints import Static_Con
from src.results.complete_result import Complete_Result
from src.results.result import Result
from src.search.search_approach import Search_Approach

class Complete_Approach(Search_Approach):

    def __init__(self, args, specification):
        j = Junction(args.junction, specification)
        self.junction = j
        specification.junction = j
        self.junction.log_stats()

        self.actor_to_lane_instances = {}
        self.danger_conditions = []

        self.num_evaluated_logical_solutions = 0
        self.num_colliding_solutions = 0
        super().__init__(args, specification)

        self.all_solutions.append(Complete_Result(self, specification)) # only a single solution is returned for the complete mode. It s asingle (deterministic) run of the algorithm.

    def validate_input_specification(self):
        constraints = self.specification.constraints
        for con in constraints:
            if not isinstance(con, Behavior_Con) and not isinstance(con, Danger_Con):
                logging.error("Invalid constraint type. Only behavior constraints or danger constraints are allowed when using the complete mode.")
                exit(1)

    def handle_constraints(self):
        for con in self.specification.constraints:
            if isinstance(con, Does_Maneuver_Con):
                all_allowed_maneuver_instances = con.get_all_allowed_maneuver_instances(self.junction)
                self.actor_to_lane_instances[con.actors[0]] = all_allowed_maneuver_instances
            elif isinstance(con, Danger_Con):
                self.danger_conditions.append(con)

    def get_dangerous_logical_scenarios(self):
        actors = self.specification.actors
        global_depth = len(actors)

        def recursiveForLoop(depth, tuple):

            if depth <= global_depth-1:
                actor = actors[depth]
                for maneuver_id, man in enumerate(self.actor_to_lane_instances[actor]):

                    # TODO Make decisions here. Remove 'tuple'

                    if depth >= 1 and man.connectingLane == actors[depth-1].assigned_maneuver_instance.connectingLane:
                        # CONSTRAINT 1: Non-ego paths must be different than ego path
                        continue
                    # if len(tuple) > 0 and man.startLane == tuple[0][0].startLane:
                    #     # CONSTRAINT 2: Non-ego paths must have different starting lane than ego path
                    #     continue
                    # if len(tuple) > 1 and tuple[-1][1] == maneuver_id:
                    #     # CONSTRAINT 3: All non-ego paths must be distinct
                    #     continue 
                    # if len(tuple) > 1 and tuple[-1][1] > maneuver_id:
                    #     # CONSTRAINT 4: No permutations among all non-ego paths
                    #     continue 

                    actor.assigned_maneuver_instance = man
                    recursiveForLoop(depth+1, tuple)
                    actor.assigned_maneuver_instance = None
            else:
                # Check if ego road is intersecting with ALL non-ego roads
                num_violated_danger_conditions = 0
                for danger_con in self.danger_conditions:
                    _, is_violated = danger_con.evaluate_danger_condition()
                    num_violated_danger_conditions += is_violated

                if num_violated_danger_conditions == 0:
                    # TODO Soolution found. save it as a Result
                    self.num_colliding_solutions += 1
                    self.all_solutions[0].update(self.specification)
                    # pass
                self.num_evaluated_logical_solutions += 1

        recursiveForLoop(0, [])

        logging.info(f'We evaluate {self.num_evaluated_logical_solutions} {global_depth}-tuples. {self.num_colliding_solutions} of them are colliding.')

    def concretize(self):

        # GET MAPPING OF ACTOR TO ALL POSSIBLE LANE REGIONS
        # CREATE A DANGER CONDITION by looking at the potential collision consraints
        self.handle_constraints()

        # GET ALL DANGEROUS LOGICAL SCENARIOS
        self.get_dangerous_logical_scenarios()

        # define the recursive function
            # ensure that only valid lane regions are considered for each actor
            # ensure the handling of danger conditions
            # ensure that the acceptance constraints are not too restrictive (e.g. wrt different speed and acceleration profiles)
        
        # once all logical scenarios are found, only keep num_required_solution of them

        # rule-based aproach to derive concrete scenarios
            # again, avoid too restrictive constraints

        # return the set of solutions as a set of Result objects.
        # we probably need to add a 'assigned_path', 'assigned_lane_region' attributes to the actors


        # VISUALIZATION: implement a visualization of the generated exact paths and a highlighting of the lane regions.
            # for suyre already done in scenic, but also need CLI args for this

        # TODO go back to `initializeAbstractScenarioDetails` from scenic, l63



        # return super().concretize(specification)