from typing import Optional, List, Type, Tuple

from qiskit.circuit import Gate
from qiskit.circuit.library.standard_gates import XGate, YGate, ZGate, HGate, PhaseGate, SwapGate, UGate, RXGate, RYGate, RZGate, U1Gate, U3Gate, SGate, SXGate, TGate, IGate, U2Gate, RGate, RXXGate, RYYGate, RZXGate, RZZGate, DCXGate, XXMinusYYGate, XXPlusYYGate, RC3XGate, RCCXGate, ECRGate

# gate.control e Inverse() geram novas gates definidas no standard
from qiskit.circuit.library.standard_gates import SGate, SXGate

# gates que usam inverse() e geram gates definidas
from qiskit.circuit.library.standard_gates import TGate, RC3XGate, RCCXGate, DCXGate

# gates que usam control() e geram gates definidas
from qiskit.circuit.library.standard_gates import XGate, YGate, ZGate, HGate, PhaseGate, SwapGate, UGate, RXGate, RYGate, RZGate, U1Gate, U3Gate

# Gates que não viram outra gate já definida com .control(x) ou .inverse()
from qiskit.circuit.library.standard_gates import IGate, U2Gate, RGate, RXXGate, RYYGate, RZXGate, RZZGate, XXMinusYYGate, XXPlusYYGate, ECRGate


from GAES4QCO_1.src.GAES4QCO.domain.models.step_size import StepSize


class GateComponent:
    def __init__(self, gate_class: Type[Gate], qubits: List[int], parameters: Optional[List[float]], steps_sizes: Optional[List[StepSize]], extra_controls: int = 0, is_inverse: bool = False) -> None:
        self.gate_class = gate_class
        self.qubits = qubits
        self.parameters = parameters
        self.steps_sizes = steps_sizes
        self.extra_controls = extra_controls
        self.is_inverse = is_inverse

    def build(self) -> Tuple[Gate, List[int]]:
        """
        Cria uma instância completa e configurada de GateComponent.
        """
        gate = self.gate_class(*self.parameters)
        if self.extra_controls > 0:
            gate = gate.control(self.extra_controls)
        if self.is_inverse:
            gate = gate.inverse()
        return gate, self.qubits

    def __eq__(self, other):
        if not isinstance(other, GateComponent):
            return False

        # Compara todos os atributos relevantes
        return (self.gate_class == other.gate_class
                and self.parameters == other.parameters
                and self.qubits == other.qubits
                and self.steps_sizes == other.steps_sizes
                and self.extra_controls == other.extra_controls
                and self.is_inverse == other.is_inverse)