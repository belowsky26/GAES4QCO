import random
from inspect import Parameter, signature
from typing import Type, List, Dict, Tuple

from numpy import pi as PI
from qiskit.circuit import Gate
from qiskit.circuit.library.standard_gates import (
    XGate, YGate, ZGate, HGate, PhaseGate, SwapGate, UGate, RXGate,
    RYGate, RZGate, SGate, SXGate, TGate, IGate, RGate, RXXGate,
    RYYGate, RZXGate, RZZGate, DCXGate, ECRGate,
    RCCXGate, RC3XGate, XXMinusYYGate, XXPlusYYGate
)

from GAES4QCO_1.src.GAES4QCO.domain.models.gate_component import GateComponent
from GAES4QCO_1.src.GAES4QCO.domain.models.step_size import StepSize


class GateFactory:
    """
    Ponto central para obter classes de gate a partir de seus nomes.
    Implementa o padrão de projeto Factory.
    """

    gate_class_map: Dict[int, List[Type[Gate]]] = {
        # --- Gates de 1 Qubit (Pauli e Clifford) ---
        1: [ XGate, YGate, ZGate, HGate, SGate, TGate, IGate,
             SXGate, UGate, PhaseGate, RGate, RXGate, RYGate, RZGate
        ],
        # --- Gates de 2 Qubits (Interação e Troca) ---
        2: [ SwapGate, RXXGate, RYYGate, RZZGate, RZXGate,
             DCXGate, ECRGate, XXMinusYYGate, XXPlusYYGate
        ],
        # --- Gates de 3 Qubits ---
        3: [ RCCXGate ],
        # --- Gates de 4 Qubits ---
        4: [ RC3XGate ]
    }

    inverses_class = [ SGate, SXGate, TGate, DCXGate ]
    gate_without_control = [ IGate ]

    def __init__(self):
        # O mapa é um detalhe de implementação da fábrica.
        pass
    def build_gate_component(self, qubits: List[int], evolutionary_strategies: bool = True) -> GateComponent:
        lim_qubits = len(qubits)
        gate_class, qubits_min = self._choice_gate_class(lim_qubits)
        generated_angles = self._generate_random_params_for_gate(gate_class)
        step_size = [StepSize() for _ in generated_angles] if evolutionary_strategies else None
        chosen_qubits, extra_controls = self._choice_qubits(gate_class, qubits, qubits_min, lim_qubits)
        is_invert = self._choice_inverse_class(gate_class)
        gate_component = GateComponent(gate_class=gate_class, qubits=chosen_qubits,
                                       parameters=generated_angles, steps_sizes=step_size, extra_controls=extra_controls, is_invert=is_invert)
        return gate_component

    @classmethod
    def _choice_inverse_class(cls, gate_class: Type[Gate]) -> bool:
        if gate_class in cls.inverses_class:
            choice = random.choice([False, True])
            return choice
        return False

    @classmethod
    def _choice_gate_class(cls, lim_qubits: int) -> Tuple[Type[Gate], int]:
        candidate_pool:List[Tuple[Type[Gate], int]] = [
            (gate_class, num_qubits)  # <-- Mudança aqui: armazenamos a tupla
            for num_qubits, gate_list in cls.gate_class_map.items()
            if num_qubits <= lim_qubits
            for gate_class in gate_list
        ]
        chosen_gate_tuple = random.choice(candidate_pool)
        return chosen_gate_tuple

    @classmethod
    def _choice_qubits(cls, gate_class: Type[Gate], qubits: List[int], min_qubits: int, lim_qubits: int) -> Tuple[List[int], int]:
        dif_qubits = lim_qubits - min_qubits
        control_qubits = random.randint(0, dif_qubits) if not gate_class in cls.gate_without_control else 0
        chosen_qubits = random.sample(qubits, min_qubits + control_qubits)
        return chosen_qubits, control_qubits

    @classmethod
    def _generate_random_params_for_gate(cls, gate_class: Type[Gate]) -> List[float]:
        """Gera parâmetros aleatórios com base na assinatura da classe."""
        sig = signature(gate_class.__init__)
        target_annotation = {
            "ParameterValueType",
            "typing.Union[qiskit.circuit.parameterexpression.ParameterExpression, float]"
        }

        generated_angles = [
            random.uniform(0, PI) if p.name == "theta" else random.uniform(0, 2 * PI)
            for p in sig.parameters.values()
            if p.name != 'self' and p.default is Parameter.empty and str(p.annotation) in target_annotation
        ]

        return generated_angles