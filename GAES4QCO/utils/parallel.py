# quantum_opt_framework/utils/parallel.py
from multiprocessing import Pool
from typing import Callable, List, Any

def parallel_map(func: Callable, data: List[Any], num_processes: int = None) -> List[Any]:
    """Executa uma função em paralelo sobre uma lista de dados."""
    with Pool(processes=num_processes) as pool:
        results = list(pool.map(func, data))
    return results