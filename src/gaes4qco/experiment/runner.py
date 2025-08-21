import numpy as np
import random
import time

from dependency_injector import providers
from qiskit.quantum_info import Statevector

from ..containers import AppContainer
from .config import ExperimentConfig


class ExperimentRunner:
    """Executa uma única instância completa de um experimento do GA."""

    def __init__(self, config: ExperimentConfig):
        self.config = config
        self.container = AppContainer()

    def run(self) -> dict:
        """
        Configura o container, executa o otimizador e retorna os resultados.
        """
        print(f"---   Iniciando Experimento com Seed {self.config.seed}   ---")
        start_time = time.time()

        # Semeia a aleatoriedade
        random.seed(self.config.seed)
        np.random.seed(self.config.seed)

        # Configura o container com os parâmetros deste experimento específico
        target_sv_object = Statevector(self.config.target_statevector_data)
        self.container.target_statevector.override(
            providers.Object(target_sv_object)
        )

        self.container.config.from_dict({
            "quantum": {
                "num_qubits": self.config.num_qubits
            },
            "evolution": {
                "population_size": self.config.population_size,
                "elitism_size": self.config.elitism_size,
                "tournament_size": self.config.tournament_size,
                "crossover_rate": self.config.crossover_rate,
                "mutation_rate": self.config.mutation_rate,
                "max_depth": self.config.max_depth,
                "diversity_threshold": self.config.diversity_threshold,
                "injection_rate": self.config.injection_rate,
            },
            "observer": {
                "filename": self.config.results_filename
            }
        })

        # Pega os componentes necessários do container
        optimizer = self.container.optimizer()
        pop_factory = self.container.population_factory()

        # Executa a otimização
        initial_pop = pop_factory.create(
            population_size=self.config.population_size,
            num_qubits=self.config.num_qubits,
            max_depth=self.config.max_depth,
            min_depth=self.config.min_depth
        )

        best_circuit = optimizer.run(
            initial_population=initial_pop,
            max_generations=self.config.max_generations
        )

        end_time = time.time()
        duration = end_time - start_time
        print(f"---   Fim Experimento Seed {self.config.seed} | Duração: {duration:.2f}s   ---")

        # Retorna um dicionário com os resultados importantes
        return {
            "seed": self.config.seed,
            "best_fitness": best_circuit.fitness,
            "duration_seconds": duration
        }


# Função standalone para ser usada pelo multiprocessing
# Ela garante que cada processo crie seus próprios objetos, evitando problemas de "pickling".
def run_experiment_from_config(config: ExperimentConfig) -> dict:
    runner = ExperimentRunner(config)
    return runner.run()
