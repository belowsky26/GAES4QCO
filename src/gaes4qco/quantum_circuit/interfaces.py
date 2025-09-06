from abc import ABC, abstractmethod
from typing import Dict

from qiskit.circuit import QuantumCircuit as QiskitCircuit
from .circuit import Circuit


class IQuantumCircuitAdapter(ABC):
    """
    ## Interface que define o contrato para a conversão e execução
    ## de nossos Circuitos de domínio em qualquer backend quântico.
    """
    @abstractmethod
    def from_domain(self, circuit: Circuit) -> QiskitCircuit:
        """Converte nossa entidade Circuit para um objeto do backend (Qiskit)."""
        pass


class IQuantumExecutor(ABC):
    """Interface para classes que executam um circuito quântico e retornam os resultados."""
    @abstractmethod
    def execute(self, circuit: Circuit, shots: int, measure: bool) -> Dict[str, int]:
        """
        Executa um circuito por um número de 'shots' (medições) e retorna
        a contagem de resultados (ex: {'001': 512, '101': 488}).
        """
        pass
