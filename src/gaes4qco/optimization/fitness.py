# optimization/fitness.py

from qiskit.quantum_info import Statevector, state_fidelity
from .interfaces import IFitnessEvaluator
from quantum_circuit.circuit import Circuit
from quantum_circuit.interfaces import IQuantumCircuitAdapter


class FidelityFitnessEvaluator(IFitnessEvaluator):
    """
    ## Calcula o fitness com base na fidelidade do estado quântico.
    ## Esta classe substitui a antiga função 'fidelityFitnessFunction'.
    """

    def __init__(self, target_statevector: Statevector, circuit_adapter: IQuantumCircuitAdapter):
        self._target_sv = target_statevector
        self._adapter = circuit_adapter

    def evaluate(self, circuit: Circuit) -> float:
        """
        Converte o circuito de domínio para Qiskit usando o adapter
        e então calcula a fidelidade.
        """
        # ## A conversão é delegada ao adapter, respeitando a Inversão de Dependência
        qiskit_circuit = self._adapter.from_domain(circuit)

        # ## O cálculo de fidelidade do Qiskit é realizado aqui
        solution_sv = Statevector.from_instruction(qiskit_circuit)
        fidelity = state_fidelity(solution_sv, self._target_sv)
        return max(0.0, fidelity)
