from analysis.loader import JsonDataLoader
from analysis.plotter import EvolutionPlotter, AggregatePlotter
from pathlib import Path
import glob

PROJECT_PATH = Path(__file__).parents[2]


def main():
    """
    Carrega os dados de um ou mais arquivos de resultado e gera os gráficos.
    """
    # Encontra todos os arquivos de resultado no diretório
    result_files = glob.glob(str(PROJECT_PATH / "results/*/results_seed_*.json"))
    if not result_files:
        print("Nenhum arquivo de resultado (results_seed_*.json) encontrado.")
        return

    # Instancia nossos componentes de análise
    loader = JsonDataLoader()
    single_plotter = EvolutionPlotter()
    aggregate_plotter = AggregatePlotter()

    all_results_data_normal = []
    all_results_data_stepsize = []
    for filepath in result_files:
        try:
            # Carrega os dados
            result_data = loader.load(filepath)
            if filepath.count("normal"):
                all_results_data_normal.append(result_data)
            else:
                all_results_data_stepsize.append(result_data)

            # Define o nome do arquivo de saída
            output_filename = filepath.replace('.json', '.png')

            # Gera o gráfico
            single_plotter.plot(result_data, output_filename)
        except Exception as e:
            print(f"Falha ao processar o arquivo {filepath}: {e}")

    if len(all_results_data_normal):
        aggregate_plotter.plot(all_results_data_normal, str(PROJECT_PATH / "results/normal/aggregated_performance.png"))

    if len(all_results_data_stepsize):
        aggregate_plotter.plot(all_results_data_stepsize, str(PROJECT_PATH / "results/stepsize/aggregated_performance.png"))


if __name__ == "__main__":
    main()
