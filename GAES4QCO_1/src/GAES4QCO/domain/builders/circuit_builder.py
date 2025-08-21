from .column_component_builder import ColumnBuilder
from ..models.circuit.circuit import Circuit

class CircuitBuilder:
    def __init__(self, column_builder: ColumnBuilder):
        self.column_builder = column_builder

    def build(self, num_qubits: int, depth: int) -> Circuit:
        """
        Constrói e retorna uma nova instância de Circuit com estrutura aleatória.
        """
        all_columns = [
            self.column_builder.build(total_circuit_qubits=num_qubits)
            for _ in range(depth)
        ]

        return Circuit(count_qubits=num_qubits, columns_components=all_columns)


    def gen_random_circuit(self):
        depth = random.randint(minDepth, maxDepth)
        circuit = Circuit(numQubits, depth)
        for y in range(depth):
            gatesParametersLocal = deepcopy(gatesParameters)
            qubitsFree = list(range(numQubits))
            while qubitsFree:
                gate, qubitsFree = createGateToListQubits(qubitsFree, gatesParametersLocal)
                circuit.gates[y].append(gate)
        circuit.constructCircuit()
        return circuit