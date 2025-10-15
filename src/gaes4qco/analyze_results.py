from analysis.loader import JsonDataLoader
from analysis.plotter import EvolutionPlotter, AggregatePlotter
from pathlib import Path
import glob


PROJECT_PATH = Path(__file__).parents[2]


def main():
    """
    Carrega os dados de 'results/concatenated' e gera os gráficos individuais
    e agregados de cada conjunto de experimentos.
    Todos os gráficos são salvos em 'results/concatenated/plots/'.
    """
    concatenated_dir = PROJECT_PATH / "results" / "concatenated"
    plots_dir = concatenated_dir / "plots"
    plots_dir.mkdir(parents=True, exist_ok=True)

    if not concatenated_dir.exists():
        print("❌ Diretório 'results/concatenated' não encontrado. Execute o concatenator primeiro.")
        return

    # Localiza todos os arquivos concatenados (ex: test_01_basic_concatenated_result.json)
    result_files = glob.glob(str(concatenated_dir / "*_concatenated_result.json"))

    if not result_files:
        print("⚠️ Nenhum arquivo concatenado encontrado em results/concatenated.")
        return

    # Instancia os componentes de análise
    loader = JsonDataLoader()
    single_plotter = EvolutionPlotter()
    aggregate_plotter = AggregatePlotter()

    grouped_results = {}

    for filepath in result_files:
        try:
            result_data = loader.load(filepath)

            # Nome base do arquivo (sem extensão)
            name = Path(filepath).stem

            # Define o caminho de saída do gráfico individual
            output_filename = plots_dir / f"{name}.png"
            single_plotter.plot(result_data, str(output_filename))

            # Classifica o teste em um grupo (ex: stepsize, sharing, nsga, normal)
            lower_name = name.lower()
            if "stepsize" in lower_name:
                group_key = "stepsize"
            elif "sharing" in lower_name:
                group_key = "sharing"
            elif "nsga" in lower_name:
                group_key = "nsga"
            else:
                group_key = "normal"

            grouped_results.setdefault(group_key, []).append(result_data)

        except Exception as e:
            print(f"⚠️ Falha ao processar {filepath}: {e}")

    # === Gráficos agregados por grupo ===
    for group, data_list in grouped_results.items():
        if not data_list:
            continue

        group_plot_path = plots_dir / f"aggregated_{group}_performance.png"
        aggregate_plotter.plot(data_list, str(group_plot_path))
        print(f"📊 Gráfico agregado salvo para grupo '{group}' → {group_plot_path.name}")

    print("\n✅ Todos os gráficos foram gerados com sucesso em 'results/concatenated/plots/'.")


if __name__ == "__main__":
    main()
