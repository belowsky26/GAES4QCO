from ..models.circuit.step_size import StepSize


class StepSizeBuilder:
    """
    Constrói instâncias de StepSize com base em parâmetros de configuração.
    """
    def __init__(self, initial_variation: float, c_factor: float, history_len: int):
        # Os parâmetros são injetados a partir da configuração geral do algoritmo
        self.initial_variation = initial_variation
        self.c_factor = c_factor
        self.history_len = history_len

    def build(self) -> StepSize:
        """
        Cria e retorna uma nova instância de StepSize.
        """
        return StepSize(
            variation=self.initial_variation,
            c=self.c_factor,
            history_len=self.history_len
        )