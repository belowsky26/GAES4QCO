import random
from typing import List
from .circuit import Circuit
from .column import Column
from .gate_factory import GateFactory  # <-- Importa a nova factory


class CircuitFactory:
    """
    Responsável por criar instâncias da nossa entidade Circuit,
    delegando a criação de gates para a GateFactory.
    """

    def __init__(self, gate_factory: GateFactory, use_evolutionary_strategy: bool):
        # A CircuitFactory agora tem uma instância da GateFactory.
        self._gate_factory = gate_factory
        self.use_evolutionary_strategy = use_evolutionary_strategy

    def create_random_circuit(self, num_qubits: int, max_depth: int, min_depth: int) -> Circuit:
        depth = random.randint(min_depth, max_depth)
        columns: List[Column] = []

        for _ in range(depth):
            qubits_free_in_column = list(range(num_qubits))
            gates_in_column = []

            # Preenche a coluna com gates até não haver mais qubits livres
            while qubits_free_in_column:
                try:
                    # Delega a criação do gate para a GateFactory
                    new_gate = self._gate_factory.build_gate(qubits_free_in_column, self.use_evolutionary_strategy)
                    gates_in_column.append(new_gate)

                    # Remove os qubits usados da lista de disponíveis na coluna
                    for used_qubit in new_gate.qubits:
                        qubits_free_in_column.remove(used_qubit)
                except ValueError:
                    # Ocorre se não for possível criar mais gates com os qubits restantes
                    break

            columns.append(Column(gates=gates_in_column))

        return Circuit(count_qubits=num_qubits, columns=columns)
