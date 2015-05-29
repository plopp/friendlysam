# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)

from itertools import chain, product

import friendlysam as fs
from friendlysam.compat import ignored

class MyopicDispatchModel(fs.Part):
    """docstring for MyopicDispatchModel"""
    def __init__(self, t0=None, horizon=None, step=None, name=None):
        super().__init__(name=name)
        self.horizon = horizon
        self.step = step
        self.t = t0
    
    def state_variables(self, t):
        return tuple()

    def cost(self, t):
        return 0

    def advance(self):
        if self.horizon < self.step:
            raise RuntimeError()

        opt_times = self.times(self.t, self.horizon)

        parts = self.parts() | {self}

        problem = fs.Problem()
        problem.objective = fs.Minimize(sum(p.cost(t) for p, t in product(parts, opt_times)))
        problem.add(chain(*(p.constraints(t) for p, t in product(parts, opt_times))))

        solution = self.solver.solve(problem)

        for p, t in product(parts, self.iter_times(self.t, self.step)):
            for v in p.state_variables(t):
                v.take_value(solution)

        self.t = self.step_time(t, self.step)
