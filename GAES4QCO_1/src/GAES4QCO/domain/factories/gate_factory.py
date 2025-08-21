import random
from typing import Type, List, Dict, Tuple
from qiskit.circuit import Gate
from qiskit.circuit.library.standard_gates import (
    XGate, YGate, ZGate, HGate, PhaseGate, SwapGate, UGate, RXGate,
    RYGate, RZGate, SGate, SXGate, TGate, IGate, RGate, RXXGate,
    RYYGate, RZXGate, RZZGate, DCXGate, ECRGate,
    RCCXGate, RC3XGate, XXMinusYYGate, XXPlusYYGate
)


class GateFactory:
    def __init__(self):
        self._qubit_map: Dict[int, List[Type[Gate]]] = {
            # --- Gates de 1 Qubit (Pauli e Clifford) ---
            1: [XGate, YGate, ZGate, HGate, SGate, TGate, IGate,
                SXGate, UGate, PhaseGate, RGate, RXGate, RYGate, RZGate
                ],
            # --- Gates de 2 Qubits (Interação e Troca) ---
            2: [SwapGate, RXXGate, RYYGate, RZZGate, RZXGate,
                DCXGate, ECRGate, XXMinusYYGate, XXPlusYYGate
                ],
            # --- Gates de 3 Qubits ---
            3: [RCCXGate],
            # --- Gates de 4 Qubits ---
            4: [RC3XGate]
        }

        # Listas de regras, como você definiu
        self._inversible_classes = {SGate, SXGate, TGate, DCXGate}
        self._uncontrollable_gates = {IGate}  # Usar um set é mais rápido para lookups

    def choice_gate_class(self, max_qubits: int) -> Tuple[Type[Gate], int]:
        """Sorteia uma tupla (gate_class, num_qubits) que respeita o limite."""
        candidate_pool = [
            (gate_class, num_qubits)
            for num_qubits, gate_list in self._qubit_map.items()
            if num_qubits <= max_qubits
            for gate_class in gate_list
        ]
        if not candidate_pool:
            raise ValueError(f"Não há gates disponíveis que usem {max_qubits} ou menos qubits.")
        return random.choice(candidate_pool)

    def can_be_inverted_to_new_gate(self, gate_class: Type[Gate]) -> bool:
        """Verifica se um gate está na lista de inversíveis que geram outra classe."""
        return gate_class in self._inversible_classes

    def can_be_controlled(self, gate_class: Type[Gate]) -> bool:
        """Verifica se um gate pode ter controles adicionados."""
        return gate_class not in self._uncontrollable_gates