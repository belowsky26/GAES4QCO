from dataclasses import dataclass
from typing import List


@dataclass
class ResultData:
    """
    Contém os dados de resultado de uma única execução do algoritmo.
    """
    fitness_per_generation: List[List[float]]
    average_fitness_per_generation: List[float]
    std_dev_fitness_per_generation: List[float]
    structural_diversity_per_generation: List[float]

    @property
    def best_fitness_per_generation(self) -> List[float]:
        """Extrai o melhor fitness (o primeiro elemento) de cada geração."""
        return [gen[0] for gen in self.fitness_per_generation if gen]

    @property
    def generation_count(self) -> int:
        """Retorna o número de gerações registradas."""
        return len(self.average_fitness_per_generation)
