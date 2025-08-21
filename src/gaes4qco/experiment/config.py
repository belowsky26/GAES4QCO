from dataclasses import dataclass, field
from typing import List, Any


@dataclass
class ExperimentConfig:
    """Encapsula todos os parâmetros para uma única execução do GA."""
    seed: int
    num_qubits: int
    max_depth: int
    min_depth: int
    population_size: int
    max_generations: int
    target_statevector_data: List[Any]
    elitism_size: int
    tournament_size: int = 3
    crossover_rate: float = 0.6
    mutation_rate: float = 0.3
    diversity_threshold: float = 0.1  # Limiar de 10%
    injection_rate: float = 0.9  # Injeta 80% quando ativado
    # O nome do arquivo de resultados é derivado da semente
    results_filename: str = field(init=False)
    # O statevector alvo é criado a partir de um label
    target_statevector_label: str = '1'  # Exemplo padrão

    def __post_init__(self):
        self.results_filename = f"results_seed_{self.seed}.json"
