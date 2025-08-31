from abc import ABC, abstractmethod

from quantum_circuit.circuit import Circuit
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


class IMutationPopulation(ABC):
    @abstractmethod
    def mutate(self, population: Population) -> Population:
        """
        ## Recebe uma população e retorna uma nova população com mutações aplicadas.
        """
        pass


class IMutationStrategy(ABC):
    """
    ## Interface para estratégias de mutação.
    """
    @abstractmethod
    def mutate_individual(self, individual: Circuit) -> Circuit:
        """
        ## Recebe uma população e retorna uma nova população com mutações aplicadas.
        """
        pass

    @abstractmethod
    def can_apply(self, individual: Circuit) -> bool:
        """
        ## Recebe um circuito e diz se essa mutação é capaz de ser executada
        """
        pass
