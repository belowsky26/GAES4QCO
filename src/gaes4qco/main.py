import random
import json
from pathlib import Path

import numpy as np
from qiskit.quantum_info import Statevector

from containers import AppContainer
from experiment.config import ExperimentConfig
from experiment.parallel_manager import ParallelExperimentManager
from quantum_circuit.circuit import Circuit
from quantum_circuit.interfaces import IQuantumCircuitAdapter

PROJECT_PATH = Path(__file__).parents[2]


def save_circuit_details(circuit: Circuit, adapter: IQuantumCircuitAdapter, filepath_base: str):
    """Salva a estrutura de um circuito em .json e sua representação em .txt."""
    print(f"Salvando detalhes do circuito em '{filepath_base}.json/.txt'...")
    with open(f"{filepath_base}.json", 'w') as f:
        json.dump(circuit.to_dict(), f, indent=4)
    qiskit_circuit = adapter.from_domain(circuit)
    with open(f"{filepath_base}.txt", 'w', encoding='utf-8') as f:
        f.write(str(qiskit_circuit.draw('text')))


def create_random_target_statevector(num_qubits: int, depth: int, seed: int) -> Statevector:
    """
    Usa nossas factories para gerar um circuito aleatório e retornar seu statevector.
    """
    print("Gerando circuito alvo aleatório...")
    random.seed(seed)
    np.random.seed(seed)
    # Usa um container temporário apenas para essa tarefa
    container = AppContainer()
    circuit_factory = container.circuit_factory()
    adapter = container.qiskit_adapter()

    # Cria nosso circuito de domínio
    domain_circuit = circuit_factory.create_random_circuit(
        num_qubits=num_qubits,
        max_depth=depth,
        min_depth=depth  # Profundidade fixa para o alvo
    )
    save_circuit_details(domain_circuit, adapter, str(PROJECT_PATH / f"results/target_circuits/circuit_seed_{seed}"))

    # Converte para Qiskit e calcula o statevector
    qiskit_circuit = adapter.from_domain(domain_circuit)
    target_sv = Statevector.from_instruction(qiskit_circuit)
    print("Alvo gerado com sucesso.")
    return target_sv


def main():
    # 1. Parâmetros Gerais do Lote de Experimentos
    NUM_QUBITS = 4
    NUM_EXPERIMENTS = 2  # Quantidade de execuções com seeds diferentes

    # 2. Criação do Circuito Alvo Aleatório (feito uma vez)
    targets_sv_data = []
    for i in range(10000, 10000+NUM_EXPERIMENTS):
        target_statevector = create_random_target_statevector(num_qubits=NUM_QUBITS, depth=20, seed=i)
        # Extrai os dados para passar para os processos de forma segura
        target_sv_data = target_statevector.data.tolist()
        targets_sv_data.append(target_sv_data)
    # 3. Define a lista de configurações para cada experimento
    # Todas as execuções usarão o mesmo alvo
    experiment_configs = [
        ExperimentConfig(
            seed=s,
            stepsize=True,
            num_qubits=NUM_QUBITS,
            max_depth=15,
            min_depth=2,
            target_depth=8,
            elitism_size=5,
            population_size=200,
            max_generations=1000,
            target_statevector_data=targets_sv_data.pop()
        ) for s in range(1111, 1111 + NUM_EXPERIMENTS)  # <-- Exemplo: rodando 10 experimentos com seeds de 0 a 9
    ]

    # 2. Cria o gerenciador de experimentos
    manager = ParallelExperimentManager(configs=experiment_configs)

    # 3. Executa o lote
    all_results = manager.run_all()

    # 4. Processa os resultados finais
    print("\n--- Resumo dos Resultados ---")
    for result in all_results:
        print(
            f"Seed {result['seed']}: Melhor Fitness = {result['best_fitness']:.6f} (Duração: {result['duration_seconds']:.2f}s)")

    # Encontra a melhor execução de todas
    best_run = max(all_results, key=lambda r: r['best_fitness'])
    print(f"\n🏆 Melhor execução geral foi com a Seed {best_run['seed']} e fitness {best_run['best_fitness']:.6f}")


if __name__ == "__main__":
    main()
