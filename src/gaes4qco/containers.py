from dependency_injector import containers, providers
from qiskit.quantum_info import Statevector

from quantum_circuit import qiskit_adapter, circuit_factory, gate_factory
from evolutionary_algorithm import selection, crossover, mutation, population_factory, rate_adapter
from optimization import fitness, observer, optimizer


class QuantumCircuitContainer(containers.DeclarativeContainer):
    """Sub-container para os componentes da feature quantum_circuit."""
    config = providers.Configuration()

    qiskit_adapter = providers.Factory(qiskit_adapter.QiskitAdapter)
    gate_factory = providers.Factory(gate_factory.GateFactory)
    circuit_factory = providers.Factory(
        circuit_factory.CircuitFactory,
        gate_factory=gate_factory,
        use_evolutionary_strategy=config.evolution.stepsize
    )


class OptimizationContainer(containers.DeclarativeContainer):
    """Sub-container para os componentes de avaliação e observação."""
    config = providers.Configuration()
    gateways = providers.DependenciesContainer()

    # O target_statevector criado com os dados passados na configuração do experimento
    target_statevector = providers.Singleton(
        Statevector,
        data=config.quantum.target_statevector_data
    )

    # Seletor para a função de fitness
    evaluator = providers.Selector(
        config.selection_strategy.fitness,
        weighted=providers.Factory(
            fitness.WeightedFidelityFitnessEvaluator,
            target_statevector=target_statevector,
            circuit_adapter=gateways.qiskit_adapter,
            target_depth=config.quantum.target_depth
        ),
        default=providers.Factory(
            fitness.FidelityFitnessEvaluator,
            target_statevector=target_statevector,
            circuit_adapter=gateways.qiskit_adapter
        ),
    )

    observer = providers.Factory(
        observer.JsonProgressObserver,
        filename=config.observer.filename
    )


class EvolutionaryAlgorithmContainer(containers.DeclarativeContainer):
    """Sub-container para as estratégias do algoritmo evolucionário."""
    config = providers.Configuration()
    factories = providers.DependenciesContainer()
    optimization = providers.DependenciesContainer()

    # --- Estratégias de Seleção ---
    parent_selector = providers.Factory(
        selection.TournamentSelection,
        population_size=config.evolution.population_size,
        tournament_size=config.evolution.tournament_size,
        elitism_count=config.evolution.elitism_size,
        survivor_selection=False
    )
    survivor_selector = providers.Factory(
        selection.TournamentSelection,
        population_size=config.evolution.population_size,
        tournament_size=config.evolution.tournament_size,
        elitism_count=config.evolution.elitism_size,
        survivor_selection=True
    )

    # --- Estratégia de Crossover ---
    crossover_strategy = providers.Factory(
        crossover.UniformCrossover,
        crossover_rate=config.evolution.crossover_rate
    )

    # --- Estratégias de Mutação ---
    mutation_pool = providers.List(
        providers.Factory(mutation.SwapColumnsMutation),
        providers.Factory(
            mutation.SingleGateFlipMutation,
            gate_factory=factories.gate_factory,
            use_evolutionary_strategy=config.evolution.stepsize
        ),
        providers.Factory(
            mutation.ChangeDepthMutation,
            max_depth=config.evolution.max_depth,
            gate_factory=factories.gate_factory,
            use_evolutionary_strategy=config.evolution.stepsize,
        ),
        providers.Factory(
            mutation.GateParameterMutation,
            fitness_evaluator=optimization.evaluator
        ),
        providers.Factory(mutation.SwapControlTargetMutation)
    )

    mutation_selector = providers.Selector(
        config.selection_strategy.mutation,
        bandit=providers.Factory(
            mutation.BanditMutationSelector,
            mutation_strategies=mutation_pool,
            mutation_rate=config.evolution.mutation_rate,
            fitness_evaluator=optimization.evaluator
        ),
        default=providers.Factory(
            mutation.RandomMutation,
            mutation_strategies=mutation_pool,
            mutation_rate=config.evolution.mutation_rate
        ),
    )

    # --- Adaptador de Taxas ---
    rate_adapter = providers.Selector(
        config.selection_strategy.rate_adapter,
        adaptive=providers.Factory(
            rate_adapter.DiversityAdaptiveRateAdapter,
            min_mutation_rate=config.adaptive_rates.min_mutation_rate,
            max_mutation_rate=config.adaptive_rates.max_mutation_rate,
            min_crossover_rate=config.adaptive_rates.min_crossover_rate,
            max_crossover_rate=config.adaptive_rates.max_crossover_rate
        ),
        default=providers.Factory(
            rate_adapter.FixedRateAdapter,
            crossover_rate=config.evolution.crossover_rate,
            mutation_rate=config.evolution.mutation_rate
        ),
    )


class AppContainer(containers.DeclarativeContainer):
    """
    Container principal que agrega todos os sub-containers da aplicação.
    """
    config = providers.Configuration()

    # --- Agregação dos Sub-Containers ---

    # 1. Componentes de Circuito Quântico (sem dependências externas)
    circuit = providers.Container(
        QuantumCircuitContainer,
        config=config
    )

    population = providers.Factory(
        population_factory.PopulationFactory,
        circuit_factory=circuit.circuit_factory
    )

    # 2. Componentes de Otimização (dependem do container de circuito)
    optimization = providers.Container(
        OptimizationContainer,
        config=config,
        gateways=circuit
    )

    # 3. Componentes do Algoritmo Evolucionário (dependem de factories e otimização)
    evolutionary_algorithm = providers.Container(
        EvolutionaryAlgorithmContainer,
        config=config,
        factories=circuit,
        optimization=optimization
    )

    # 4. Montagem do Optimizer Principal (componente de mais alto nível)
    optimizer = providers.Factory(
        optimizer.Optimizer,
        fitness_evaluator=optimization.evaluator,
        parent_selection=evolutionary_algorithm.parent_selector,
        survivor_selection=evolutionary_algorithm.survivor_selector,
        crossover=evolutionary_algorithm.crossover_strategy,
        mutation=evolutionary_algorithm.mutation_selector,
        population_factory=population,
        rate_adapter=evolutionary_algorithm.rate_adapter,
        diversity_threshold=config.evolution.diversity_threshold,
        injection_rate=config.evolution.injection_rate,
        observer=optimization.observer,
    )
