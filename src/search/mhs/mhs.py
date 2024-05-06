
from src.search.mhs.algorithm.geneticModAlgo import NSGA2MOD, GAMOD, NSGA3MOD
from src.search.mhs.termination.oneSolutionHeuristicTermination import OneSolutionHeuristicTermination
from src.search.mhs.utils import getMapBoundaries, handleConstraints, getHeuristic
import logging

from pymoo.optimize import minimize
from pymoo.core.problem import ElementwiseProblem
from pymoo.termination.collection import TerminationCollection
from pymoo.termination.max_time import TimeBasedTermination
from pymoo.algorithms.moo.nsga2 import NSGA2

from src.search.result import Result

class MHS_Approach:

    def __init__(self, args):
        self.aggregation_strategy = args.aggregation_strategy
        self.algorithm_name = args.algorithm_name
        self.restart_time = args.restart_time
        self.history = args.history
        self.timeout = args.timeout

    def getProblem(self, specification):
        actors = specification.actors
        tot_var = len(actors)*2

        # MAP BOUNDARIES
        logging.warning(f'Update the getMapBoundaries function in mhs/utils.py.')
        loBd, hiBd = getMapBoundaries(specification, len(actors))

        # HANDLE CONSTRAINT CATEGORIZATION
        logging.info(f'Improve the handleConstraints below, considering the new constraint structure. should have an AGGREGATION_STRATEGY abstrcat class object')
        con2id, exp = handleConstraints(self, specification)

        # PROBLEM
        class MyProblem(ElementwiseProblem):
            def __init__(self):
                super().__init__(n_var=tot_var, n_obj=len(exp), n_constr=0, xl=loBd, xu=hiBd)

            # Notes: x = [x_a0, y_a0, x_a1, y_a1, ...]
            def _evaluate(self, x, out, *args, **kwargs):
                heuristics = getHeuristic(specification, x, con2id, exp)
                out["F"] = heuristics
        return MyProblem(), len(exp)

    def getAlgo(self, n_objectives):
        algo_name = self.algorithm_name
        # restart_raw = restart_time
        # restart = float(restart_raw if restart_raw else -1)
        if algo_name == 'nsga2':
            algorithm = NSGA2MOD(pop_size=5, n_offsprings=None, restart_time=self.restart_time,
                            eliminate_duplicates=True)
            algorithm = NSGA2(pop_size=5, n_offsprings=20)
            # algorithm = NSGA2MOD(pop_size=5, n_offsprings=None, restart_time=self.restart_time, eliminate_duplicates=True)
        elif algo_name == 'ga':
            from pymoo.algorithms.soo.nonconvex.ga import GA
            algorithm = GAMOD(pop_size=5, n_offsprings=None, restart_time=self.restart_time,
                        eliminate_duplicates=True)
        elif algo_name == 'nsga3':
            from pymoo.util.ref_dirs import get_reference_directions
            # TODO analyse n_partitions
            ref_dirs = get_reference_directions("das-dennis", n_dim=n_objectives, n_partitions=1)
            algorithm = NSGA3MOD(ref_dirs=ref_dirs, pop_size=None, n_offsprings=None,
                                 restart_time=self.restart_time, eliminate_duplicates=True)
            # algorithm = NSGA3(ref_dirs=X, pop_size=20, n_offsprings=10)
        else:
            raise Exception(f'Evol algo <{algo_name}> is unknown.')

        return algorithm

    def getTermination(self, target_heuristic_values):
        # TODO
        t1 = OneSolutionHeuristicTermination(heu_vals=target_heuristic_values)
        # TEMP
        # t1 = MultiObjectiveSpaceToleranceTermination(tol=0.0025, n_last=30)	
        # t1 = ConstraintViolationToleranceTermination(n_last=20, tol=1e-6,)	
        # t1 = IGDTermination	
        t2 = TimeBasedTermination(max_time=self.timeout)

        return TerminationCollection(t1, t2)

    def concretize(self, specification):
        # GET PROBLEM
        # TODO remove the num_objectives once the AGREATION_STRATEGY abstract class is created
        
        problem, num_objectives = self.getProblem(specification)

        # GET ALGORITHM
        algorithm = self.getAlgo(num_objectives)

        # GET TERMINATION
        target_heuristic_values = [0 for _ in range(num_objectives)]
        termination = self.getTermination(target_heuristic_values)

        # RUN PROBLEM
        # (For Repeatability) use seed=1 option
        verbose_pymoo = logging.getLogger().getEffectiveLevel() <= logging.WARNING
        mhs_res = minimize(problem, algorithm, termination, save_history=self.history, verbose=verbose_pymoo)

        # CREATE RESULT OBJECT
        # Important Note: mhs_res only contains NDSs, so it is always <=, often <,  pop_size
        res = Result(mhs_res, specification)
        res.update_from_mhs()
        return res