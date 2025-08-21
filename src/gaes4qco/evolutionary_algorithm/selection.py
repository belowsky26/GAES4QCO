import random
from typing import List
from .interfaces import ISelectionStrategy
from .population import Population
from ..quantum_circuit.circuit import Circuit


class TournamentSelection(ISelectionStrategy):
    def __init__(self, population_size: int, tournament_size: int, elitism_count: int, survivor_selection: bool = False):
        self.population_size = population_size
        self.tournament_size = tournament_size
        self.elitism_count = max(elitism_count, 1)
        self.survivor_selection = survivor_selection

    def select(self, population: Population) -> Population:
        # Assinatura já estava correta. Apenas o corpo foi ajustado.
        if not population:
            return Population()  # Retorna uma população vazia

        # ## 1. Extrai a lista de indivíduos para trabalhar com ela.
        individuals = population.get_individuals()

        if self.survivor_selection:
            # A lógica de elitismo é mais crítica aqui
            selected_individuals = self._select_survivors_with_elitism(individuals)
        else:
            selected_individuals = self._select_for_crossover(individuals)

        # ## 3. Encapsula a lista resultante em um novo objeto Population.
        return Population(selected_individuals)

    def _select_for_crossover(self, individuals: List[Circuit]) -> List[Circuit]:
        # A assinatura do método privado foi mantida, pois ele opera sobre uma lista.
        next_gen_parents = []
        for _ in range(self.population_size):
            # Garante que o tamanho do grupo não seja maior que a população
            current_tournament_size = min(self.tournament_size, len(individuals))
            group = random.sample(individuals, current_tournament_size)
            champion = max(group, key=lambda circuit: circuit.fitness)
            next_gen_parents.append(champion)
        return next_gen_parents

    def _select_survivors_with_elitism(self, individuals: List[Circuit]) -> List[Circuit]:
        """
        Seleciona os sobreviventes usando elitismo garantido seguido por torneios.
        """

        # Ordena a população pelo fitness em ordem decrescente
        sorted_population = sorted(individuals, key=lambda ind: ind.fitness, reverse=True)

        # 1. Elitismo: Separa os melhores indivíduos
        elites = sorted_population[:self.elitism_count]

        # O restante da população competirá nos torneios
        competitors = sorted_population[self.elitism_count:]

        num_tournaments_to_run = self.population_size - self.elitism_count
        tournament_winners = []

        for _ in range(num_tournaments_to_run):
            if not competitors:
                break  # Para se a população de competidores acabar

            current_tournament_size = min(self.tournament_size, len(competitors))
            group = random.sample(competitors, current_tournament_size)

            champion = max(group, key=lambda circuit: circuit.fitness)
            tournament_winners.append(champion)

            # Remove o campeão para que ele não compita novamente (torneio sem reposição)
            competitors.remove(champion)

        # A nova população de sobreviventes é a junção dos elites e dos vencedores do torneio
        return elites + tournament_winners