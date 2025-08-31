from itertools import combinations
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

    def _calculate_distance(self, ind1, ind2) -> float:
        """Calcula a distância de Jaccard normalizada entre dois indivíduos."""
        set1 = ind1.get_structural_representation()
        set2 = ind2.get_structural_representation()

        intersection_size = len(set1.intersection(set2))
        union_size = len(set1.union(set2))

        if union_size == 0:
            return 0.0

        jaccard_similarity = intersection_size / union_size
        return 1.0 - jaccard_similarity

    def shape(self, population: Population):
        """Ajusta o fitness de cada indivíduo na população."""
        individuals = population.get_individuals()

        for i in range(len(individuals)):
            niche_count = 0
            for j in range(len(individuals)):
                distance = self._calculate_distance(individuals[i], individuals[j])

                # Calcula a função de compartilhamento
                if distance < self._sigma_share:
                    sh = 1 - (distance / self._sigma_share) ** self._alpha
                    niche_count += sh

            # Ajusta o fitness dividindo-o pela contagem do nicho
            if niche_count > 0:
                individuals[i].fitness /= niche_count
