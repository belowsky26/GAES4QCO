from collections import deque
from uuid import UUID

from ..shared.identity import StepSizeId


class StepSize(StepSizeId):
    def __init__(self, variation: float, c: float, history_len: int, _id: UUID = None):
        super().__init__(_id)
        self.mean = 0
        self.variation = variation
        self.c = c
        self.history = deque(maxlen=history_len)
        self.history_len = history_len

    def __reset_variation(self):
        success = sum(self.history)/len(self.history)
        if success > 1/self.history_len:
            self.variation /= self.c
        elif success < 1/self.history_len:
            self.variation *= self.c
            
    def add_hit(self, hit:bool):
        self.history.append(int(hit))
        self.__reset_variation()

    def __eq__(self, other):
        if not isinstance(other, StepSize):
            return False

        return (self.mean == other.mean
                and self.variation == other.variation
                and self.c == other.c
                and self.history == other.history
                and self.history_len == other.history_len)