from .population import Population
from quantum_circuit.circuit_factory import CircuitFactory


class PopulationFactory:
    """
    Responsável por criar uma instância de Population com indivíduos
    gerados aleatoriamente.
    """
    def __init__(self, circuit_factory: CircuitFactory):
        self._circuit_factory = circuit_factory

    def create(
        self,
        population_size: int,
        num_qubits: int,
        max_depth: int,
        min_depth: int
    ) -> Population:
        """
        Cria uma população com 'population_size' circuitos aleatórios.
        """
        individuals = []
        for _ in range(population_size):
            circuit = self._circuit_factory.create_random_circuit(
                num_qubits=num_qubits,
                max_depth=max_depth,
                min_depth=min_depth
            )
            individuals.append(circuit)

        return Population(individuals)
