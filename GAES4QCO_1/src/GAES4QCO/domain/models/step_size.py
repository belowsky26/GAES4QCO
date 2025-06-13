
class StepSize:
    def __init__(self, variation: float = 0.5, c: float = 0.9, history_len: int = 5):
        self.mean = 0
        self.variation = variation
        self.c = c
        self.history = []
        self.history_len = history_len

    def __reset_variation(self):
        len_limit = len(self.history) if len(self.history) < self.history_len else self.history_len
        success = sum(self.history[-len_limit:])/len_limit
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