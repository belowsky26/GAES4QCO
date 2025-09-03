from dataclasses import dataclass, field, asdict
from typing import List, Any, Optional, Generator
from pathlib import Path
import json
import hashlib

PROJECT_ROOT = Path(__file__).resolve().parents[3]


@dataclass
class PhaseConfig:
    """Configuração para uma única fase da otimização."""
    use_stepsize: bool
    use_weighted_fitness: bool
    use_adaptive_rates: bool
    use_bandit_mutation: bool
    use_nsga2_survivor_selection: bool
    use_fitness_sharing: bool
    generations: int
    # Condição de parada opcional para a fase
    fidelity_threshold_stop: Optional[float]


@dataclass
class ExperimentConfig:
    """Encapsula todos os parâmetros para uma única execução do GA."""
    seed: int
    max_depth: int
    min_depth: int
    target_depth: int
    target_statevector_data: List[Any]
    filename_target_circuit: str
    phases: List[PhaseConfig]
    resume_from_checkpoint: bool
    num_qubits: int = 4
    elitism_size: int = 10
    population_size: int = 200
    tournament_size: int = 2
    crossover_rate: float = 0.6  # Para FixedCrossover
    mutation_rate: float = 0.3  # Para FixedMutation
    min_mutation_rate: float = 0.2
    max_mutation_rate: float = 0.5
    min_crossover_rate: float = 0.6
    max_crossover_rate: float = 0.95
    diversity_threshold: float = 0.15  # Limiar de 10%
    injection_rate: float = 0.15  # Injeta 90% quando ativado
    sharing_radius: float = 0.4
    alpha: float = 1.0
    # O nome do arquivo de resultados é derivado da semente
    # results_filename: str = field(init=False)

    def get_config_foldername(self) -> Generator[str, Any, None]:
        """Gera um nome de pasta descritivo a partir das flags de configuração."""
        for i, phase in enumerate(self.phases):
            fit_flag = "W" if phase.use_weighted_fitness else "F"  # Weighted vs Fidelity-only
            rate_flag = "A" if phase.use_adaptive_rates else "F"  # Adaptive vs Fixed
            mut_flag = "B" if phase.use_bandit_mutation else "R"  # Bandit vs Random
            step_flag = "T" if phase.use_stepsize else "F"  # True vs False
            select_survivor_flag = "N" if phase.use_nsga2_survivor_selection else "T"
            yield f"pha={i}_fit={fit_flag}_rates={rate_flag}_mut={mut_flag}_step={step_flag}_selectsurvior={select_survivor_flag}"

    def get_config_hash(self) -> Generator[str, Any, None]:
        """
        Gera um hash SHA256 curto e único para a configuração do experimento.
        """
        data = asdict(self).copy()
        data.pop("target_statevector_data", None)
        data.pop("resume_from_checkpoint", None)
        for i in range(1, len(self.phases) + 1):
            data_final = data.copy()
            data_final["phases"] = data_final["phases"][:i]
            canonical_string = json.dumps(data_final, sort_keys=True, separators=(",", ":"), default=lambda o: o.__dict__)
            hasher = hashlib.sha256(canonical_string.encode("utf-8"))
            yield hasher.hexdigest()[:15]

    @property
    def config_file_path(self) -> Generator[str, Any, None]:
        folder_path = PROJECT_ROOT / "results"
        for i, (config_foldername, config_hash) in enumerate(zip(self.get_config_foldername(), self.get_config_hash())):
            folder_path = folder_path / config_foldername
            yield str(folder_path / f"{config_hash}_config.json")

    def to_dict(self) -> dict:
        """Converte a configuração para um dicionário, excluindo dados grandes."""
        data = asdict(self)
        del data["target_statevector_data"]
        del data["resume_from_checkpoint"]
        del data["phases"]
        data.pop("config_file_path", None)
        return data
