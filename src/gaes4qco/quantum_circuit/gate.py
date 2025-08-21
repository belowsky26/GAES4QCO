from typing import Optional, List, Type
from qiskit.circuit import Gate as QiskitGate  # ## Renomeado para evitar conflito
from shared.value_objects import StepSize


class Gate:
    """
    ## Entidade que representa um gate em nosso domínio.
    ## Não possui mais o método .build() para não depender diretamente do Qiskit.
    ## A responsabilidade de 'construir' um gate do Qiskit é do Adapter.
    """
    def __init__(
        self,
        gate_class: Type[QiskitGate],  # ## A referência à classe do Qiskit é mantida como dado.
        qubits: List[int],
        parameters: Optional[List[float]] = None,
        steps_sizes: Optional[List[StepSize]] = None,
        extra_controls: int = 0,
        is_inverse: bool = False
    ) -> None:
        self.gate_class = gate_class
        self.qubits = qubits
        self.parameters = parameters if parameters is not None else []
        self.steps_sizes = steps_sizes if steps_sizes is not None else []
        self.extra_controls = extra_controls
        self.is_inverse = is_inverse

    def __eq__(self, other):
        if not isinstance(other, Gate):
            return False
        return (self.gate_class == other.gate_class and
                self.parameters == other.parameters and
                self.qubits == other.qubits and
                self.steps_sizes == other.steps_sizes and
                self.extra_controls == other.extra_controls and
                self.is_inverse == other.is_inverse)

    def to_dict(self) -> dict:
        """Converte o objeto Gate para um dicionário serializável."""
        return {
            "gate_class_name": self.gate_class.__name__,
            "qubits": self.qubits,
            "parameters": self.parameters,
            "step_sizes": [ss.to_dict() for ss in self.steps_sizes],
            "extra_controls": self.extra_controls,
            "is_inverse": self.is_inverse,
        }
