from analysis.distance_metrics import StructuralJaccardDistance
from analysis.interfaces import IDistanceMetric

from .interfaces import IFitnessShaper
from evolutionary_algorithm.population import Population


class NullFitnessShaper(IFitnessShaper):
    """Um modelador que não faz nada. Usado quando o Fitness Sharing está desativado."""

    def shape(self, population: Population):
        pass  # Não faz nenhuma alteração


class FitnessSharingShaper(IFitnessShaper):
    """
    Ajusta o fitness da população usando a técnica de Fitness Sharing.
    Penaliza indivíduos que são muito similares a outros.
    """

    def __init__(self, sharing_radius: float, alpha: float):
        """
        Args:
            sharing_radius (float): O raio de nicho (sigma_share). A distância abaixo
                                    da qual dois indivíduos são considerados do mesmo nicho.
            alpha (float): Expoente que controla o formato da função de compartilhamento.
        """
        self._sigma_share = sharing_radius
        self._alpha = alpha
        self._distance_metric = StructuralJaccardDistance()

    def shape(self, population: Population):
        """Ajusta o fitness de cada indivíduo na população."""
        individuals = population.get_individuals()

        for i in range(len(individuals)):
            niche_count = 0
            for j in range(len(individuals)):
                distance = self._distance_metric.calculate(individuals[i], individuals[j])

                # Calcula a função de compartilhamento
                if distance < self._sigma_share:
                    sh = 1 - (distance / self._sigma_share) ** self._alpha
                    niche_count += sh

            # Ajusta o fitness dividindo-o pela contagem do nicho
            if niche_count > 0:
                individuals[i].fitness /= niche_count
