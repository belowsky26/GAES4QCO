import uuid
from typing import Any

# --- 1. A Classe Base Genérica (sem alterações) ---
class AggregateId:
    """
    Classe base para todos os identificadores de Agregado e Entidade.
    Usa UUIDs para garantir unicidade. É um Objeto de Valor imutável.
    """
    def __init__(self, value: uuid.UUID = None):
        self._value = value or uuid.uuid4()

    @property
    def value(self) -> uuid.UUID:
        """Propriedade somente leitura para garantir a imutabilidade."""
        return self._value

    def __eq__(self, other: Any) -> bool:
        """Dois IDs são iguais se forem da mesma classe e tiverem o mesmo valor UUID."""
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self._value == other._value

    def __hash__(self) -> int:
        """O hash é baseado no valor do UUID."""
        return hash(self._value)

    def __str__(self) -> str:
        """Representação em string do ID."""
        return str(self._value)

    def __repr__(self) -> str:
        """Representação para desenvolvedores, útil para depuração."""
        return f"{self.__class__.__name__}('{self._value}')"


# --- 2. As Classes Específicas de ID ---

class CircuitId(AggregateId):
    """Identificador único para um Agregado Circuit."""
    pass

class GenerationId(AggregateId):
    """Identificador único para um Agregado Generation."""
    pass

class ColumnComponentId(AggregateId):
    """Identificador único para uma Entidade ColumnComponent."""
    pass

class GateComponentId(AggregateId):
    """Identificador único para uma Entidade GateComponent."""
    pass

# --- NOVA CLASSE ADICIONADA ---
class StepSizeId(AggregateId):
    """Identificador único para uma Entidade StepSize."""
    pass