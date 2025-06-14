from typing import Optional

from GAES4QCO_1.src.GAES4QCO.domain.models.circuit import Circuit


class Population:
    def __init__(self, circuits: list[Circuit], best_circuit: Optional[Circuit], mean_fitness: Optional[float], variance_fitness: Optional[float], worse_circuit: Optional[Circuit]):
        self.circuits = circuits
        self.best_circuit = best_circuit
        self.mean_fitness = mean_fitness
        self.variance_fitness = variance_fitness
        self.worse_circuit = worse_circuit
    