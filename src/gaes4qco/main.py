import json
import numpy as np
import random
from pathlib import Path
from typing import List
from qiskit.quantum_info import Statevector

from containers import AppContainer
from experiment.config import ExperimentConfig
from experiment.parallel_manager import ParallelExperimentManager
from quantum_circuit.circuit import Circuit
from quantum_circuit.interfaces import IQuantumCircuitAdapter

PROJECT_PATH = Path(__file__).resolve().parents[2]


def save_circuit_details(circuit: Circuit, adapter: IQuantumCircuitAdapter, filepath_base: str):
    """Salva a estrutura de um circuito em .json e sua representação em .txt."""
    print(f"Salvando detalhes do circuito em '{filepath_base}.json/.txt'...")
    Path(filepath_base).parent.mkdir(parents=True, exist_ok=True)

    with open(f"{filepath_base}.json", 'w', encoding='utf-8') as f:
        json.dump(circuit.to_dict(), f, indent=4)
    qiskit_circuit = adapter.from_domain(circuit)
    with open(f"{filepath_base}.txt", 'w', encoding='utf-8') as f:
        f.write(str(qiskit_circuit.draw('text')))


def create_random_target(num_qubits: int, depth: int, seed: int) -> Statevector:
    """
    Usa factories para gerar um circuito aleatório, salvá-lo e
    retornar seu statevector e o objeto de domínio.
    """
    print("Gerando circuito alvo aleatório...")
    random.seed(seed)
    np.random.seed(seed)

    container = AppContainer()

    # ## CORREÇÃO AQUI: Acessando os providers através dos sub-containers ##
    circuit_factory = container.circuit.circuit_factory()
    adapter = container.circuit.qiskit_adapter()

    domain_circuit = circuit_factory.create_random_circuit(
        num_qubits=num_qubits, max_depth=depth, min_depth=depth
    )

    # Salva o circuito alvo para referência
    target_filepath = PROJECT_PATH / f"results/target_circuits/target_seed_{seed}"
    save_circuit_details(domain_circuit, adapter, str(target_filepath))

    qiskit_circuit = adapter.from_domain(domain_circuit)
    target_sv = Statevector.from_instruction(qiskit_circuit)
    print("Alvo gerado e salvo com sucesso.")
    return target_sv


def main():
    # --- Configuração Geral dos Experimentos ---
    NUM_QUBITS = 4
    DEPTH_GEN_TARGET = 20
    NUM_TARGETS = 2  # Quantidade de Targets criados
    NUM_EXPERIMENTS_PER_TARGET = 1  # Quantidade de Experimentos por Target
    INITIAL_SEED_TARGETS = 10000  # Semente Inicial para gerar os circuitos alvos
    INITIAL_SEED_EXPERIMENTS = 1111  # Semente inicial para as execuções do GA

    # --- Criação dos Alvos para os Experimentos ---
    targets_svs = [
        create_random_target(
            num_qubits=NUM_QUBITS, depth=DEPTH_GEN_TARGET, seed=s
        ) for s in range(INITIAL_SEED_TARGETS, INITIAL_SEED_TARGETS + NUM_TARGETS)
    ]

    experiment_configs: List[ExperimentConfig] = []
    for target in targets_svs:
        target_sv_data = target.data.tolist()

        # --- Definição da Lista de Configurações para o Lote ---
        experiment_configs += [
            ExperimentConfig(
                seed=s,
                use_stepsize=True,
                use_weighted_fitness=True,
                use_adaptive_rates=True,
                use_bandit_mutation=True,
                num_qubits=NUM_QUBITS,
                max_depth=15,
                min_depth=2,
                target_depth=8,
                elitism_size=5,
                population_size=100,
                max_generations=25,
                target_statevector_data=target_sv_data
            ) for s in range(INITIAL_SEED_EXPERIMENTS, INITIAL_SEED_EXPERIMENTS + NUM_EXPERIMENTS_PER_TARGET)
        ]

    # --- Execução e Análise ---
    manager = ParallelExperimentManager(configs=experiment_configs)
    all_results = manager.run_all()

    print("\n--- Resumo dos Resultados ---")
    for result in all_results:
        print(
            f"Seed {result['seed']}: Melhor Fitness = {result['best_fitness']:.6f} (Duração: {result['duration_seconds']:.2f}s)")

    if all_results:
        best_run = max(all_results, key=lambda r: r['best_fitness'])
        print(f"\n🏆 Melhor execução geral foi com a Seed {best_run['seed']} e fitness {best_run['best_fitness']:.6f}")


if __name__ == "__main__":
    main()