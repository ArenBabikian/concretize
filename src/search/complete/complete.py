
import logging
from src.model.constraints.behavior_constraints import Behavior_Con, Does_Maneuver_Con
from src.model.constraints.danger_constraints import Danger_Con
from src.model.junction import Junction
from src.model.constraints.constraint import Static_Con
from src.results.complete_result import Complete_Result
from src.results.result import Result
from src.search.search_approach import Search_Approach
import src.search.complete.constants as cst
import src.search.complete.utils as utils
import src.search.complete.utils_concrete as utils_con

class Complete_Approach(Search_Approach):

    def __init__(self, args, specification):
        j = Junction(args.junction, specification)
        self.junction = j
        specification.junction = j
        self.junction.log_stats()

        self.actor_to_lane_instances = {ac:[] for ac in specification.actors}
        self.danger_conditions = []

        self.num_evaluated_logical_solutions = 0
        self.num_colliding_logical_solutions = 0
        self.num_no_init_overlap_concrete_solutions = 0
        self.num_valid_concrete_solutions = 0
        super().__init__(args, specification)

        self.all_solutions.append(Complete_Result(self, specification)) # only a single solution is returned for the complete mode. It s asingle (deterministic) run of the algorithm.

    def validate_input_specification(self):
        actors = self.specification.actors
        if len([a for a in actors if a.isEgo]) != 1:
            raise Exception("The scenario must contain exactly one ego actor.")

        actors_w_behavior = set()
        constraints = self.specification.constraints
        for con in constraints:
            if not isinstance(con, Behavior_Con) and not isinstance(con, Danger_Con):
                raise Exception(f"Invalid constraint type {con}. Only behavior constraints or danger constraints are allowed when using the complete mode.")
            else:
                actors_w_behavior.add(con.actors[0])

        diff = set(actors).difference(actors_w_behavior)
        if diff:
            raise Exception(f"Every actor must be assigned a behavior. {diff} {'is' if len(diff) == 1 else 'are'} not assigned a behavior.")

    # TODO refactor this w/ the autopilot approach
    def handle_constraints(self, specification):
        danger_constraints = []
        for con in specification.constraints:
            if isinstance(con, Does_Maneuver_Con):
                all_allowed_maneuver_instances = con.get_all_allowed_maneuver_instances(self.junction)
                self.actor_to_lane_instances[con.actors[0]] = all_allowed_maneuver_instances
            elif isinstance(con, Danger_Con):
                danger_constraints.append(con)
        return danger_constraints        

    def get_dangerous_logical_scenarios(self):
        actors = self.specification.actors
        ego_actor = actors[self.specification.ego_id]
        actors_with_ego_first = [ego_actor] + [actor for actor in actors if actor != ego_actor]
        global_depth = len(actors)

        def recursiveForLoop(depth):

            if depth <= global_depth-1:
                actor = actors_with_ego_first[depth]
                for maneuver_id, man in enumerate(self.actor_to_lane_instances[actor]):

                    # we enter these conditions if ego is already assigned a maneuver
                    ego_man = ego_actor.assigned_maneuver_instance
                    assert depth == 0 or ego_man is not None
                    if depth > 0 and man.connectingLane == ego_man.connectingLane:
                        # CONSTRAINT 1: Non-ego paths must be different than ego path
                        continue
                    if depth > 0 and man.startLane == ego_man.startLane:
                        # CONSTRAINT 2: Non-ego paths must have different starting lane than ego path
                        continue
                    if depth > 1 and actors_with_ego_first[depth-1].assigned_maneuver_instance == man:
                        # CONSTRAINT 3: All non-ego paths must be distinct
                        continue 
                    # TODO below IMPORTANT
                    # if depth > 1 and tuple[-1][1] > maneuver_id:
                    #     # CONSTRAINT 4: No permutations among all non-ego paths
                    #     continue 

                    actor.assigned_maneuver_instance = man
                    recursiveForLoop(depth+1)
                    actor.assigned_maneuver_instance = None
            else:
                # Check if ego road is intersecting with ALL non-ego roads
                num_violated_danger_conditions = 0
                for danger_con in self.danger_conditions:
                    _, is_violated = danger_con.evaluate_logical_condition()
                    num_violated_danger_conditions += is_violated

                if num_violated_danger_conditions == 0:
                    # TODO Soolution found. save it as a Result
                    self.num_colliding_logical_solutions += 1
                    self.all_solutions[0].update(self.specification)
                    # pass
                self.num_evaluated_logical_solutions += 1

        recursiveForLoop(0)
        logging.info(f'We evaluate {self.num_evaluated_logical_solutions} {global_depth}-lane combinations. {self.num_colliding_logical_solutions} of them are colliding at the logical level.')

    def get_dangerous_concrete_scenarios(self):
        # Scenarios are included in aelf.all_solutions[0].all_solutions
        scenario_instances = self.all_solutions[0].all_solutions

        for i_sc, scenario in enumerate(scenario_instances):
            # 1. get logical params of ego
            ego_actor = scenario.actors[scenario.specification.ego_id]
            utils.validate_speed_profiles(ego_actor)
            ego_man = ego_actor.assigned_maneuver_instance
            ego_man_reg = ego_man.connectingLane

            # 2. get starting position of ego (5m before the junction)
            ego_start_reg = ego_man_reg._predecessor.sections[-1]
            ego_start_cl = ego_start_reg.centerline
            ego_start_point = ego_start_cl.pointAlongBy(-cst.EGO_DIST_BEFORE_JUNC)

            # 3. Set up ego actor
            utils.fill_concrete_actors(ego_actor, ego_start_point, ego_start_reg)

            # 4. Get collisions in order
            collision_constraints = self.handle_constraints(scenario)
            collisions_in_order = utils_con.get_collisions_in_order(collision_constraints)
            # ranked_non_ego_by_dist_for_ego = []

            # 5. Determine how much time to add to ensure collision must happen
            # ...and that non-egos wont collide with each other, at least not  on the path of ego
            for i_cur, cur_coll_stats in enumerate(collisions_in_order):
                if i_cur == 0:
                    # no time to add for the first collision.
                    continue

                i_prev = i_cur-1
                prev_coll_stats = collisions_in_order[i_prev]
                prev_time_to_add = prev_coll_stats['time_to_add']

                time_to_add_to_non_ego = utils_con.calculate_time_for_man(prev_coll_stats)
                new_time_to_add = prev_time_to_add + time_to_add_to_non_ego
                cur_coll_stats['time_to_add'] = new_time_to_add

            # 6. Determins how much time to add to the ego timeout measurement
            ego_time_to_add = 0
            if len(collisions_in_order) >= 1:
                stats_last = collisions_in_order[-1]
                last_time_to_add = stats_last['time_to_add']

                time_to_add_for_last_man = utils_con.calculate_time_for_man(stats_last)
                ego_time_to_add = last_time_to_add + time_to_add_for_last_man

            # 7. Handle non-ego actors
            utils_con.setup_other_actors(collision_constraints, collisions_in_order, self.junction.junction_in_network)

            # 8. If some actors are not assigned an exact path, we position them right outside the junction
            for actor in scenario.actors:
                if actor.assign_exact_path_for_vis is None:
                    ac_man_reg = actor.assigned_maneuver_instance.connectingLane
                    ac_start_reg = ac_man_reg._predecessor.sections[-1]
                    ac_start_cl = ac_start_reg.centerline
                    ac_start_point = ac_start_cl.pointAlongBy(-cst.EGO_DIST_BEFORE_JUNC)

                    utils.fill_concrete_actors(actor, ac_start_point, ac_start_reg)
            
            # 9. Validate the concrete scene
            num_problems = {'init_overlap': 0}
            for a1_i, a1 in enumerate(scenario.actors):
                for a2 in scenario.actors[a1_i+1:]:
            # for c in collision_constraints:
            #     ego_actor, other_actor = utils_con.detect_ego_and_other_actors(c, False)
            #     if ego_actor is None:
            #         continue

                    # VALIDATION 1 : non-egos should initially not overlap
                    if a1.overlaps_with(a2):
                        num_problems['init_overlap'] += 1
                        logging.info(f'WARNING: SCENARIO {i_sc} VOIDED, {a1} and {a2} have initially overlapping positions.')

                    # VALIDATION 2 : are non-ego paths overlapping?
                    # TODO: implement this validation?
                    # if i_ac != 0:
                    #     # avoid checking thiss for ego
                    #     i_reg = colliding_tuple[i_ac].connectingLane
                    #     j_reg = colliding_tuple[j_ac].connectingLane
                    #     ij_coll_reg, _ = find_colliding_region(i_reg, j_reg, handle_centerlines=True)
                    #     # if ij_coll_reg != EmptyRegion(''):
                    #     #     print(f'WARNING: For Scenario {i_sc}, actors {i_ac} and {j_ac} have overlapping paths.')
                    # else:
                    #     self.num_no_non_ego_coll_concrete_solutions += 1
            
            # 10. confirm validity of the scenario instance
            if num_problems['init_overlap'] == 0:
                self.num_no_init_overlap_concrete_solutions += 1
                
                # TODO : extend later with further validation
                self.num_valid_concrete_solutions += 1
                scenario.is_concrete_solution = True

            # 11. measure the timeout of the cenario
            timeout = utils_con.calculate_timeout(ego_actor, ego_man_reg, ego_time_to_add)
            scenario.measured_timeout = timeout

        logging.info(f'From these {self.num_colliding_logical_solutions} colliding tuples, {self.num_valid_concrete_solutions} of them are valid at the concrete level (i.e. they do not have initial-position overlaps).')

    def concretize(self):

        # GET MAPPING OF ACTOR TO ALL POSSIBLE LANE REGIONS
        # CREATE A DANGER CONDITION by looking at the potential collision consraints
        danger_constraints = self.handle_constraints(self.specification)
        self.danger_conditions = danger_constraints

        # GET ALL DANGEROUS LOGICAL SCENARIOS
        # Scenarios are included in aelf.all_solutions[0].all_solutions
        self.get_dangerous_logical_scenarios()

        # TODO once all logical scenarios are found, only keep num_required_solution of them

        # GET ALL DANGEROUS CONCRETE SCENARIOS
        self.get_dangerous_concrete_scenarios()

        # SAVE EXECUTABLE XML FILES

        # TODO go back to `initializeAbstractScenarioDetails` from scenic, l63, for the analysis at the end
