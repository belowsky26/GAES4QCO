class Circuit:
    def __init__(self, n_qubits, m_gates) -> None:
        self.n_qubits = n_qubits
        self.m_gates = m_gates
        self.gates = [[] for _ in range(m_gates)]
        self.fitness = None
        self.circuit = None
    
    def constructCircuit(self):
        self.circuit = QuantumCircuit(self.n_qubits)
        for gatesInDepth in self.gates:
            for gate in gatesInDepth:
                parametersString = ""
                for type, h, *parameter in gate.parameters:
                    try:
                        parametersString += f"{parameter[0]}"
                    except Exception as e:
                        print(f"Parameter errado = {type}, {h}, {parameter}")
                    if type == "float":
                        parametersString += f"*{pi}"
                    parametersString += ","
                parametersString = parametersString[:-1]
                #print(f"self.circuit.{gate.name}({parametersString})")
                exec(f"self.circuit.{gate.name}({parametersString})")
    
    def __str__(self) -> str:
        gatesString = ""
        for gatesDepth in self.gates:
            gatesString += "    Profundidade:"
            for gate in gatesDepth:
                gatesString += f"       {gate}\n"
        return f"Circuit [{self.n_qubits} x {self.m_gates}] -- Fitness = {self.fitness}\n{gatesString}"

class Gate:
    def __init__(self, name:str, affected_qubits:list[int], gateInfo:dict={}) -> None:
        self.name =  name
        self.affected_qubits = affected_qubits
        self.parameters = gateInfo["combinations"][0]
        #self.gateInfo = gateInfo #? {'combinations': [[['str', 1], ['list[int]', 1, [0]]], 1, 0, 1]}} or {'combinations': [[['int', 1, 2]], 1, 0, 0]}
    def __str__(self) -> str:
        return f"[{self.name}] -> {self.affected_qubits}   -----------  {self.parameters}"

class StepSize:
    def __init__(self) -> None:
        self.mean = 0
        self.variation = 0.5
        self.history = []
        self.c = 0.9
    def resetVariation(self):
        lenLimit = len(self.history) if len(self.history) < 5 else 5
        success = sum(self.history[-lenLimit:])/lenLimit
        if success > 1/5:
            self.variation /= self.c
        elif success < 1/5:
            self.variation *= self.c
    def addHit(self, hit:bool):
        self.history.append(int(hit))
        self.resetVariation()


def saveJson(dados:dict, nameFile:str):
    with open(nameFile, "w") as arquivo:
        json.dump(dados, arquivo, indent=4)

def createGateToListQubits(qubitsFree:list, gateParameters:dict):
    structLocal = deepcopy(gateParameters)
    for gateName, gateInfo in structLocal.items():
        gateInfo["info"]["combinations"] = [combination for combination in gateInfo["info"]["combinations"] if combination[1] <= len(qubitsFree)]
    
    structLocal = {gateName: gateInfo for gateName, gateInfo in structLocal.items() if len(gateInfo["info"]["combinations"])}
    gateName, gateInfo = random.choice(list(structLocal.items()))
    gateInfo = gateInfo.copy()
    gateCounts = gateInfo.pop("info").copy()
    gateCounts["combinations"] = list(random.choice(gateCounts["combinations"]))
    gateCounts["combinations"][0] = list(gateCounts["combinations"][0])
    countFree = len(qubitsFree) - gateCounts["combinations"][1]
    types = []
    for type in gateCounts["combinations"][0]:
        type = [type, 1 if type != "None" else 0]
        if type.count("list[int]"):
            addCount = random.randint(0, countFree)
            countFree -= addCount
            type[1] += addCount
            gateCounts["combinations"][1] += addCount
        types.append(type)
    gateCounts["combinations"][0] = types
    
    qubitsChoice = random.sample(qubitsFree, gateCounts["combinations"][1])
    affectedQubits = list(qubitsChoice)
    qubitsFree = list(set(qubitsFree).difference(qubitsChoice))
    for param in gateCounts["combinations"][0]:
        if param[0] in ["int", "list[int]"]:
            qubits = random.sample(qubitsChoice, param[1])
            qubitsChoice = list(set(qubitsChoice).difference(qubits))
            if  param[0] == "int":
                qubits = qubits[0]
            param.append(qubits)
        elif param[0] == "float":
            param.append(random.uniform(0, 2))
            param.append(StepSize())
    gate = Gate(gateName, affectedQubits, gateCounts)
    return gate, qubitsFree

def createCircuit(numQubits:int, maxDepth:int, minDepth:int, gatesParameters:dict):
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
