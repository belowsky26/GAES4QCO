import json
import numpy as np
import random
from pathlib import Path
from typing import List, Tuple, Optional
from qiskit.quantum_info import Statevector

from containers import AppContainer, QuantumCircuitContainer
from experiment.config import ExperimentConfig, PhaseConfig
from experiment.parallel_manager import ParallelExperimentManager
from quantum_circuit.circuit import Circuit
from quantum_circuit.interfaces import IQuantumCircuitAdapter
from shared.value_objects import CrossoverType

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


def create_random_target(num_qubits: int, depth: int, seed: int, allowed_gates: Optional[List[str]] = None) -> Tuple[Statevector, str]:
    """
    Usa factories para gerar um circuito aleatório, salvá-lo e
    retornar seu statevector e o objeto de domínio.
    """
    print("Gerando circuito alvo aleatório...")
    random.seed(seed)
    np.random.seed(seed)

    circuit_container = QuantumCircuitContainer()
    circuit_container.config.from_dict({"quantum": {"allowed_gates": allowed_gates}})

    # ## CORREÇÃO AQUI: Acessando os providers através dos sub-containers ##
    circuit_factory = circuit_container.circuit_factory()
    adapter = circuit_container.qiskit_adapter()

    domain_circuit = circuit_factory.create_random_circuit(
        num_qubits=num_qubits, max_depth=depth, min_depth=depth, use_evolutionary_strategy=False
    )

    # Salva o circuito alvo para referência
    target_filepath = PROJECT_PATH / f"results/target_circuits/target_seed_{seed}"
    save_circuit_details(domain_circuit, adapter, str(target_filepath))

    qiskit_circuit = adapter.from_domain(domain_circuit)
    print(qiskit_circuit.depth())
    target_sv = Statevector.from_instruction(qiskit_circuit)
    print("Alvo gerado e salvo com sucesso.")
    return target_sv, str(target_filepath)


def main():
    # --- Configuração Geral dos Experimentos ---
    NUM_QUBITS = 4
    DEPTH_GEN_TARGET = 20
    NUM_TARGETS = 4  # Quantidade de Targets criados
    NUM_EXPERIMENTS_PER_TARGET = 1  # Quantidade de Experimentos por Target
    INITIAL_SEED_TARGETS = 101  # Semente Inicial para gerar os circuitos alvos
    INITIAL_SEED_EXPERIMENTS = 1  # Semente inicial para as execuções do GA
    ALLOWED_GATES = None # ["IGate", "RZGate", "SXGate", "XGate", "CXGate"]
    # --- Criação dos Alvos para os Experimentos ---
    targets_svs_filename = [
        create_random_target(
            num_qubits=NUM_QUBITS, depth=DEPTH_GEN_TARGET, seed=s, allowed_gates=ALLOWED_GATES
        ) for s in range(INITIAL_SEED_TARGETS, INITIAL_SEED_TARGETS + NUM_TARGETS)
    ]

    experiment_configs: List[ExperimentConfig] = []
    for target, filename in targets_svs_filename:
        target_sv_data = target.data.tolist()

        # --- Definição da Lista de Configurações para o Lote ---

        ffrftn_phase = [
            PhaseConfig(
                generations=100,
                use_stepsize=True,  # True: Aumenta em até 30% o tempo
                use_weighted_fitness=True,  # Não afeta quase nada ~8%
                use_adaptive_rates=True,
                use_bandit_mutation=True,  # True aumenta tempo de execução ~200%
                use_nsga2_survivor_selection=True,  # True aumenta tempo de execução
                use_fitness_sharing=True,  # True aumenta tempo de execução
                crossover_strategy=CrossoverType.BLOCKWISE,
                fidelity_threshold_stop=None,
            )
        ]
        farttn_phase = [PhaseConfig(
                generations=g,
                use_stepsize=True,  # True: Aumenta em até 30% o tempo
                use_weighted_fitness=False,  # Não afeta quase nada ~8%
                use_adaptive_rates=False,  # False: Dependendo da taxa fixa de mutação e crossover pode afetar negativamente o tempo quando
                use_bandit_mutation=False,  # True aumenta tempo de execução ~200%
                use_nsga2_survivor_selection=False,  # True aumenta tempo de execução
                use_fitness_sharing=False,  # True aumenta tempo de execução
                crossover_strategy=CrossoverType.MULTI_POINT,
                fidelity_threshold_stop=None
            ) for g in [400, 100, 100, 400]
        ]
        warttn_phase = [
            PhaseConfig(
                generations=50,
                use_stepsize=True,  # True: Aumenta em até 30% o tempo
                use_weighted_fitness=True,  # Não afeta quase nada ~8%
                use_adaptive_rates=True,
                # False: Dependendo da taxa fixa de mutação e crossover pode afetar negativamente o tempo quando
                use_bandit_mutation=False,  # True aumenta tempo de execução ~200%
                use_nsga2_survivor_selection=False,  # True aumenta tempo de execução
                use_fitness_sharing=False,  # True aumenta tempo de execução,
                crossover_strategy=CrossoverType.MULTI_POINT,
                fidelity_threshold_stop=None
            )
        ]
        fartts_phase = [
            PhaseConfig(
                generations=100,
                use_stepsize=True,  # True: Aumenta em até 30% o tempo
                use_weighted_fitness=False,  # Não afeta quase nada ~8%
                use_adaptive_rates=True,
                use_bandit_mutation=False,  # True aumenta tempo de execução ~200%
                use_nsga2_survivor_selection=False,  # True aumenta tempo de execução
                use_fitness_sharing=True,  # True aumenta tempo de execução
                crossover_strategy=CrossoverType.MULTI_POINT,
                fidelity_threshold_stop=None
            )
        ]
        fartnt_phase = [
            PhaseConfig(
                generations=250,
                use_stepsize=True,  # True: Aumenta em até 30% o tempo
                use_weighted_fitness=False,  # Não afeta quase nada ~8%
                use_adaptive_rates=True,  # False: Dependendo da taxa fixa de mutação e crossover pode afetar negativamente o tempo quando
                use_bandit_mutation=False,  # True aumenta tempo de execução ~200%
                use_nsga2_survivor_selection=True,  # True aumenta tempo de execução
                use_fitness_sharing=False,  # True aumenta tempo de execução
                crossover_strategy=CrossoverType.MULTI_POINT,
                fidelity_threshold_stop=None
            )
        ]
        phases = farttn_phase + warttn_phase + fartts_phase + fartnt_phase
        #phases = ffrftn_phase
        experiment_configs += [
            ExperimentConfig(
                seed=s,
                phases=phases,
                max_depth=20,
                min_depth=1,
                target_depth=20,
                target_statevector_data=target_sv_data,
                filename_target_circuit=filename,
                resume_from_checkpoint=True,
                allowed_gates=ALLOWED_GATES
            ) for s in range(INITIAL_SEED_EXPERIMENTS, INITIAL_SEED_EXPERIMENTS + NUM_EXPERIMENTS_PER_TARGET)
        ]

    # --- Execução e Análise ---
    manager = ParallelExperimentManager(configs=experiment_configs, max_processes=NUM_EXPERIMENTS_PER_TARGET * NUM_TARGETS)
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
