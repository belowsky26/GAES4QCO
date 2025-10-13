import sys
from pathlib import Path

from experiment.parallel_manager import ParallelExperimentManager
from experiment.test_loader import TestConfigLoader


def main():
    """
    Entry point for running all GA experiments defined in `tests/`.
    Uses the TestConfigLoader to automatically handle target generation and loading.
    """
    project_root = Path(__file__).resolve().parents[2]
    print(project_root)
    tests_dir = project_root / "tests"

    print("🚀 Starting Quantum Circuit Evolution Experiments")
    print(f"🔍 Loading test configurations from: {tests_dir}")

    # --- Load all test configurations ---
    loader = TestConfigLoader(tests_dir)
    experiment_configs, filenames = loader.load_all()

    if not experiment_configs:
        print("⚠️ No valid test configurations found. Exiting.")
        sys.exit(0)

    # --- Execute all experiments in parallel ---
    print(f"🧠 Running {len(experiment_configs)} experiments in parallel...")
    manager = ParallelExperimentManager(
        configs=experiment_configs,
        filenames=filenames,
        max_processes=len(experiment_configs)
    )

    all_results = manager.run_all()

    # --- Summarize results ---
    print("\n=== 🧩 EXPERIMENT SUMMARY ===")
    for result in all_results:
        fname = result.get("filename", "unknown.json")
        seed = result.get("seed", "N/A")
        best_fit = result.get("best_fitness", 0.0)
        duration = result.get("duration_seconds", 0.0)
        print(f"📄 {fname}: Seed {seed} | Best Fitness = {best_fit:.6f} | Duration = {duration:.2f}s")

    if all_results:
        best_run = max(all_results, key=lambda r: r.get("best_fitness", 0.0))
        print("\n🏆 BEST RUN SUMMARY")
        print(f"📄 {best_run['filename']} | Seed {best_run['seed']} | Fitness {best_run['best_fitness']:.6f}")

    print("\n✅ All experiments completed successfully.")


if __name__ == "__main__":
    main()
