"""Optimization pipeline for Sprint 7.

Order: constant folding -> constant propagation -> folding again -> dead code
elimination.  The pipeline iterates until statistics stop changing or the
iteration limit is reached.
"""

from .constant_folding import ConstantFolding
from .constant_propagation import ConstantPropagation
from .dead_code import DeadCodeElimination


class OptimizationPipeline:
    def __init__(self, max_iterations: int = 4):
        self.max_iterations = max_iterations
        self.stats = {
            'constant_folding': 0,
            'constant_propagation': 0,
            'dead_code_removed': 0,
            'iterations': 0,
        }

    def optimize(self, program):
        for _ in range(self.max_iterations):
            before = dict(self.stats)

            folding = ConstantFolding()
            folding.optimize(program)
            self._merge(folding.get_stats())

            propagation = ConstantPropagation()
            propagation.optimize(program)
            self._merge(propagation.get_stats())

            folding2 = ConstantFolding()
            folding2.optimize(program)
            self._merge(folding2.get_stats())

            dce = DeadCodeElimination()
            dce.optimize(program)
            self._merge(dce.get_stats())

            self.stats['iterations'] += 1
            if all(self.stats[k] == before.get(k, 0) for k in ('constant_folding', 'constant_propagation', 'dead_code_removed')):
                break
        return program

    def _merge(self, new_stats):
        for k, v in new_stats.items():
            self.stats[k] = self.stats.get(k, 0) + v

    def get_stats(self):
        return dict(self.stats)
