import json
from pathlib import Path
from qiskit.quantum_info import Statevector

from containers import QuantumCircuitContainer
from experiment.config import ExperimentConfig
from containers import AppContainer
from quantum_circuit.circuit_factory import GateFactory, CircuitFactory
from quantum_circuit.qiskit_adapter import QiskitAdapter


def main():
    """
    Carrega um circuito salvo (alvo ou otimizado) e calcula sua taxa de erro
    em um simulador com ruído.
    """
    # --- Configuração ---
    CIRCUIT_TO_TEST_PATH = r"/home/LuizMFL/Projects/GAES4QCO/results/target_circuits/target_seed_101.json"
    circuit_optimized_path = r"/home/LuizMFL/Projects/GAES4QCO/results/pha=0_FD_si_to_to_FX_BD_ST_NL/8791165d_circuits/rank_000_fit_0.9374_depth_20.json"
    SHOTS = 2**20
    container = AppContainer()
    container.config.from_dict({
        "num_qubits": 4
    })
    quantum_circuit_container = container.circuit()
    circuit_factory = quantum_circuit_container.circuit_factory()
    error_analyzer = container.error_analyzer()

    print(f"Analisando o circuito: {CIRCUIT_TO_TEST_PATH}")

    with open(CIRCUIT_TO_TEST_PATH, "r") as f:
        circuit_data = json.load(f)
    with open(circuit_optimized_path, "r") as f:
        circuit_optimized_data = json.load(f)

    circuit_target_domain = circuit_factory.create_from_dict(circuit_data)
    adapter = quantum_circuit_container.qiskit_adapter()
    circuit_target = adapter.from_domain(circuit_target_domain)
    statevector_target = Statevector.from_instruction(circuit_target)

    error = error_analyzer.calculate_error_rate(
        circuit=circuit_target_domain,
        target_statevector=statevector_target,
        shots=SHOTS
    )
    print(f"Alvo Error: {error}")

    circuit_target_domain = circuit_factory.create_from_dict(circuit_optimized_data)
    error_optimized = error_analyzer.calculate_error_rate(
        circuit=circuit_target_domain,
        target_statevector=statevector_target,
        shots=SHOTS
    )
    print(f"Optimized Error: {error_optimized}")

    print(f"O novo circuito tem menos erro que o antigo? {error_optimized < error} ")
    print(f"O novo circuito tem erro igual ao antigo? {error_optimized == error} ")


if __name__ == "__main__":
    main()
