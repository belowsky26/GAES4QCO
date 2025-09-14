import random
from typing import List, Tuple
from copy import deepcopy
from .interfaces import IPopulationCrossover, ICrossoverStrategy
from .population import Population
from quantum_circuit.circuit import Circuit, Column


class PopulationCrossover(IPopulationCrossover):
    def __init__(self, crossover_strategy: ICrossoverStrategy, crossover_rate: float = 0.8):
        self.crossover_strategy = crossover_strategy
        self.crossover_rate = crossover_rate

    def run(self, parent_population: Population) -> Population:
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
                child1, child2 = self.crossover_strategy.crossover(parent1, parent2)
                offspring.extend([child1, child2])

        return Population(offspring)


class MultiPointCrossover(ICrossoverStrategy):
    def crossover(self, parent_1: Circuit, parent_2: Circuit) -> Tuple[Circuit, Circuit]:
        min_depth = min(parent_1.depth, parent_2.depth)
        crossover_points = [random.choice([0, 1]) for _ in range(min_depth)]
        child1_cols, child2_cols = [], []

        for i in range(min_depth):
            if crossover_points[i] == 0:
                child1_cols.append(deepcopy(parent_1.columns[i]))
                child2_cols.append(deepcopy(parent_2.columns[i]))
            else:
                child1_cols.append(deepcopy(parent_2.columns[i]))
                child2_cols.append(deepcopy(parent_1.columns[i]))

        if parent_1.depth > min_depth:
            child1_cols.extend(deepcopy(parent_1.columns[min_depth:]))
        elif parent_2.depth > min_depth:
            child2_cols.extend(deepcopy(parent_2.columns[min_depth:]))
        num_qubits = parent_1.count_qubits
        child1 = Circuit(num_qubits, child1_cols)
        child2 = Circuit(num_qubits, child2_cols)
        return child1, child2


class BlockwiseCrossover(ICrossoverStrategy):
    """
    Crossover 2D que divide os pais por uma coluna e um qubit.
    Pode quebrar e reconstruir gates, introduzindo nova informação genética.
    """

    def crossover(self, parent_1: Circuit, parent_2: Circuit) -> Tuple[Circuit, Circuit]:
        num_qubits = max(parent_1.count_qubits, parent_2.count_qubits)
        max_depth = max(parent_1.depth, parent_2.depth)

        # 1. Escolhe os pontos de divisão 2D
        split_col = random.randint(0, max_depth)
        split_qubit = random.randint(0, num_qubits - 1)

        # 2. Constrói os filhos combinando os "blocos"
        child1 = self._build_child(parent_1, parent_2, split_col, split_qubit, num_qubits)
        child2 = self._build_child(parent_2, parent_1, split_col, split_qubit, num_qubits)

        return child1, child2

    def _build_child(self, p1: Circuit, p2: Circuit, split_c: int, split_q: int, num_qubits: int) -> Circuit:
        child_cols = []
        max_depth = max(p1.depth, p2.depth)

        for i in range(max_depth):
            new_col_gates = []

            # Pega gates da coluna i do pai 1 que atuam nos qubits <= split_q
            if i < p1.depth:
                for gate in p1.columns[i].get_gates():
                    if all(q <= split_q for q in gate.qubits):
                        new_col_gates.append(deepcopy(gate))

            # Pega gates da coluna i do pai 2 que atuam nos qubits > split_q
            if i < p2.depth:
                for gate in p2.columns[i].get_gates():
                    if all(q > split_q for q in gate.qubits):
                        new_col_gates.append(deepcopy(gate))

            # NOTA: A "reconstrução" de gates quebrados mencionada no artigo
            # é implicitamente tratada aqui. Ao pegar apenas os gates que se
            # encaixam inteiramente em uma das partições (acima ou abaixo do split_qubit),
            # nós efetivamente "destruímos" os gates que cruzam a fronteira.
            # O algoritmo então confia nos operadores de mutação (como a RepairMutation)
            # para preencher os "buracos" criados, introduzindo nova informação.

            child_cols.append(Column(new_col_gates))

        return Circuit(num_qubits, child_cols)


class SinglePointCrossover(ICrossoverStrategy):
    """
    Crossover de Ponto Único.
    Sorteia uma única coluna para ser o ponto de troca de material genético.
    """

    def crossover(self, parent_1: Circuit, parent_2: Circuit) -> Tuple[Circuit, Circuit]:
        min_depth = min(parent_1.depth, parent_2.depth)
        if min_depth == 1:
            return deepcopy(parent_1), deepcopy(parent_2)

        crossover_point = random.randint(1, min_depth - 1)

        # Cria os filhos trocando as colunas a partir do ponto de crossover
        child1_cols = deepcopy(parent_1.columns[:crossover_point]) + deepcopy(parent_2.columns[crossover_point:])
        child2_cols = deepcopy(parent_2.columns[:crossover_point]) + deepcopy(parent_1.columns[crossover_point:])

        num_qubits = max(parent_1.count_qubits, parent_2.count_qubits)
        child1 = Circuit(num_qubits, child1_cols)
        child2 = Circuit(num_qubits, child2_cols)
        return child1, child2

