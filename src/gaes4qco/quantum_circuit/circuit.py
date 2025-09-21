from typing import List, Set, Tuple
from .column import Column


class Circuit:
    """
    ## Entidade principal do domínio, representa um circuito quântico.
    ## É um objeto de domínio puro, sem dependências de Qiskit.
    ## Os métodos 'build' e 'gen_random_circuit' foram movidos para o Adapter e a Factory.
    """

    def __init__(
            self,
            count_qubits: int,
            columns: List[Column],
            fitness: float = 0.0,
            fidelity: float = 0.0
    ):
        self.count_qubits = count_qubits
        self.columns = columns
        self.fitness = fitness
        self.fidelity = fidelity

        self.rank: int = -1  # Rank da Fronteira de Pareto
        self.crowding_distance: float = 0.0  # Distância de multidão para desempate

        self._structural_representation: Set[Tuple] = set()

    @property
    def objectives(self) -> Tuple[float, ...]:
        """
        Retorna a tupla de objetivos para a otimização multiobjetivo.
        Objetivo 1: Maximizar a Fidelidade (ou o fitness ponderado).
        Objetivo 2: Maximizar a Profundidade Negativa (ou seja, Minimizar a Profundidade).
        """
        return self.fidelity, -float(self.depth)

    @property
    def depth(self) -> int:
        return len(self.columns)

    def get_structural_representation(self) -> Set[Tuple]:
        """
        Cria uma representação única da estrutura do circuito, ignorando parâmetros.
        O resultado é um conjunto de tuplas, onde cada tupla representa um gate.
        Ex: {('HGate', (0,)), ('CXGate', (0, 1)), ...}
        """
        if self._structural_representation:
            return self._structural_representation

        representation = set()
        for i_col, col in enumerate(self.columns):
            for gate in col.get_gates():
                # Normaliza os qubits para a ordem ser irrelevante
                qubits_tuple = tuple(sorted(gate.qubits))
                params_tuple = tuple(round(p, 6) for p in gate.parameters)
                gene = (
                    gate.gate_class.__name__,
                    qubits_tuple,
                    params_tuple,
                    gate.extra_controls,
                    gate.is_inverse,
                    i_col
                )
                representation.add(gene)

        self._structural_representation = set(sorted(list(representation)))
        return self._structural_representation

    def to_dict(self) -> dict:
        """Converte o objeto Circuit e seus componentes para um dicionário serializável."""
        return {
            "count_qubits": self.count_qubits,
            "depth": self.depth,
            "fitness": self.fitness,
            "fidelity": self.fidelity,
            "nsga2_rank": self.rank,  # Adiciona os novos campos para depuração
            "nsga2_crowding_distance": self.crowding_distance,
            "columns": [col.to_dict() for col in self.columns]
        }

    def copy(self) -> "Circuit":
        """
        Return a lightweight copy of the Circuit instance with copied columns.
        Copies all Columns and their Gates, preserving the circuit's integrity.
        Does not copy _structural_representation cache, as it will be recalculated when needed.
        """
        return Circuit(
            count_qubits=self.count_qubits,
            columns=[col.copy() for col in self.columns],
            fitness=self.fitness,
            fidelity=self.fidelity
        )
