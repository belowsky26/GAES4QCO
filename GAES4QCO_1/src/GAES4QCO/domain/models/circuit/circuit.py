from qiskit.circuit import QuantumCircuit


from GAES4QCO_1.src.GAES4QCO.domain.models.column_component import ColumnComponent


class Circuit:
    def __init__(self, count_qubits: int, depth: int, columns_components: list[ColumnComponent], apply_evolutionary_strategy: bool = False, fitness: float = 0.):
        self.count_qubits = count_qubits
        self.depth = depth
        self.columns_components = columns_components
        self.apply_evolutionary_strategy = apply_evolutionary_strategy
        self.fitness = fitness


    def build(self):
        circuit = QuantumCircuit(self.count_qubits)
        for column in self.columns_components:
            for gate_component in column.get_gates():
                gate, qubits = gate_component.build()
                circuit.append(gate, qubits)
        return circuit

    def gen_random_circuit(self, numQubits: int, maxDepth: int, minDepth: int, gatesParameters: dict):
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