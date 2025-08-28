# optimization/observer.py

import json
import numpy as np
from .interfaces import IProgressObserver
from evolutionary_algorithm.population import Population


class JsonProgressObserver(IProgressObserver):
    """
    ## Implementa um observador que coleta estatísticas e salva em um arquivo JSON.
    """

    def __init__(self, filename: str):
        self._filename = filename
        self._data_to_save = {
            "fitness_per_generation": [],
            "fidelity_per_generation": [],
            "average_fitness_per_generation": [],
            "std_dev_fitness_per_generation": [],
            "structural_diversity_per_generation": [],
        }

    def update(self, generation: int, population: Population):
        """Coleta os dados de fitness da população atual."""
        individuals = population.get_individuals()
        individuals.sort(key=lambda individual: (individual.fitness, individual.fidelity), reverse=True)
        fitness_values = [ind.fitness for ind in individuals]
        fidelity_values = [ind.fidelity for ind in individuals]
        diversity = population.calculate_structural_diversity()

        self._data_to_save["fitness_per_generation"].append(fitness_values)
        self._data_to_save["fidelity_per_generation"].append(fidelity_values)
        self._data_to_save["average_fitness_per_generation"].append(np.mean(fitness_values))
        self._data_to_save["std_dev_fitness_per_generation"].append(np.std(fitness_values))
        self._data_to_save["structural_diversity_per_generation"].append(diversity)

        # Log no console para feedback imediato
        if generation % 25 == 0:
            avg_fitness = np.mean(fitness_values)
            print(
                f"Generation {generation} | Best Fitness: {max(fitness_values)*100:.10f} | Best Fidelity: {max(fidelity_values)*100:.10f} | "
                f"Avg Fitness: {avg_fitness:.4f} | Diversity: {diversity:.4f}"
            )

    def save(self):
        """Salva o dicionário de dados no arquivo JSON."""
        print(f"Saving results to {self._filename}...")
        with open(self._filename, 'w') as f:
            json.dump(self._data_to_save, f, indent=4)
        print("Save complete.")
