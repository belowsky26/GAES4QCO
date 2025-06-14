import uuid
from typing import Any


# --- 1. A Classe Base Genérica ---
# Ela contém toda a lógica comum para qualquer ID de agregado.
class AggregateId:
    """
    Classe base para todos os identificadores de Agregado.
    Usa UUIDs para garantir unicidade. É um Objeto de Valor imutável.
    """
    def __init__(self, value: uuid.UUID = None):
        # Se nenhum valor for fornecido, gera um novo UUID único.
        # Isso facilita a criação de novas entidades.
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
# Elas herdam toda a funcionalidade e servem apenas para dar um tipo distinto a cada ID.

class CircuitId(AggregateId):
    """Identificador único para um Agregado Circuit."""
    pass


class GenerationId(AggregateId):
    """Identificador único para um Agregado Generation."""
    pass


class ContextId(AggregateId):
    """Identificador único para um Agregado ChannelContext."""
    pass


# E qualquer outro ID que você precisar...
# class PopulationId(AggregateId): # Se População fosse um agregado
#     pass