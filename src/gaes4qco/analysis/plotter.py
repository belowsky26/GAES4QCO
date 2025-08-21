import matplotlib.pyplot as plt
from typing import List
import numpy as np
from .interfaces import IPlotter
from .data_models import ResultData


class EvolutionPlotter(IPlotter):
    """Gera um gráfico da evolução do fitness e da diversidade."""

    def plot(self, data: ResultData, output_path: str):
        print(f"Gerando gráfico em {output_path}...")

        generations = range(data.generation_count)
        avg_fitness = data.average_fitness_per_generation
        std_dev = data.std_dev_fitness_per_generation
        best_fitness = data.best_fitness_per_generation
        diversity = data.structural_diversity_per_generation

        fig, ax1 = plt.subplots(figsize=(14, 7))

        # Eixo Y primário (Fitness)
        color = 'tab:blue'
        ax1.set_xlabel('Geração')
        ax1.set_ylabel('Fitness', color=color)
        ax1.plot(generations, best_fitness, color=color, linestyle='-', label='Melhor Fitness')
        ax1.plot(generations, avg_fitness, color=color, linestyle='--', label='Fitness Médio')
        # Área sombreada para o desvio padrão
        ax1.fill_between(
            generations,
            [m - s for m, s in zip(avg_fitness, std_dev)],
            [m + s for m, s in zip(avg_fitness, std_dev)],
            alpha=0.2,
            color=color
        )
        ax1.tick_params(axis='y', labelcolor=color)
        ax1.grid(True, which='both', linestyle=':', linewidth=0.5)
        ax1.set_ylim(0, 1.05)  # Fitness varia de 0 a 1

        # Eixo Y secundário (Diversidade)
        ax2 = ax1.twinx()
        color = 'tab:red'
        ax2.set_ylabel('Diversidade Estrutural', color=color)
        ax2.plot(generations, diversity, color=color, linestyle='-.', label='Diversidade')
        ax2.tick_params(axis='y', labelcolor=color)
        ax2.set_ylim(0, 1.05)  # Diversidade também varia de 0 a 1

        # Legendas
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax2.legend(lines1 + lines2, labels1 + labels2, loc='center right')

        fig.tight_layout()
        plt.title('Evolução do Fitness e Diversidade Genética por Geração')
        plt.savefig(output_path)
        plt.close()
        print("Gráfico salvo com sucesso.")


class AggregatePlotter:
    """Gera um gráfico com a média e desvio padrão de múltiplas execuções."""

    def plot(self, all_results: List[ResultData], output_path: str):
        print(f"Gerando gráfico agregado em {output_path}...")

        # Encontra o número mínimo de gerações entre todas as execuções para garantir consistência
        min_generations = min(res.generation_count for res in all_results)

        # Cria arrays 2D para cada métrica (cada linha é uma geração, cada coluna é uma execução)
        best_fitness_matrix = np.array([res.best_fitness_per_generation[:min_generations] for res in all_results])
        avg_fitness_matrix = np.array([res.average_fitness_per_generation[:min_generations] for res in all_results])
        diversity_matrix = np.array([res.structural_diversity_per_generation[:min_generations] for res in all_results])

        # Calcula a média e o desvio padrão ao longo das execuções (eixo 1)
        mean_best_fitness = np.mean(best_fitness_matrix, axis=0)
        std_best_fitness = np.std(best_fitness_matrix, axis=0)

        mean_avg_fitness = np.mean(avg_fitness_matrix, axis=0)
        std_avg_fitness = np.std(avg_fitness_matrix, axis=0)

        mean_diversity = np.mean(diversity_matrix, axis=0)
        std_diversity = np.std(diversity_matrix, axis=0)

        generations = range(min_generations)

        # Lógica de plotagem similar à anterior, mas com os dados agregados
        fig, ax1 = plt.subplots(figsize=(14, 7))

        # Eixo Y primário (Fitness)
        color = 'tab:blue'
        ax1.set_xlabel('Geração')
        ax1.set_ylabel('Fitness Médio (entre execuções)', color=color)
        ax1.plot(generations, mean_best_fitness, color='blue', linestyle='-', label='Média Melhor Fitness')
        ax1.fill_between(generations, mean_best_fitness - std_best_fitness, mean_best_fitness + std_best_fitness,
                         alpha=0.2, color='blue')

        ax1.plot(generations, mean_avg_fitness, color='cyan', linestyle='--', label='Média Fitness Médio')
        ax1.fill_between(generations, mean_avg_fitness - std_avg_fitness, mean_avg_fitness + std_avg_fitness, alpha=0.2,
                         color='cyan')

        ax1.tick_params(axis='y', labelcolor=color)
        ax1.grid(True, which='both', linestyle=':', linewidth=0.5)
        ax1.set_ylim(0, 1.05)

        # Eixo Y secundário (Diversidade)
        ax2 = ax1.twinx()
        color = 'tab:red'
        ax2.set_ylabel('Diversidade Estrutural Média', color=color)
        ax2.plot(generations, mean_diversity, color=color, linestyle='-.', label='Média Diversidade')
        ax2.fill_between(generations, mean_diversity - std_diversity, mean_diversity + std_diversity, alpha=0.2,
                         color=color)
        ax2.tick_params(axis='y', labelcolor=color)
        ax2.set_ylim(0, 1.05)

        # Legendas
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax2.legend(lines1 + lines2, labels1 + labels2, loc='center right')

        fig.tight_layout()
        plt.title(f'Desempenho Médio de {len(all_results)} Execuções')
        plt.savefig(output_path)
        plt.close()
        print("Gráfico agregado salvo com sucesso.")
