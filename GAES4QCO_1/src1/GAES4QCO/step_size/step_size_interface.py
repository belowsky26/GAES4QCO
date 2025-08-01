from abc import ABC, abstractmethod
from typing import Deque


class IStepSize(ABC):
    """
    Define o contrato para um componente de Step Size adaptativo.
    Qualquer classe que implemente esta interface deve fornecer a lógica
    para ajustar sua variação com base em um histórico de sucessos.
    """

    @property
    @abstractmethod
    def variation(self) -> float:
        """A variação atual do step size, usada na mutação."""
        pass

    @property
    @abstractmethod
    def history(self) -> Deque[int]:
        """O histórico de sucessos recentes."""
        pass

    @property
    @abstractmethod
    def c(self) -> float:
        """O histórico de sucessos recentes."""
        pass

    @property
    @abstractmethod
    def history_len(self) ->int:
        """O histórico de sucessos recentes."""
        pass

    @abstractmethod
    def add_hit(self, hit: bool) -> None:
        """
        Adiciona um resultado (sucesso ou falha) ao histórico e
        aciona a lógica para reajustar a variação.
        """
        pass