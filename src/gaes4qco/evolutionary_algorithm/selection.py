import random
from typing import List
from .interfaces import ISelectionStrategy
from .population import Population
from quantum_circuit.circuit import Circuit


class TournamentSelection(ISelectionStrategy):
    def __init__(self, population_size: int, tournament_size: int, elitism_count: int, survivor_selection):
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
        sorted_population = sorted(individuals, key=lambda ind: ind.fidelity, reverse=True)

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


class NSGA2Selection(ISelectionStrategy):
    """
    Implementa a seleção de sobreviventes baseada no algoritmo NSGA-II.
    Esta estratégia substitui a seleção por torneio na fase de sobrevivência
    para otimização multiobjetivo.
    """

    def __init__(self, population_size: int, elitism_count: int):
        self.population_size = population_size
        self.elitism_count = max(elitism_count, 1)

    def select(self, population: Population) -> Population:
        individuals = population.get_individuals()
        sorted_population = sorted(individuals, key=lambda ind: ind.fidelity, reverse=True)
        fronts = self._non_dominated_sort(sorted_population[self.elitism_count:])
        next_gen_individuals = sorted_population[:self.elitism_count]
        for front in fronts:
            if len(next_gen_individuals) + len(front) <= self.population_size:
                next_gen_individuals.extend(front)
            else:
                self._crowding_distance_assignment(front)
                front.sort(key=lambda x: x.crowding_distance, reverse=True)
                needed = self.population_size - len(next_gen_individuals)
                next_gen_individuals.extend(front[:needed])
                break

        return Population(next_gen_individuals)

    def _non_dominated_sort(self, individuals: List[Circuit]) -> List[List[Circuit]]:
        fronts = [[]]
        for p in individuals:
            p.domination_count = 0
            p.dominated_solutions = []
            for q in individuals:
                if p is q:
                    continue
                if self._dominates(p, q):
                    p.dominated_solutions.append(q)
                elif self._dominates(q, p):
                    p.domination_count += 1

            if p.domination_count == 0:
                p.rank = 0
                fronts[0].append(p)

        i = 0
        while i < len(fronts) and fronts[i]:
            next_front = []
            for p in fronts[i]:
                for q in p.dominated_solutions:
                    q.domination_count -= 1
                    if q.domination_count == 0:
                        q.rank = i + 1
                        next_front.append(q)
            i += 1
            if next_front:
                fronts.append(next_front)

        return fronts

    def _dominates(self, p: Circuit, q: Circuit) -> bool:
        """Retorna True se p domina q."""
        p_objectives = p.objectives
        q_objectives = q.objectives

        # Pelo menos um objetivo em 'p' deve ser melhor
        at_least_one_better = any(p_obj > q_obj for p_obj, q_obj in zip(p_objectives, q_objectives))
        # Nenhum objetivo em 'p' pode ser pior
        none_worse = all(p_obj >= q_obj for p_obj, q_obj in zip(p_objectives, q_objectives))

        return at_least_one_better and none_worse

    def _crowding_distance_assignment(self, front: List[Circuit]):
        if not front:
            return

        for ind in front:
            ind.crowding_distance = 0.0

        num_objectives = len(front[0].objectives)

        for m in range(num_objectives):
            front.sort(key=lambda x: x.objectives[m])

            # Atribui distância infinita para as soluções extremas
            front[0].crowding_distance = float('inf')
            front[-1].crowding_distance = float('inf')

            # Normaliza os valores do objetivo
            min_obj = front[0].objectives[m]
            max_obj = front[-1].objectives[m]
            range_obj = max_obj - min_obj
            if range_obj == 0:
                continue

            # Calcula a distância para as soluções intermediárias
            for i in range(1, len(front) - 1):
                distance = front[i + 1].objectives[m] - front[i - 1].objectives[m]
                front[i].crowding_distance += distance / range_obj
