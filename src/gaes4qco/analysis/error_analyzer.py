from qiskit.quantum_info import Statevector, state_fidelity
from quantum_circuit.circuit import Circuit
from quantum_circuit.interfaces import IQuantumExecutor


class ErrorAnalyzer:
    """Calcula a taxa de erro de um circuito comparando sua execução
    com o resultado ideal, seja em statevector ou counts ruidosos."""

    def __init__(self, executor: IQuantumExecutor):
        self._executor = executor

    def calculate_error_rate(self, circuit: Circuit, target_statevector: Statevector, shots: int) -> float:
        """
        Executa o circuito e calcula a taxa de erro.
        Funciona tanto para backend determinístico (statevector) quanto ruidoso (counts).
        """
        # Estado com maior probabilidade no target
        ideal_probs = target_statevector.probabilities_dict()
        print(ideal_probs)
        # correct_state_str = max(ideal_probs, key=ideal_probs.get)
        # Executa o circuito
        result = self._executor.execute(circuit, shots, measure=False)
        print(result)
        # Se o resultado for counts (dict)
        errors_rates = []
        if isinstance(result, dict):
            for key in ideal_probs.keys():
                print(key)
                correct_counts = result.get(key, 0)
                success_probability = correct_counts / shots
                success = abs(success_probability - ideal_probs[key])
                error_rate = abs(1.0 - success_probability)
                print(f"[Simulador] Estado correto: '{key}' ocorreu {correct_counts}/{shots} vezes")
                print(f"Probabilidade de sucesso: {success_probability:.10%}, Taxa de erro: {error_rate:.2%}")
                errors_rates.append(error_rate)
                # Se o resultado for statevector
            return sum(errors_rates) / len(errors_rates)
        elif isinstance(result, Statevector):
            # Probabilidade de medir o estado correto
            success_probability = state_fidelity(result, target_statevector)
            error_rate = 1.0 - success_probability
            print(f"Probabilidade de sucesso: {success_probability:.2%}, Taxa de erro: {error_rate:.2%}")
            return error_rate

        else:
            raise TypeError(f"Executor retornou tipo inesperado: {type(result)}")
