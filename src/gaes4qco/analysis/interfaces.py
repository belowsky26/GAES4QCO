from abc import ABC, abstractmethod

from quantum_circuit.circuit import Circuit
from .data_models import ResultData


class IDataLoader(ABC):
    """Interface para classes que carregam dados de resultado."""
    @abstractmethod
    def load(self, filepath: str) -> ResultData:
        """Carrega os dados de um arquivo e retorna um objeto ResultData."""
        pass


class IPlotter(ABC):
    """Interface para classes que geram gráficos a partir de dados de resultado."""
    @abstractmethod
    def plot(self, data: ResultData, output_path: str):
        """Gera e salva um gráfico a partir de um objeto ResultData."""
        pass

class IDistanceMetric(ABC):

    @staticmethod
    def calculate(ind1: Circuit, ind2: Circuit) -> float:
        """Calcula a distância entre dois indivíduos."""
        pass
