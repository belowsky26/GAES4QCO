import time
from multiprocessing import Pool, cpu_count
from typing import List
from .config import ExperimentConfig
from .runner import run_experiment_from_config  # Importa a função standalone


class ParallelExperimentManager:
    """Gerencia a execução de múltiplos experimentos em paralelo."""

    def __init__(self, configs: List[ExperimentConfig], max_processes: int):
        self.configs = configs
        self.max_processes = min(max_processes, cpu_count())

    def run_all(self) -> List[dict]:
        """Executa todos os experimentos configurados usando um pool de processos."""
        num_experiments = len(self.configs)
        num_processes = min(num_experiments, self.max_processes)  # Usa no máximo os CPUs disponíveis

        print(f"Iniciando {num_experiments} experimentos em {num_processes} processos paralelos...")
        start_time = time.time()

        with Pool(num_processes) as pool:
            # Usa starmap para passar cada objeto de configuração para a função de execução
            results = pool.map(run_experiment_from_config, self.configs)

        end_time = time.time()
        total_duration = end_time - start_time
        print(f"--- Fim de todos os experimentos | Duração Total: {total_duration:.2f}s ---")

        return results
