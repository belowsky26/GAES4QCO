from ..evolutionary_algorithm.population_factory import PopulationFactory
from ..quantum_circuit.circuit import Circuit
from ..evolutionary_algorithm.interfaces import (
    ISelectionStrategy, ICrossoverStrategy, IMutationStrategy
)
from ..evolutionary_algorithm.population import Population
from .interfaces import IFitnessEvaluator, IProgressObserver


class Optimizer:
    """
    ## O motor do Algoritmo Genético. Orquestra todo o processo evolucionário.
    ## É configurado com interfaces, não com classes concretas.
    """

    def __init__(
            self,
            fitness_evaluator: IFitnessEvaluator,
            parent_selection: ISelectionStrategy,
            survivor_selection: ISelectionStrategy,
            crossover: ICrossoverStrategy,
            mutation: IMutationStrategy,
            population_factory: PopulationFactory,
            diversity_threshold: float,
            injection_rate: float,
            observer: IProgressObserver = None
    ):
        self._fitness_evaluator = fitness_evaluator
        self._parent_selection = parent_selection
        self._survivor_selection = survivor_selection
        self._crossover = crossover
        self._mutation = mutation
        self._population_factory = population_factory
        self._diversity_threshold = diversity_threshold
        self._injection_rate = injection_rate
        self._observer = observer

    def run(self, initial_population: Population, max_generations: int) -> Circuit:
        """
        Executa o fluxo do algoritmo genético por um número de gerações.
        """
        current_population = initial_population

        print("Evaluating initial population...")
        self._evaluate_population(current_population)

        for gen in range(max_generations):
            if self._observer:
                self._observer.update(gen, current_population)
            current_diversity = current_population.calculate_structural_diversity()
            if current_diversity < self._diversity_threshold:
                print(f"  -> Low diversity detected ({current_diversity:.4f}). Injecting fresh individuals.")
                self._inject_fresh_blood(current_population)

            # 1. Seleção dos Pais
            parent_population = self._parent_selection.select(current_population)

            # 2. Cruzamento
            offspring_population = self._crossover.crossover(parent_population)

            # 3. Mistura a antiga população com a nova, evitando duplicatas
            offspring_population = Population(offspring_population.get_individuals() + current_population.get_individuals())
            offspring_population.remove_duplicates()

            # 4. Mutação
            mutated_population = self._mutation.mutate(offspring_population)

            # 5. Avaliação dos novos indivíduos
            self._evaluate_population(mutated_population)

            current_population = self._survivor_selection.select(mutated_population)

        if self._observer:
            self._observer.save()

        print("Optimization finished.")
        return current_population.get_fittest()

    def _evaluate_population(self, population: Population):
        """
        ## Helper para calcular o fitness de cada indivíduo que ainda não foi avaliado.
        ## Substitui a antiga função 'applyFitnessIntoCircuit'.
        """
        for individual in population.get_individuals():
            if individual.fitness == 0.0:  # Assume 0.0 como não avaliado
                individual.fitness = self._fitness_evaluator.evaluate(individual)

    def _inject_fresh_blood(self, population: Population):
        """Substitui os piores indivíduos por novos indivíduos aleatórios."""
        num_to_inject = int(len(population) * self._injection_rate)
        if num_to_inject == 0 or not population:
            return

        sample_ind = population.get_individuals()[0]
        min_depth = max(1, sample_ind.depth // 2)

        new_individuals_pop = self._population_factory.create(
            population_size=num_to_inject,
            num_qubits=sample_ind.count_qubits,
            max_depth=sample_ind.depth,
            min_depth=min_depth
        )
        self._evaluate_population(new_individuals_pop)

        individuals = population.get_individuals()
        individuals.sort(key=lambda ind: ind.fitness)  # Ordena do pior para o melhor

        # Substitui os piores pelos novos
        individuals[:num_to_inject] = new_individuals_pop.get_individuals()
