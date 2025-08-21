from abc import ABC, abstractmethod
from .population import Population           # Importamos nossa classe Population


class ISelectionStrategy(ABC):
    """
    ## Interface para estratégias que selecionam uma sub-população
    ## a partir de uma população existente (ex: seleção de pais).
    """
    @abstractmethod
    def select(self, population: Population) -> Population:
        """Recebe uma população e retorna uma nova população selecionada."""
        pass


class ICrossoverStrategy(ABC):
    """
    ## Interface para estratégias de cruzamento.
    """
    @abstractmethod
    def crossover(self, parent_population: Population) -> Population:
        """
        ## Recebe uma população de pais e retorna uma nova população de filhos.
        """
        pass


class IMutationStrategy(ABC):
    """
    ## Interface para estratégias de mutação.
    """
    @abstractmethod
    def mutate(self, population: Population) -> Population:
        """
        ## Recebe uma população e retorna uma nova população com mutações aplicadas.
        """
        pass
