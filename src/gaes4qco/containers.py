from dependency_injector import containers, providers
from qiskit.quantum_info import Statevector

# Importamos nossas classes de implementação de todas as features
from quantum_circuit import qiskit_adapter, circuit_factory, gate_factory
from evolutionary_algorithm import (
    selection,
    crossover,
    mutation,
    population_factory
)
from optimization import fitness, observer, optimizer


class AppContainer(containers.DeclarativeContainer):
    """
    Container principal de Injeção de Dependência para a aplicação GAES4QCO.
    """
    # ==================================================================
    # 1. Configuração
    # providers.Configuration permite injetar valores de fora (ex: YAML, dict)
    # ==================================================================
    config: providers.Configuration = providers.Configuration()

    # ==================================================================
    # 2. Gateways e Adapters (Comunicação com o mundo externo)
    # Usamos providers.Factory para criar uma nova instância a cada vez que for pedido.
    # ==================================================================
    qiskit_adapter = providers.Factory(
        qiskit_adapter.QiskitAdapter
    )

    # ==================================================================
    # 3. Factories (Classes que criam nossos objetos de domínio)
    # ==================================================================
    gate_factory = providers.Factory(
        gate_factory.GateFactory
    )

    circuit_factory = providers.Factory(
        circuit_factory.CircuitFactory,
        # A injeção de dependência acontece aqui! O container sabe que
        # CircuitFactory precisa de uma GateFactory.
        gate_factory=gate_factory,
        use_evolutionary_strategy=config.evolution.stepsize
    )

    population_factory = providers.Factory(
        population_factory.PopulationFactory,
        circuit_factory=circuit_factory
    )

    # ==================================================================
    # 4. Estratégias e Avaliadores
    # ==================================================================

    # --- Fitness ---
    # Usamos um provider Singleton para o Statevector, pois ele não muda.
    target_statevector = providers.Singleton(
        Statevector.from_label,
        label=config.quantum.target_statevector_label
    )

    fitness_evaluator = providers.Factory(
        fitness.FidelityFitnessEvaluator,
        target_statevector=target_statevector,
        circuit_adapter=qiskit_adapter
    )

    weighted_fidelity_evaluator = providers.Factory(
        fitness.WeightedFidelityFitnessEvaluator,
        target_statevector=target_statevector,
        circuit_adapter=qiskit_adapter,
        target_depth=config.quantum.target_depth
    )

    # --- Seleção ---
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

    # --- Crossover ---
    crossover_strategy = providers.Factory(
        crossover.UniformCrossover,
        crossover_rate=config.evolution.crossover_rate
    )

    # --- Mutação (a montagem do pool de mutações fica muito limpa aqui) ---
    mutation_pool = providers.List(
        providers.Factory(mutation.SwapColumnsMutation),
        providers.Factory(
            mutation.SingleGateFlipMutation,
            gate_factory=gate_factory,
            use_evolutionary_strategy=config.evolution.stepsize
        ),
        providers.Factory(
            mutation.ChangeDepthMutation,
            max_depth=config.evolution.max_depth,
            gate_factory=gate_factory,
            use_evolutionary_strategy=config.evolution.stepsize,
        ),
        providers.Factory(
            mutation.GateParameterMutation,
            fitness_evaluator=fitness_evaluator
        ),
        providers.Factory(mutation.SwapControlTargetMutation)
    )

    mutation_strategy = providers.Factory(
        mutation.RandomMutation,
        mutation_strategies=mutation_pool,
        mutation_rate=config.evolution.mutation_rate
    )

    # ==================================================================
    # 5. Componentes de Alto Nível (Observer e Optimizer)
    # ==================================================================
    progress_observer = providers.Factory(
        observer.JsonProgressObserver,
        filename=config.observer.filename
    )

    optimizer = providers.Factory(
        optimizer.Optimizer,
        # fitness_evaluator=fitness_evaluator,
        fitness_evaluator=weighted_fidelity_evaluator,
        parent_selection=parent_selector,
        survivor_selection=survivor_selector,
        crossover=crossover_strategy,
        mutation=mutation_strategy,
        population_factory=population_factory,
        diversity_threshold=config.evolution.diversity_threshold,
        injection_rate=config.evolution.injection_rate,
        observer=progress_observer,
    )
