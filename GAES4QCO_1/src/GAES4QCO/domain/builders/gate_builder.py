import random
import inspect
from typing import List, Type, Tuple

from numpy import pi as PI
from qiskit.circuit import Gate

from .step_size_builder import StepSizeBuilder
from ..models.circuit.gate_component import GateComponent
from ..factories.gate_factory import GateFactory


class GateBuilder:
    """
    Responsável por construir uma única instância de GateComponent,
    completa e configurada aleatoriamente.
    """

    def __init__(self, gate_factory: GateFactory, step_size_builder: StepSizeBuilder):
        # 1. RECEBE o StepSizeBuilder via Injeção de Dependência
        self.factory = gate_factory
        self.step_size_builder = step_size_builder

    def build(self, available_qubits: List[int], evolutionary_strategies: bool = True) -> Tuple[
        GateComponent, List[int]]:
        """
        Constrói uma instância de GateComponent completa e aleatória.
        """
        max_qubits = len(available_qubits)

        # 1. Obter a matéria-prima da fábrica
        base_gate_class, base_num_qubits = self.factory.choice_gate_class(max_qubits)

        # 2. Tomar decisões aleatórias usando a fábrica como fonte de regras
        is_inverse = self._should_be_inverse(base_gate_class)
        chosen_qubits, num_controls = self._plan_layout(available_qubits, base_gate_class, base_num_qubits)

        # 3. Gerar parâmetros e criar o componente
        params = self._generate_params(base_gate_class)
        step_sizes = [self.step_size_builder.build() for _ in params] if evolutionary_strategies else None

        gate_component = GateComponent(
            gate_class=base_gate_class,
            qubits=chosen_qubits,
            parameters=params,
            steps_sizes=step_sizes,
            extra_controls=num_controls,
            is_inverse=is_inverse
        )

        free_qubits = list(set(available_qubits) - set(chosen_qubits))
        return gate_component, free_qubits

    def _should_be_inverse(self, gate_class: Type[Gate]) -> bool:
        """Decide aleatoriamente se um gate deve ser invertido."""
        if self.factory.can_be_inverted_to_new_gate(gate_class):
            return random.choice([False, True])
        return False

    def _plan_layout(self, available_qubits: List[int], gate_class: Type[Gate], base_num_qubits: int) -> Tuple[
        List[int], int]:
        """Decide quantos controles adicionar e seleciona os qubits."""
        if not self.factory.can_be_controlled(gate_class):
            return random.sample(available_qubits, base_num_qubits), 0

        max_extra_controls = len(available_qubits) - base_num_qubits
        num_extra_controls = random.randint(0, max_extra_controls)
        total_needed = base_num_qubits + num_extra_controls
        return random.sample(available_qubits, total_needed), num_extra_controls

    def _generate_params(self, gate_class: Type[Gate]) -> List[float]:
        """Gera parâmetros aleatórios."""
        sig = inspect.signature(gate_class.__init__)
        target_annotations = {'ParameterValueType',
                              'typing.Union[qiskit.circuit.parameterexpression.ParameterExpression, float]'}
        params = [p for p in sig.parameters.values() if
                  p.name != 'self' and p.default is inspect.Parameter.empty and str(p.annotation) in target_annotations]
        return [random.uniform(0, PI) if p.name == 'theta' else random.uniform(0, 2 * PI) for p in params]
