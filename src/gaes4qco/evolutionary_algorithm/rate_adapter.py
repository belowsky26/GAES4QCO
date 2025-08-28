from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class EvolutionRates:
    """Contém as taxas de crossover e mutação para uma geração."""
    crossover_rate: float
    mutation_rate: float


class IRateAdapter(ABC):
    """Interface para estratégias que adaptam as taxas de evolução."""

    @abstractmethod
    def adapt(self, diversity: float) -> EvolutionRates:
        """
        Recebe a diversidade atual e retorna as novas taxas de crossover e mutação.
        """
        pass


class FixedRateAdapter(IRateAdapter):
    """Implementa a estratégia de taxas fixas."""

    def __init__(self, crossover_rate: float, mutation_rate: float):
        self._rates = EvolutionRates(crossover_rate, mutation_rate)

    def adapt(self, diversity: float) -> EvolutionRates:
        # Simplesmente retorna as taxas fixas, ignorando a diversidade.
        return self._rates


class DiversityAdaptiveRateAdapter(IRateAdapter):
    """
    Adapta as taxas de evolução com base na diversidade genética da população.
    - Baixa diversidade: Aumenta a mutação (exploração).
    - Alta diversidade: Aumenta o crossover (explotação).
    """

    def __init__(self, min_mutation_rate: float, max_mutation_rate: float,
                 min_crossover_rate: float, max_crossover_rate: float):
        self.min_mr = min_mutation_rate
        self.max_mr = max_mutation_rate
        self.min_cr = min_crossover_rate
        self.max_cr = max_crossover_rate

    def adapt(self, diversity: float) -> EvolutionRates:
        """
        Calcula as novas taxas usando uma interpolação linear inversa.
        Quanto menor a diversidade, maior a taxa de mutação e menor a de crossover.
        """
        # Normaliza a diversidade para o intervalo [0, 1] (já está nesse intervalo)
        diversity_norm = max(0.0, min(1.0, diversity))

        # Interpolação linear inversa para a mutação
        mutation_rate = self.max_mr - (diversity_norm * (self.max_mr - self.min_mr))

        # Interpolação linear direta para o crossover
        crossover_rate = self.min_cr + (diversity_norm * (self.max_cr - self.min_cr))

        return EvolutionRates(crossover_rate=crossover_rate, mutation_rate=mutation_rate)
