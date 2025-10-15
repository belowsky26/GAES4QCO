# src/analysis/result_concatenator.py

import json
from pathlib import Path
from typing import List

from experiment.test_loader import TestConfigLoader
from experiment.config import ExperimentConfig
from analysis.result_file_locator import ResultFileLocator
from analysis.loader import JsonDataLoader
from analysis.data_models import ResultData


class JsonResultConcatenator:
    """
    Combina os resultados de múltiplas phases de um mesmo experimento em um único JSON.
    """

    def __init__(self, tests_dir: Path, results_dir: Path):
        self.tests_dir = tests_dir
        self.results_dir = results_dir

        self.loader = TestConfigLoader(self.tests_dir)
        self.locator = ResultFileLocator(self.results_dir)
        self.data_loader = JsonDataLoader()

        self.output_dir = self.results_dir / "concatenated"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _concat_result_data(self, result_data_list: List[ResultData]) -> ResultData:
        """
        Concatena dados de várias phases em um único ResultData contínuo.
        """
        fitness_all = []
        avg_all = []
        std_all = []
        diversity_all = []

        for rd in result_data_list:
            fitness_all.extend(rd.fitness_per_generation)
            avg_all.extend(rd.average_fitness_per_generation)
            std_all.extend(rd.std_dev_fitness_per_generation)
            diversity_all.extend(rd.structural_diversity_per_generation)

        return ResultData(
            fitness_per_generation=fitness_all,
            average_fitness_per_generation=avg_all,
            std_dev_fitness_per_generation=std_all,
            structural_diversity_per_generation=diversity_all
        )

    def process_single_test(self, config: ExperimentConfig, test_filename: str) -> Path:
        """
        Gera um único arquivo concatenado para um test.json específico.
        """
        result_files = self.locator.locate_for_experiment(config)
        if not result_files:
            print(f"⚠️ Nenhum resultado encontrado para {test_filename}")
            return None

        print(f"🔗 Concatenando {len(result_files)} fases para {test_filename}...")

        # Carrega todos os dados
        result_data_list = [self.data_loader.load(str(f)) for f in result_files]

        # Concatena
        concatenated = self._concat_result_data(result_data_list)

        # Salva em um novo arquivo
        output_path = self.output_dir / f"{test_filename.replace('.json', '')}_concatenated_result.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump({
                "fitness_per_generation": concatenated.fitness_per_generation,
                "average_fitness_per_generation": concatenated.average_fitness_per_generation,
                "std_dev_fitness_per_generation": concatenated.std_dev_fitness_per_generation,
                "structural_diversity_per_generation": concatenated.structural_diversity_per_generation
            }, f, indent=4)

        print(f"✅ Resultado concatenado salvo em: {output_path.name}")
        return output_path

    def process_all_tests(self) -> List[Path]:
        """
        Processa todos os arquivos de teste encontrados no diretório `tests/`
        e retorna a lista de caminhos dos arquivos concatenados gerados.
        """
        experiment_configs, filenames = self.loader.load_all()
        concatenated_paths = []

        for cfg, fname in zip(experiment_configs, filenames):
            path = self.process_single_test(cfg, fname)
            if path:
                concatenated_paths.append(path)

        print(f"\n📦 {len(concatenated_paths)} arquivos concatenados gerados com sucesso.")
        return concatenated_paths
