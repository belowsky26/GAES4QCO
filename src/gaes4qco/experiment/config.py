from dataclasses import dataclass, field, asdict
from typing import List, Any
from pathlib import Path
import json
import hashlib

PROJECT_ROOT = Path(__file__).resolve().parents[3]


@dataclass
class ExperimentConfig:
    """Encapsula todos os parâmetros para uma única execução do GA."""
    seed: int
    use_stepsize: bool
    use_weighted_fitness: bool
    use_adaptive_rates: bool
    use_bandit_mutation: bool
    use_nsga2_survivor_selection: bool
    num_qubits: int
    max_depth: int
    min_depth: int
    target_depth: int
    population_size: int
    max_generations: int
    target_statevector_data: List[Any]
    elitism_size: int
    tournament_size: int = 3
    crossover_rate: float = 0.6  # Para FixedCrossover
    mutation_rate: float = 0.3  # Para FixedMutation
    min_mutation_rate: float = 0.05
    max_mutation_rate: float = 0.5
    min_crossover_rate: float = 0.6
    max_crossover_rate: float = 0.95
    diversity_threshold: float = 0.1  # Limiar de 10%
    injection_rate: float = 0.9  # Injeta 90% quando ativado
    # O nome do arquivo de resultados é derivado da semente
    results_filename: str = field(init=False)

    def get_config_foldername(self) -> str:
        """Gera um nome de pasta descritivo a partir das flags de configuração."""
        fit_flag = "W" if self.use_weighted_fitness else "F"  # Weighted vs Fidelity-only
        rate_flag = "A" if self.use_adaptive_rates else "F"  # Adaptive vs Fixed
        mut_flag = "B" if self.use_bandit_mutation else "R"  # Bandit vs Random
        step_flag = "T" if self.use_stepsize else "F"  # True vs False
        select_survivor_flag = "N" if self.use_nsga2_survivor_selection else "T"
        return f"fit={fit_flag}_rates={rate_flag}_mut={mut_flag}_step={step_flag}_selectsurvior={select_survivor_flag}"

    def get_config_hash(self) -> str:
        """
        Gera um hash SHA256 curto e único para a configuração do experimento.
        """
        # CORREÇÃO: Usa uma cópia de __dict__ em vez de asdict para evitar
        # tentar acessar atributos não inicializados.
        data = self.__dict__.copy()

        # Remove os campos que não devem fazer parte do hash
        data.pop('target_statevector_data', None)
        data.pop('seed', None)
        # A linha "del data['results_filename']" foi removida, pois o atributo
        # não existe no __dict__ neste ponto, e a chamada causaria um KeyError.

        # Converte o dicionário para uma string JSON canônica
        canonical_string = json.dumps(data, sort_keys=True, separators=(',', ':'))

        # Gera o hash SHA256
        hasher = hashlib.sha256(canonical_string.encode('utf-8'))

        return hasher.hexdigest()[:8]

    def __post_init__(self):
        """
        Define o caminho completo para o arquivo de resultado com base
        na configuração do experimento, usando um hash para garantir a unicidade.
        """
        config_folder = self.get_config_foldername()
        config_hash = self.get_config_hash()

        # O novo nome de arquivo combina a seed com o hash da configuração
        basename = f"s{self.seed}_h{config_hash}"

        self.results_filename = str(
            PROJECT_ROOT / "results" / config_folder / f"{basename}.json"
        )

    def to_dict(self) -> dict:
        """Converte a configuração para um dicionário, excluindo dados grandes."""
        data = asdict(self)
        del data['target_statevector_data']
        return data
