# FONT-CODE: src/GAES4QCO/step_size/step_size_model.py

from collections import deque
from typing import Deque
from uuid import UUID

# Importa a interface que acabamos de criar
from .step_size_interface import IStepSize

# Importa o ID da camada compartilhada
from ..shared.identity import StepSizeId


# A classe agora herda da interface IStepSize e da sua classe de ID
class StepSize(IStepSize, StepSizeId):

    def __init__(self, variation: float, c: float, history_len: int, _id: UUID = None):
        super().__init__(_id)
        self._variation = variation  # Atributo agora é privado
        self._c = c  # Atributo agora é privado
        self._history = deque(maxlen=history_len)
        self._history_len = history_len

    @property
    def variation(self) -> float:
        """Implementação da propriedade abstrata 'variation'."""
        return self._variation

    @property
    def history(self) -> Deque[int]:
        """Implementação da propriedade abstrata 'history'."""
        return self._history

    @property
    def c(self) -> float:
        return self._c

    @property
    def history_len(self) -> int:
        return self._history_len

    def __reset_variation(self):
        success_rate = sum(self.history) / len(self.history)
        threshold = 1.0 / self.history_len

        if success_rate > threshold:
            self._variation /= self._c
        elif success_rate < threshold:
            self._variation *= self._c

    def add_hit(self, hit: bool) -> None:
        """Implementação do método abstrato 'add_hit'."""
        self._history.append(int(hit))
        self.__reset_variation()

    def __eq__(self, other):
        if not isinstance(other, StepSize):
            return NotImplemented

        return super().__eq__(other)