from pathlib import Path
from typing import List, Tuple

from experiment.config import ExperimentConfig


class ResultFileLocator:
    """
    Descobre automaticamente todos os arquivos de resultado (results.json)
    gerados para um determinado experimento.
    """

    def __init__(self, base_results_dir: Path):
        self._base_dir = base_results_dir
        if not self._base_dir.exists():
            raise FileNotFoundError(f"Results directory not found: {self._base_dir}")

    def locate_for_experiment(self, config: ExperimentConfig) -> List[Path]:
        """
        Dado um ExperimentConfig, retorna os caminhos dos arquivos results.json
        correspondentes a cada phase, em ordem.
        """
        result_paths: List[Path] = []

        for foldername, hash_value in zip(config.get_config_foldername(), config.get_config_hash()):
            phase_dir = self._base_dir / foldername
            result_file = phase_dir / f"{hash_value}_results.json"
            if result_file.exists():
                result_paths.append(result_file)
            else:
                print(f"⚠️ Result file not found for phase: {phase_dir.name}")

        return result_paths

    def locate_all(self) -> List[Path]:
        """
        Varre todo o diretório base em busca de arquivos *_results.json.
        Útil para análises agregadas globais.
        """
        return sorted(self._base_dir.rglob("*_results.json"))

    def summarize_for_experiment(self, config: ExperimentConfig) -> List[Tuple[int, str]]:
        """
        Retorna uma lista de tuplas (phase_index, filepath_str) para debug e visualização.
        """
        summary = []
        for i, result_file in enumerate(self.locate_for_experiment(config)):
            summary.append((i, str(result_file)))
        return summary
