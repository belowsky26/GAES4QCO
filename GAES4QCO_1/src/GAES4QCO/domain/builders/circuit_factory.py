
class CircuitFactory:
    def __init__(self, numQubits: int, maxDepth: int, minDepth: int, gatesParameters: dict):
        self.numQubits = numQubits

    def createCircuit(numQubits: int, maxDepth: int, minDepth: int, gatesParameters: dict):
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