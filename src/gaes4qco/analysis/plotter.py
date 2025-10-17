from typing import List, Dict

import matplotlib.pyplot as plt
import numpy as np

from .interfaces import IPlotter
from .data_models import ResultData


def _clip(values):
    """Ensure all values are within [0, 1]."""
    return np.clip(values, 0.0, 1.0)


class EvolutionPlotter(IPlotter):
    """Generates a detailed evolution plot with clear phase markers and info boxes."""

    def plot(self, data: ResultData, output_path: str, config_info: Dict = None):
        print(f"Gerando gráfico em {output_path}...")

        generations = range(data.generation_count)
        avg_fitness = _clip(np.array(data.average_fitness_per_generation))
        std_dev = np.array(data.std_dev_fitness_per_generation)
        best_fitness = _clip(np.array(data.best_fitness_per_generation))
        diversity = _clip(np.array(data.structural_diversity_per_generation))

        lower_fill = _clip(avg_fitness - std_dev)
        upper_fill = _clip(avg_fitness + std_dev)

        # === Layout com área inferior extra ===
        fig = plt.figure(figsize=(14, 9))
        gs = fig.add_gridspec(2, 1, height_ratios=[3.5, 1])
        ax1 = fig.add_subplot(gs[0])

        # --- Eixo primário: Fitness ---
        color = 'tab:blue'
        ax1.set_xlabel('Geração')
        ax1.set_ylabel('Fitness', color=color)
        ax1.plot(generations, best_fitness, color=color, linestyle='-', label='Melhor Fitness')
        ax1.plot(generations, avg_fitness, color=color, linestyle='--', label='Fitness Médio')
        ax1.fill_between(generations, lower_fill, upper_fill, alpha=0.25, color=color)
        ax1.tick_params(axis='y', labelcolor=color)
        ax1.grid(True, which='both', linestyle=':', linewidth=0.5)
        ax1.set_ylim(0, 1.05)
        ax1.set_xlim(0, data.generation_count - 1)

        # --- Eixo secundário: Diversidade ---
        ax2 = ax1.twinx()
        color = 'tab:red'
        ax2.set_ylabel('Diversidade Estrutural', color=color)
        ax2.plot(generations, diversity, color=color, linestyle='-.', label='Diversidade')
        ax2.tick_params(axis='y', labelcolor=color)
        ax2.set_ylim(0, 1.05)

        # --- Marcação visual das fases ---
        if config_info and "phases" in config_info:
            phases = config_info["phases"]
            phase_colors = plt.cm.Set2(np.linspace(0, 1, len(phases)))

            current_start = 0
            for i, (phase, color_box) in enumerate(zip(phases, phase_colors)):
                phase_len = phase.get("generations", 0)
                start_gen = current_start

                # Somente da segunda fase em diante: linha vertical marcando início
                if i > 0:
                    ax1.axvline(
                        x=start_gen,
                        color=color_box,
                        linestyle='--',
                        linewidth=1.3,
                        alpha=0.7,
                    )

                # Numeração da geração de início da phase
                ax1.text(
                    start_gen,
                    -0.08,  # abaixo do eixo X
                    str(start_gen),
                    color=color_box,
                    fontsize=9,
                    fontweight='bold',
                    ha='center',
                    va='top',
                    transform=ax1.get_xaxis_transform()
                )

                current_start += phase_len

        # --- Legenda combinada ---
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax2.legend(lines1 + lines2, labels1 + labels2, loc='center right')

        plt.suptitle('Evolução do Fitness e Diversidade Genética por Geração', fontsize=13, y=0.94)

        # === Área inferior: Detalhes das Phases ===
        ax_config = fig.add_subplot(gs[1])
        ax_config.axis('off')

        if config_info and "phases" in config_info:
            phases = config_info["phases"]
            num_phases = len(phases)
            phase_colors = plt.cm.tab10(np.linspace(0, 1, num_phases))

            x_positions = np.linspace(0.02, 0.9, num_phases)
            for i, (phase, color_box) in enumerate(zip(phases, phase_colors)):
                true_flags = []
                if phase.get("use_stepsize"): true_flags.append("StepSize")
                if phase.get("use_adaptive_rates"): true_flags.append("AdaptiveRates")
                if phase.get("use_weighted_fitness"): true_flags.append("WeightedFitness")
                if phase.get("use_fitness_sharing"): true_flags.append("FitnessSharing")
                if phase.get("use_bandit_mutation"): true_flags.append("BanditMutation")

                text_lines = [
                    f"Phase {i + 1}",
                    f"Gerações: {phase.get('generations', '-')}",
                    f"ParentSel: {phase.get('parent_selection', '-')}",
                    f"SurvivorSel: {phase.get('survivor_selection', '-')}",
                    f"Crossover: {phase.get('crossover_strategy', '-')}"
                ]
                if true_flags:
                    text_lines.append("Ativos: " + ", ".join(true_flags))

                ax_config.text(
                    x_positions[i],
                    0.5,
                    "\n".join(text_lines),
                    fontsize=9,
                    va='center',
                    ha='left',
                    color='black',
                    bbox=dict(
                        boxstyle="round,pad=0.4",
                        facecolor=(color_box[0], color_box[1], color_box[2], 0.2),
                        edgecolor=color_box,
                        linewidth=1.2,
                    ),
                    transform=ax_config.transAxes
                )

        plt.subplots_adjust(hspace=0.35)
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
