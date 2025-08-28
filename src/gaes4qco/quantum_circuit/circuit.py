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
            fidelity: float = 0.0,
            apply_evolutionary_strategy: bool = False
    ):
        self.count_qubits = count_qubits
        self.columns = columns
        self.fitness = fitness
        self.fidelity = fidelity
        self.apply_evolutionary_strategy = apply_evolutionary_strategy
        self._structural_representation: Set[Tuple] = set()

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
            "columns": [col.to_dict() for col in self.columns]
        }
