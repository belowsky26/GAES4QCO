from abc import ABC, abstractmethod
from qiskit.circuit import QuantumCircuit as QiskitCircuit # ## Tipo de retorno do Qiskit
from .circuit import Circuit # ## Nossa entidade de domínio

class IQuantumCircuitAdapter(ABC):
    """
    ## Interface que define o contrato para a conversão e execução
    ## de nossos Circuitos de domínio em qualquer backend quântico.
    """
    @abstractmethod
    def from_domain(self, circuit: Circuit) -> QiskitCircuit:
        """Converte nossa entidade Circuit para um objeto do backend (Qiskit)."""
        pass