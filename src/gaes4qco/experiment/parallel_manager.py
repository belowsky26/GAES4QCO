import time
from dataclasses import asdict
from multiprocessing import Pool, cpu_count
from typing import List

from containers import ExperimentContainer
from .config import ExperimentConfig
from .runner import ExperimentRunner


class ParallelExperimentManager:
    """Gerencia a execução de múltiplos experimentos em paralelo."""

    def __init__(self, configs: List[ExperimentConfig], max_processes: int):
        self.configs = configs
        self.max_processes = min(max_processes, cpu_count())
        self.experiment_container = ExperimentContainer()

    def run_all(self) -> List[dict]:
        """Executa todos os experimentos configurados usando um pool de processos."""
        num_experiments = len(self.configs)
        num_processes = min(num_experiments, self.max_processes)  # Usa no máximo os CPUs disponíveis

        print(f"Iniciando {num_experiments} experimentos em {num_processes} processos paralelos...")
        start_time = time.time()
        experiments = []
        for i in range(num_experiments):
            config_dict = asdict(self.configs[i])
            self.experiment_container.config.from_dict(config_dict)
            experiments.append(self.experiment_container.runner())

        with Pool(num_processes) as pool:
            # Usa starmap para passar cada objeto de configuração para a função de execução
            results = pool.map(run_experiment, experiments)

        end_time = time.time()
        total_duration = end_time - start_time
        print(f"--- Fim de todos os experimentos | Duração Total: {total_duration:.2f}s ---")

        return results


def run_experiment(runner: ExperimentRunner) -> dict:
    """
    Cria uma instância do container, configura-o e usa-o para
    construir e executar um ExperimentRunner.
    """
    return runner.run()
