import logging
from src.search.mhs.termination.single_element_termination import SingleElementTermination
from pymoo.termination.collection import TerminationCollection
from src.specification import Specification_Instance
from src.search.mhs import utils
import pymoo.core.result

class Result:

    def __init__(self, raw_result, specification):
        self.raw_res = raw_result
        self.specification = specification

        self.runtime = None
        self.n_iterations = None
        self.n_solutions = None
        self.success = None
        self.all_solutions = None
        self.ordered_outcomes = None

    def update_from_mhs(self):
        # basic info
        self.runtime = self.raw_res.exec_time
        self.n_iterations = self.raw_res.algorithm.n_gen

        # Check which population members are solutions
        # TODO handle different number of solutions (see scenic>scenarios.py:L280-343)
        mhs_pop = self.raw_res.X
        mhs_fitness = self.raw_res.F

        all_solutions = []
        elements_ordered_by_n_violations = []
        for i, i_values in enumerate(mhs_pop):
            i_fitness = mhs_fitness[i]

            # 1 Create instance
            i_instance = Specification_Instance(self.specification)
            i_instance.raw_res = list(i_values)
            utils.fillInstance(i_instance, i_values)
            
            # TODO add history saving (see scenic>scenarios.py:L369-391)

            # 2 Check if it is a valid solution (wrt. termination criteria)
            # TODO Important, maybe this kind of element-level validity check analysis
            # is not unique to MHS (ex. case of re-evaluating for Scenic sampling-based).
            # Think about this
            i_is_valid = self.check_element_validity_from_fitness(i_fitness)
            if i_is_valid:
                all_solutions.append(i_instance)

            # 3 Check the validity of each input consraints
            n_violations = self.analyse_data_and_fill_element(i_instance)
            elements_ordered_by_n_violations.append((n_violations, i_instance))
            # constraints = self.specification.constraints
            
        # Sort solutions in increasing order of constraint violations
        elements_ordered_by_n_violations.sort(key=lambda x: x[0])

        # Saving general data
        self.n_solutions = len(all_solutions)
        self.success = self.n_solutions > 0

        # MHS-specific data
        # self.restarts = None # TODO
        self.all_solutions = all_solutions
        self.ordered_outcomes = [x[1] for x in elements_ordered_by_n_violations]

    def check_element_validity_from_fitness(self, fitness):
        termination = self.raw_res.algorithm.termination
        if isinstance(termination, SingleElementTermination):
            return termination.single_element_validity(fitness)
        elif(isinstance(termination, TerminationCollection)):
            for term in termination.terminations:
                if isinstance(term, SingleElementTermination):
                    return term.single_element_validity(fitness)

    def analyse_data_and_fill_element(self, element):
        num_violations = 0
        constraint2heuristic = {}
        for constraint in self.specification.constraints:
            heuristic_value = constraint.get_heuristic_value()
            if heuristic_value != 0:
                # constraint is violated
                num_violations += 1
            constraint2heuristic[constraint] = heuristic_value

        # Store the run info in the element itself
        element.n_violations = num_violations
        element.constraint2heuristic = constraint2heuristic
        return num_violations
