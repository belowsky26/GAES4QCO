import random
from typing import List
from copy import deepcopy
from .interfaces import ICrossoverStrategy
from .population import Population
from quantum_circuit.circuit import Circuit, Column


class UniformCrossover(ICrossoverStrategy):
    def __init__(self, crossover_rate: float = 0.8):
        self.crossover_rate = crossover_rate

    def crossover(self, parent_population: Population) -> Population:
        # 1. Extrai a lista de indivíduos do objeto Population.
        parents_local = parent_population.get_individuals()
        random.shuffle(parents_local)
        offspring = []

        for i in range(0, len(parents_local), 2):
            if i + 1 >= len(parents_local):
                offspring.append(parents_local[i])
                continue

            parent1, parent2 = parents_local[i], parents_local[i + 1]

            if random.random() < self.crossover_rate:
                child1_cols, child2_cols = self._perform_crossover(parent1, parent2)

                num_qubits = max(parent1.count_qubits, parent2.count_qubits)
                child1 = Circuit(num_qubits, child1_cols)
                child2 = Circuit(num_qubits, child2_cols)

                offspring.extend([child1, child2])

        return Population(offspring)

    def _perform_crossover(self, p1: Circuit, p2: Circuit) -> tuple[List[Column], List[Column]]:
        min_depth = min(p1.depth, p2.depth)
        crossover_points = [random.choice([0, 1]) for _ in range(min_depth)]
        child1_cols, child2_cols = [], []

        for i in range(min_depth):
            if crossover_points[i] == 0:
                child1_cols.append(deepcopy(p1.columns[i]))
                child2_cols.append(deepcopy(p2.columns[i]))
            else:
                child1_cols.append(deepcopy(p2.columns[i]))
                child2_cols.append(deepcopy(p1.columns[i]))

        if p1.depth > min_depth:
            child1_cols.extend(deepcopy(p1.columns[min_depth:]))
        elif p2.depth > min_depth:
            child2_cols.extend(deepcopy(p2.columns[min_depth:]))

        return child1_cols, child2_cols
