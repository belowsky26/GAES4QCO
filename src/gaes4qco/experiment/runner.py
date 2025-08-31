import numpy as np
import random
import time
import json
from pathlib import Path

from dependency_injector import providers
from qiskit.quantum_info import Statevector

from containers import AppContainer
from quantum_circuit.circuit import Circuit
from quantum_circuit.interfaces import IQuantumCircuitAdapter
from .config import ExperimentConfig


def save_circuit_details(circuit: Circuit, adapter: IQuantumCircuitAdapter, filepath_base: str):
    """Salva a estrutura de um circuito em .json e sua representação em .txt."""
    print(f"Salvando detalhes do circuito em '{filepath_base}.json/.txt'...")
    Path(filepath_base).parent.mkdir(parents=True, exist_ok=True)

    with open(f"{filepath_base}.json", 'w', encoding='utf-8') as f:
        json.dump(circuit.to_dict(), f, indent=4)
    qiskit_circuit = adapter.from_domain(circuit)
    with open(f"{filepath_base}.txt", 'w', encoding='utf-8') as f:
        f.write(str(qiskit_circuit.draw('text')))


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

        config_filepath = self.config.results_filename.replace('.json', '_config.json')
        print(f"Salvando configuração do experimento em: {config_filepath}")
        Path(config_filepath).parent.mkdir(parents=True, exist_ok=True)
        with open(config_filepath, 'w', encoding='utf-8') as f:
            json.dump(self.config.to_dict(), f, indent=4)

        random.seed(self.config.seed)
        np.random.seed(self.config.seed)

        self.container.optimization.target_statevector.override(
            providers.Singleton(Statevector, self.config.target_statevector_data)
        )

        self.container.config.from_dict({
            "quantum": {
                "num_qubits": self.config.num_qubits,
                "target_depth": self.config.target_depth
            },
            "selection_strategy": {
                "fitness": "weighted" if self.config.use_weighted_fitness else "default",
                "rate_adapter": "adaptive" if self.config.use_adaptive_rates else "default",
                "mutation": "bandit" if self.config.use_bandit_mutation else "default",
                "survivor": "nsga2" if self.config.use_nsga2_survivor_selection else "default",
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
                "stepsize": self.config.use_stepsize,
            },
            "adaptive_rates": {
                "min_mutation_rate": self.config.min_mutation_rate,
                "max_mutation_rate": self.config.max_mutation_rate,
                "min_crossover_rate": self.config.min_crossover_rate,
                "max_crossover_rate": self.config.max_crossover_rate,
            },
            "observer": {
                "filename": self.config.results_filename
            }
        })

        optimizer = self.container.optimizer()
        pop_factory = self.container.population()

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

        # ## CORREÇÃO 3: Acessa o qiskit_adapter através do sub-container 'circuit' ##
        adapter = self.container.circuit.qiskit_adapter()
        output_base_path = self.config.results_filename.replace('.json', '_best_fitness_circuit')
        save_circuit_details(best_circuit, adapter, output_base_path)

        end_time = time.time()
        duration = end_time - start_time
        print(f"---   Fim Experimento Seed {self.config.seed} | Duração: {duration:.2f}s   ---")

        return {
            "seed": self.config.seed,
            "best_fitness": best_circuit.fitness,
            "duration_seconds": duration
        }


def run_experiment_from_config(config: ExperimentConfig) -> dict:
    runner = ExperimentRunner(config)
    return runner.run()