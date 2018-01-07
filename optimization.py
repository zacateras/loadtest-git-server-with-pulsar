import random
import math
import pandas as pd
from app_log_dumper import ensure_file_not_exist


class OptimizationLog:
    def __init__(self, *args, log_name="./optimization.log"):
        self.log_file_name = ensure_file_not_exist(log_name)
        self._df = pd.DataFrame(columns=args)

    def flush(self):
        self._df.to_csv(self.log_file_name)

    def log(self, *args):
        df = self._df
        df.loc[len(df)] = args
        if len(df) % 10 == 0:
            self.flush()


class Annealing:
    class FirstIteration(IndexError):
        pass

    def __init__(self, result_logs, variables_names, initial_values, deltas, boundaries):
        self._result_logs = result_logs
        self._variables_names = variables_names
        self.current_values = None
        self._initial_values = initial_values
        self._deltas = deltas
        self._boundaries = boundaries
        self._t = 0
        self._values_generator = self._algoritm_iterator()
        self._logger = OptimizationLog("t", "T", "dE", "obj_f_value", "moved", *self._variables_names)

    def _get_total_duration(self):
        try:
            last_result = self._result_logs[-1]
        except IndexError as err:
            raise Annealing.FirstIteration from err
        total_duration = 0
        for event in last_result["cycle_result"]:
            total_duration += event.command_duration
        return total_duration

    def _goal_reached(self):
        return False

    def _T(self):
        mu = 0.0
        sig = 40.0
        max_T = 0.5
        return math.exp(-(self._t - mu)**2. / (2 * sig**2.)) * max_T

    def _random_assignment(self, dE):
        return random.random() < math.exp(dE/self._T())

    def _log(self, t, T, dE, objective_f, moved):
        pass

    def _algoritm_iterator(self):
        self.current_values = self._initial_values
        yield {name: value for name, value in zip(self._variables_names, self._initial_values)}
        current_objective_function_value = self._get_total_duration()

        while not self._goal_reached():

            next_values = [value + random.randint(-1, 1) * delta
                           for value, delta in zip(self.current_values, self._deltas)]
            for i, (value, (lower_bound, upper_bound)) in enumerate(zip(next_values, self._boundaries)):
                if lower_bound is not None and value < lower_bound:
                    next_values[i] = lower_bound
                if upper_bound is not None and value > upper_bound:
                    next_values[i] = upper_bound

            yield {name: value for name, value in zip(self._variables_names, next_values)}
            new_objective_function_value = self._get_total_duration()
            dE = (new_objective_function_value - current_objective_function_value) * \
                 2 / (new_objective_function_value + current_objective_function_value)
            moved = False
            if dE > 0 or self._random_assignment(dE):
                current_objective_function_value = new_objective_function_value
                self.current_values = next_values
                moved = True
            self._logger.log(self._t, self._T(), dE, current_objective_function_value, moved, *self.current_values)
            self._t += 1
        self._logger.flush()

    def get_optimal_parameters(self):
        return next(self._values_generator)
