import json
from .interfaces import IDataLoader
from .data_models import ResultData


class JsonDataLoader(IDataLoader):
    """Carrega dados de resultado de um arquivo JSON."""

    def load(self, filepath: str) -> ResultData:
        print(f"Carregando dados de {filepath}...")
        with open(filepath, 'r') as f:
            data = json.load(f)

        return ResultData(
            fitness_per_generation=data["fitness_per_generation"],
            average_fitness_per_generation=data["average_fitness_per_generation"],
            std_dev_fitness_per_generation=data["std_dev_fitness_per_generation"],
            structural_diversity_per_generation=data["structural_diversity_per_generation"]
        )
