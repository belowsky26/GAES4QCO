from enum import Enum
from typing import List


class StepSize:
    """
    ## Representa os parâmetros para a Estratégia Evolucionária de um gate.
    ## É um objeto de valor (Value Object) puro, contendo apenas estado.
    ## A lógica que o modifica foi removida para respeitar a Responsabilidade Única.
    """
    def __init__(self, variation: float = 0.5, c: float = 0.9, history_len: int = 5, history: List[int] = None, mean: float = 0.0):
        self.variation = variation
        self.c: float = c
        self.history_len: int = history_len
        # O histórico e a média são estados de tempo de execução, podem ser inicializados em outro lugar.
        self.history: list[int] = history if history else []
        self.mean: float = mean

    def __eq__(self, other):
        if not isinstance(other, StepSize):
            return False
        return (self.variation == other.variation and
                self.c == other.c and
                self.history_len == other.history_len)

    def to_dict(self):
        return {
            "variation": self.variation,
            "c": self.c,
            "history_len": self.history_len,
            "history": self.history,
            "mean": self.mean,
        }

    def copy(self) -> "StepSize":
        """
        Return a lightweight copy of the StepSize instance.
        """
        return StepSize(
            variation=self.variation,
            c=self.c,
            history_len=self.history_len,
            history=list(self.history),
            mean=self.mean
        )


class CrossoverType(str, Enum):
    """Define os tipos de estratégias de crossover disponíveis."""
    MULTI_POINT = "multipoint"
    SINGLE_POINT = "singlepoint"
    BLOCKWISE = "blockwise"
    # Adicionando um para o futuro seletor adaptativo
    ADAPTIVE_BANDIT = "bandit"
    RANDOM = "random"
