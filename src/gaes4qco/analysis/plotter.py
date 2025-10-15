import matplotlib.pyplot as plt
from typing import List
import numpy as np
from .interfaces import IPlotter
from .data_models import ResultData


def _clip(values):
    """Garante que todos os valores fiquem entre 0 e 1."""
    return np.clip(values, 0.0, 1.0)


class EvolutionPlotter(IPlotter):
    """Gera um gráfico da evolução do fitness e da diversidade."""

    def plot(self, data: ResultData, output_path: str):
        print(f"Gerando gráfico em {output_path}...")

        generations = range(data.generation_count)
        avg_fitness = _clip(np.array(data.average_fitness_per_generation))
        std_dev = np.array(data.std_dev_fitness_per_generation)
        best_fitness = _clip(np.array(data.best_fitness_per_generation))
        diversity = _clip(np.array(data.structural_diversity_per_generation))

        # Limita os intervalos de preenchimento para evitar sair de [0, 1]
        lower_fill = _clip(avg_fitness - std_dev)
        upper_fill = _clip(avg_fitness + std_dev)

        fig, ax1 = plt.subplots(figsize=(14, 7))

        # Eixo Y primário (Fitness)
        color = 'tab:blue'
        ax1.set_xlabel('Geração')
        ax1.set_ylabel('Fitness', color=color)
        ax1.plot(generations, best_fitness, color=color, linestyle='-', label='Melhor Fitness')
        ax1.plot(generations, avg_fitness, color=color, linestyle='--', label='Fitness Médio')
        ax1.fill_between(generations, lower_fill, upper_fill, alpha=0.2, color=color)

        ax1.tick_params(axis='y', labelcolor=color)
        ax1.grid(True, which='both', linestyle=':', linewidth=0.5)
        ax1.set_ylim(0, 1.05)

        # Eixo Y secundário (Diversidade)
        ax2 = ax1.twinx()
        color = 'tab:red'
        ax2.set_ylabel('Diversidade Estrutural', color=color)
        ax2.plot(generations, diversity, color=color, linestyle='-.', label='Diversidade')
        ax2.tick_params(axis='y', labelcolor=color)
        ax2.set_ylim(0, 1.05)

        # Legendas combinadas
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax2.legend(lines1 + lines2, labels1 + labels2, loc='center right')

        plt.title('Evolução do Fitness e Diversidade Genética por Geração', pad=20)  # afasta o título do topo
        fig.tight_layout(rect=(0, 0, 1, 0.97))  # reserva espaço extra para o título
        plt.savefig(output_path, bbox_inches='tight', dpi=200)
        plt.close()
        print("✅ Gráfico salvo com sucesso.")


class AggregatePlotter:
    """Gera um gráfico com a média e desvio padrão de múltiplas execuções."""

    def plot(self, all_results: List[ResultData], output_path: str):
        print(f"Gerando gráfico agregado em {output_path}...")

        # Número mínimo de gerações entre execuções
        min_generations = min(res.generation_count for res in all_results)

        # Matrizes 2D (cada linha: geração, cada coluna: execução)
        best_fitness_matrix = np.array(
            [_clip(res.best_fitness_per_generation[:min_generations]) for res in all_results]
        )
        avg_fitness_matrix = np.array(
            [_clip(res.average_fitness_per_generation[:min_generations]) for res in all_results]
        )
        diversity_matrix = np.array(
            [_clip(res.structural_diversity_per_generation[:min_generations]) for res in all_results]
        )

        # Médias e desvios
        mean_best_fitness = _clip(np.mean(best_fitness_matrix, axis=0))
        std_best_fitness = np.std(best_fitness_matrix, axis=0)
        mean_avg_fitness = _clip(np.mean(avg_fitness_matrix, axis=0))
        std_avg_fitness = np.std(avg_fitness_matrix, axis=0)
        mean_diversity = _clip(np.mean(diversity_matrix, axis=0))
        std_diversity = np.std(diversity_matrix, axis=0)

        # Preenchimentos limitados
        lower_best = _clip(mean_best_fitness - std_best_fitness)
        upper_best = _clip(mean_best_fitness + std_best_fitness)
        lower_avg = _clip(mean_avg_fitness - std_avg_fitness)
        upper_avg = _clip(mean_avg_fitness + std_avg_fitness)
        lower_div = _clip(mean_diversity - std_diversity)
        upper_div = _clip(mean_diversity + std_diversity)

        generations = range(min_generations)
        fig, ax1 = plt.subplots(figsize=(14, 7))

        # --- Fitness ---
        color = 'tab:blue'
        ax1.set_xlabel('Geração')
        ax1.set_ylabel('Fitness Médio (entre execuções)', color=color)
        ax1.plot(generations, mean_best_fitness, color='blue', linestyle='-', label='Média Melhor Fitness')
        ax1.fill_between(generations, lower_best, upper_best, alpha=0.2, color='blue')
        ax1.plot(generations, mean_avg_fitness, color='cyan', linestyle='--', label='Média Fitness Médio')
        ax1.fill_between(generations, lower_avg, upper_avg, alpha=0.2, color='cyan')

        ax1.tick_params(axis='y', labelcolor=color)
        ax1.grid(True, which='both', linestyle=':', linewidth=0.5)
        ax1.set_ylim(0, 1.05)

        # --- Diversidade ---
        ax2 = ax1.twinx()
        color = 'tab:red'
        ax2.set_ylabel('Diversidade Estrutural Média', color=color)
        ax2.plot(generations, mean_diversity, color=color, linestyle='-.', label='Média Diversidade')
        ax2.fill_between(generations, lower_div, upper_div, alpha=0.2, color=color)
        ax2.tick_params(axis='y', labelcolor=color)
        ax2.set_ylim(0, 1.05)

        # Legendas combinadas
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax2.legend(lines1 + lines2, labels1 + labels2, loc='center right')

        plt.title(f'Desempenho Médio de {len(all_results)} Execuções', pad=20)
        fig.tight_layout(rect=(0, 0, 1, 0.97))
        plt.savefig(output_path, bbox_inches='tight', dpi=200)
        plt.close()
        print("✅ Gráfico agregado salvo com sucesso.")
