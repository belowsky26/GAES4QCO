from itertools import combinations
from typing import List, Iterator
from quantum_circuit.circuit import Circuit


class Population:
    """
    Encapsula uma coleção de indivíduos (Circuitos) e fornece
    operações úteis sobre o conjunto.
    """
    def __init__(self, individuals: List[Circuit] = None):
        self._individuals = individuals if individuals is not None else []

    def add_individual(self, individual: Circuit):
        """Adiciona um indivíduo à população."""
        self._individuals.append(individual)

    def get_fittest(self) -> Circuit:
        """Encontra e retorna o indivíduo com o maior fitness."""
        if not self._individuals:
            raise ValueError("A população está vazia, não é possível encontrar o mais apto.")
        return max(self._individuals, key=lambda ind: ind.fitness)

    def get_individuals(self) -> List[Circuit]:
        """Retorna a lista de todos os indivíduos."""
        return self._individuals

    @property
    def average_fitness(self) -> float:
        """Calcula e retorna a média do fitness da população."""
        if not self._individuals:
            return 0.0
        total_fitness = sum(ind.fitness for ind in self._individuals)
        return total_fitness / len(self._individuals)

    def calculate_structural_diversity(self) -> float:
        """
        Calcula a diversidade estrutural média da população.
        Usa a distância de Jaccard, que mede a dissimilaridade entre conjuntos.
        O valor varia de 0 (todos os indivíduos são clones) a 1 (todos são completamente diferentes).
        """
        if len(self._individuals) < 2:
            return 0.0

        total_distance = 0.0
        # Cria todas as combinações de pares únicos de indivíduos
        pairs = list(combinations(self._individuals, 2))

        for ind1, ind2 in pairs:
            # Pega a "impressão digital" de cada circuito
            set1 = ind1.get_structural_representation()
            set2 = ind2.get_structural_representation()

            # Calcula a distância de Jaccard: 1 - (tamanho da interseção / tamanho da união)
            intersection_size = len(set1.intersection(set2))
            union_size = len(set1.union(set2))

            if union_size == 0:
                distance = 0.0
            else:
                jaccard_similarity = intersection_size / union_size
                distance = 1.0 - jaccard_similarity

            total_distance += distance

        # Retorna a média da distância entre todos os pares
        return total_distance / len(pairs)

    def remove_duplicates(self):
        """
        Verifica e remove circuitos duplicados da população com base em sua
        assinatura genética (estrutura e parâmetros).
        """
        if not self._individuals:
            return

        seen_signatures = set()
        unique_individuals = []
        for individual in self._individuals:
            signature = tuple(individual.get_structural_representation())
            if signature not in seen_signatures:
                seen_signatures.add(signature)
                unique_individuals.append(individual)

        self._individuals = unique_individuals

    def __len__(self) -> int:
        """Permite o uso de len(population_object)."""
        return len(self._individuals)

    def __iter__(self) -> Iterator[Circuit]:
        """Permite iterar sobre os indivíduos: for circuit in population_object:"""
        return iter(self._individuals)
