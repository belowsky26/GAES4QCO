from typing import Iterator, List
from .gate import Gate


class Column:
    """
    ## Entidade que representa uma coluna (ou 'slice' de tempo) no circuito.
    ## Agrega um conjunto de Gates que são aplicados concorrentemente.
    """
    def __init__(self, gates: List[Gate] = None):
        self.gates = gates if gates is not None else []

    def add_gate(self, gate: Gate):
        self.gates.append(gate)

    def get_gates(self) -> Iterator[Gate]:
        yield from self.gates

    def to_dict(self) -> dict:
        """Converte o objeto Column e seus Gates para um dicionário serializável."""
        return {
            "gates": [gate.to_dict() for gate in self.gates]
        }
