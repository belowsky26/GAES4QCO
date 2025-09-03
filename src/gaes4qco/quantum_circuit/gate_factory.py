import random
from inspect import Parameter, signature
from typing import Type, List, Dict, Tuple

from numpy import pi as PI
from qiskit.circuit import Gate as QiskitGate
from qiskit.circuit.library.standard_gates import (
    XGate, YGate, ZGate, HGate, PhaseGate, SwapGate, UGate, RXGate,
    RYGate, RZGate, SGate, SXGate, TGate, IGate, RGate, RXXGate,
    RYYGate, RZXGate, RZZGate, DCXGate, ECRGate,
    RCCXGate, RC3XGate, XXMinusYYGate, XXPlusYYGate
)

# Imports atualizados para a nova arquitetura
from .gate import Gate
from shared.value_objects import StepSize


class GateFactory:
    """
    Cria uma entidade 'Gate' de forma aleatória,
    encapsulando as regras de seleção e parametrização.
    """

    # O mapa de gates é um detalhe de implementação da fábrica.
    _gate_class_map: Dict[int, List[Type[QiskitGate]]] = {
        1: [XGate, YGate, ZGate, HGate, SGate, TGate, IGate, SXGate,
            UGate, PhaseGate, RGate, RXGate, RYGate, RZGate],
        2: [SwapGate, RXXGate, RYYGate, RZZGate, RZXGate,
            DCXGate, ECRGate, XXMinusYYGate, XXPlusYYGate],
        3: [RCCXGate],
        4: [RC3XGate]
    }
    _gate_name_map: Dict[str, Type[QiskitGate]] = {
        cls.__name__: cls for _, gate_list in _gate_class_map.items() for cls in gate_list
    }
    _inverses_class = [SGate, SXGate, TGate, DCXGate]
    _gate_without_control = [IGate]

    def build_gate(self, available_qubits: List[int], use_evolutionary_strategy: bool) -> Gate:
        """
        Método principal para construir uma instância da nossa entidade Gate.
        """
        lim_qubits = len(available_qubits)
        if lim_qubits == 0:
            raise ValueError("Não há qubits disponíveis para criar um gate.")

        gate_class, qubits_min = self._choice_gate_class(lim_qubits)
        generated_angles = self._generate_random_params_for_gate(gate_class)
        steps_sizes = [StepSize() for _ in generated_angles] if use_evolutionary_strategy else None
        chosen_qubits, extra_controls = self._choice_qubits(gate_class, available_qubits, qubits_min)
        is_inverse = self._choice_inverse_class(gate_class)

        # Retorna nossa entidade 'Gate', e não 'GateComponent'
        return Gate(
            gate_class=gate_class,
            qubits=chosen_qubits,
            parameters=generated_angles,
            steps_sizes=steps_sizes,
            extra_controls=extra_controls,
            is_inverse=is_inverse
        )

    def create_from_dict(self, data: dict) -> Gate:
        """
        Reconstrói uma entidade Gate a partir de um dicionário (proveniente de um JSON).
        """
        gate_name = data.get("gate_class_name")
        gate_class = self._gate_name_map.get(gate_name)

        if not gate_class:
            raise ValueError(f"Gate '{gate_name}' desconhecido. Não é possível reconstruir o circuito.")

        steps_sizes_dict = data.get("step_sizes")
        steps_sizes = [StepSize(**step_size) for step_size in steps_sizes_dict] if steps_sizes_dict else None

        return Gate(
            gate_class=gate_class,
            qubits=data.get("qubits"),
            parameters=data.get("parameters"),
            steps_sizes=steps_sizes,
            extra_controls=data.get("extra_controls"),
            is_inverse=data.get("is_inverse")
        )

    @classmethod
    def _choice_gate_class(cls, lim_qubits: int) -> Tuple[Type[QiskitGate], int]:
        candidate_pool = [
            (gate_class, num_qubits)
            for num_qubits, gate_list in cls._gate_class_map.items()
            if num_qubits <= lim_qubits
            for gate_class in gate_list
        ]
        if not candidate_pool:
            raise ValueError(f"Não há gates disponíveis para {lim_qubits} ou menos qubits.")
        return random.choice(candidate_pool)

    @classmethod
    def _choice_qubits(cls, gate_class: Type[QiskitGate], qubits: List[int], min_qubits: int) -> Tuple[List[int], int]:
        lim_qubits = len(qubits)
        dif_qubits = lim_qubits - min_qubits
        extra_controls = 0
        if gate_class not in cls._gate_without_control and dif_qubits > 0:
            extra_controls = random.randint(0, dif_qubits)

        num_total_qubits = min_qubits + extra_controls
        chosen_qubits = random.sample(qubits, num_total_qubits)
        return chosen_qubits, extra_controls

    @classmethod
    def _choice_inverse_class(cls, gate_class: Type[QiskitGate]) -> bool:
        return gate_class in cls._inverses_class and random.choice([False, True])

    @classmethod
    def _generate_random_params_for_gate(cls, gate_class: Type[QiskitGate]) -> List[float]:
        """
        Usa introspecção para gerar ângulos aleatórios.
        Nota: Este método é poderoso, mas frágil. Mudanças na API do Qiskit
        podem exigir sua atualização.
        """
        sig = signature(gate_class.__init__)

        generated_angles = []
        for p in sig.parameters.values():
            # Verifica se é um parâmetro de ângulo que precisa ser preenchido
            if p.name not in ['self', 'label'] and p.default is Parameter.empty:
                angle = random.uniform(0, PI) if "theta" in p.name else random.uniform(0, 2 * PI)
                generated_angles.append(angle)
        return generated_angles
