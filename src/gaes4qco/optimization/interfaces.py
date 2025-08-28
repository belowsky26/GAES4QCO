from abc import ABC, abstractmethod
from typing import Tuple

from quantum_circuit.circuit import Circuit
from evolutionary_algorithm.population import Population


class IFitnessEvaluator(ABC):
    """Interface para qualquer classe que calcula o fitness de um circuito."""

    @abstractmethod
    def evaluate(self, circuit: Circuit) -> Tuple[float, float]:
        """Calcula e retorna o valor de fitness de um único circuito."""
        pass


class IProgressObserver(ABC):
    """Interface para classes que observam e registram o progresso do algoritmo."""

    @abstractmethod
    def update(self, generation: int, population: Population):
        """Método chamado a cada geração para registrar o estado da população."""
        pass

    @abstractmethod
    def save(self):
        """Salva os dados coletados ao final da execução."""
        pass
