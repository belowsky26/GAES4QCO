from typing import Optional, List, Type, Tuple
from uuid import UUID

from qiskit.circuit import Gate

from .step_size import StepSize
from ..shared.identity import GateComponentId


class GateComponent(GateComponentId):
    def __init__(self, gate_class: Type[Gate], qubits: List[int], parameters: Optional[List[float]], steps_sizes: Optional[List[StepSize]], extra_controls: int = 0, is_inverse: bool = False, _id: UUID = None) -> None:
        super().__init__(_id)
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

    def get_count_qubits(self) -> int:
        return len(self.qubits)
