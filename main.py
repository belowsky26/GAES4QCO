from copy import deepcopy
from math import pi
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector, state_fidelity
from copy import deepcopy
import itertools
import inspect
import random
import math
import numpy as np
import time

CROSSOVER = 80
MUTATION = 5

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
        if success > 3/5:
            self.variation /= self.c
        elif success < 3/5:
            self.variation *= self.c
    def addHit(self, hit:bool):
        self.history.append(int(hit))
        self.resetVariation()

def createGateToListQubits(qubitsFree:list, structLocal:dict):
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
        elif param[0] == "None":
            param.append(None)
    gate = Gate(gateName, affectedQubits, gateCounts)
    return gate, qubitsFree

def createCircuit(numQubits, maxDepth, minDepth, gatesParameters:dict):
    depth = random.randint(minDepth, maxDepth)
    circuit = Circuit(numQubits, depth)
    for y in range(depth):
        gatesParametersLocal = gatesParameters.copy()
        qubitsFree = list(range(numQubits))
        while qubitsFree:
            gate, qubitsFree = createGateToListQubits(qubitsFree, gatesParametersLocal)
            circuit.gates[y].append(gate)
    circuit.constructCircuit()
    return circuit

def initialPopulation(numPopulation:int, numQubits:int, maxDepth:int, minDepth:int, gatesParameters:dict):
    population = []
    for _ in range(numPopulation):
        circuit = createCircuit(numQubits, maxDepth, minDepth, gatesParameters)
        population.append(circuit)
    return population

def fidelityFitnessFunction(circuit:Circuit, svTarget:Statevector):
    svTargetLocal = Statevector(svTarget)
    svSolution = Statevector.from_instruction(circuit.circuit)
    fidelity = state_fidelity(svSolution, svTargetLocal)
    return max(0, fidelity)

def applyFitnessIntoCircuit(circuit:Circuit, svTarget:Statevector):
    if not circuit.fitness:
        circuit.constructCircuit()
        circuit.fitness = fidelityFitnessFunction(circuit, svTarget)
    return circuit

def selection(population:list[Circuit], svTarget:Statevector, lenPopulationNext:int):
    populationLocal = deepcopy(population)
    for i, circuit in enumerate(populationLocal):
        populationLocal[i] = applyFitnessIntoCircuit(circuit, svTarget)
    champion = max(populationLocal, key=lambda circuit: circuit.fitness)
    champions = []
    champions.append(champion)
    for _ in range(lenPopulationNext - len(champions)):
        group = random.sample(populationLocal, 2)
        champion = max(group, key=lambda circuit: circuit.fitness)
        champions.append(champion)
    return champions

def crossover(population:list[Circuit], gatesParameters:dict):
    populationLocal = deepcopy(population)
    gatesParametersLocal = gatesParameters.copy()
    random.shuffle(populationLocal)
    populationNextGen = []
    for i in range(0, len(populationLocal), 2):
        circuit1 = populationLocal[i]
        circuit2 = populationLocal[i+1]
        if random.random()%100 < CROSSOVER:
            circuitGates1 = []
            circuitGates2 = []
            minDepth = circuit1.m_gates if circuit1.m_gates <= circuit2.m_gates else circuit2.m_gates
            points = random.choices([0, 1], k=minDepth)
            if not points.count(1):
                points[random.randint(0, minDepth - 1)] = 1
            elif not points.count(0):
                points[random.randint(0, minDepth - 1)] = 0
            
            for y in range(minDepth):
                if points[y] == 0:
                    circuitGates1.append(list(circuit1.gates[y]))
                    circuitGates2.append(list(circuit2.gates[y]))
                else:
                    circuitGates1.append(list(circuit2.gates[y]))
                    circuitGates2.append(list(circuit1.gates[y]))
            if minDepth < circuit1.m_gates:
                circuitGates1 += list(circuit1.gates[minDepth:])
            elif minDepth < circuit2.m_gates:
                circuitGates2 += list(circuit2.gates[minDepth:])
            
            nQubits = circuit1.n_qubits if circuit1.n_qubits >= circuit2.n_qubits else circuit2.n_qubits
            circuit1 = Circuit(nQubits, circuit1.m_gates)
            circuit1.gates = circuitGates1
            circuit2 = Circuit(nQubits, circuit2.m_gates)
            circuit2.gates = circuitGates2
            gatesParametersLocal = {"id": gatesParametersLocal["id"]} # Substituir os qubits Livres por I Gates
            for circuitNextGen in [circuit1, circuit2]:
                for y, gateDepth in enumerate(circuitNextGen.gates):
                    qubitsFree = list(range(0, circuit1.n_qubits))
                    for gate in gateDepth:
                        qubitsFree = list(set(qubitsFree).difference(gate.affected_qubits))
                    while qubitsFree:
                        gate, qubitsFree = createGateToListQubits(qubitsFree, gatesParametersLocal)
                        circuitNextGen.gates[y].append(gate)
        populationNextGen.append(circuit1)
        populationNextGen.append(circuit2)
    return populationNextGen

def mutation(population:list[Circuit], svTarget:Statevector, maxDepth:int, gatesParameters:dict):
    populationLocal = deepcopy(population)
    populationNextGen = []
    for circuit in populationLocal:
        if random.random()%100 < MUTATION:
            mutations = [mutationSingleGateFlip, mutationNumberGates]
            depthQubitList = [(y, x) for y, gatesDepth in enumerate(circuit.gates) for x, gate in enumerate(gatesDepth) if gate.name.count("c") and len(gate.affected_qubits) > 1]
            if len(depthQubitList):
                mutations.append(mutationSwapControlQubit)
            listGateParamFloat = [(y, x, p) for y, gatesDepth in enumerate(circuit.gates) for x, gate in enumerate(gatesDepth) for p, parameter in enumerate(gate.parameters) if parameter[0] == "float"]
            if len(listGateParamFloat):
                mutations.append(mutationGateParameters)
            if circuit.m_gates > 1:
                mutations.append(mutationSwapColumns)
            mutationSelected = random.choice(mutations)
            if mutationSelected == mutationGateParameters:
                circuit = mutationSelected(circuit, svTarget, listGateParamFloat)
            elif mutationSelected == mutationNumberGates:
                circuit = mutationSelected(circuit, maxDepth, gatesParameters)
            elif mutationSelected == mutationSwapControlQubit:
                circuit = mutationSelected(circuit, depthQubitList)
            elif mutationSelected == mutationSingleGateFlip:
                circuit = mutationSelected(circuit, gatesParameters)
            else:
                circuit = mutationSelected(circuit)
            circuit.fitness = None
            circuit.circuit = None
        populationNextGen.append(circuit)
    return populationNextGen

def mutationSingleGateFlip(circuit:Circuit, gatesParameters:dict):
    circuitLocal = deepcopy(circuit)
    gatesParametersLocal = gatesParameters.copy()
    depthChoice = random.randint(0, circuitLocal.m_gates - 1)
    gateChoice = random.randint(0, len(circuitLocal.gates[depthChoice]) - 1)
    gateSelected = circuitLocal.gates[depthChoice].pop(gateChoice)
    qubitsFree = list(gateSelected.affected_qubits)
    while qubitsFree:
        gateNew, qubitsFree = createGateToListQubits(qubitsFree, gatesParametersLocal)
        circuitLocal.gates[depthChoice].append(gateNew)
    return circuitLocal

def mutationSwapColumns(circuit:Circuit):
    circuitLocal = deepcopy(circuit)
    column1, column2 = random.sample(list(range(0, circuitLocal.m_gates)), 2)
    circuitLocal.gates[column1], circuitLocal.gates[column2] = circuitLocal.gates[column2], circuitLocal.gates[column1]
    return circuitLocal

def mutationSwapControlQubit(circuit:Circuit, depthQubitList:list[tuple]):
    circuitLocal = deepcopy(circuit)
    depth, qubit = random.choice(depthQubitList)
    gateSelected = circuitLocal.gates[depth].pop(qubit)
    indexInitialQubits = len(gateSelected.parameters) - len(gateSelected.affected_qubits)
    gateSelected.parameters, parametersQubitLocal = [], gateSelected.parameters[indexInitialQubits:] if indexInitialQubits == 0 else gateSelected.parameters[:indexInitialQubits], gateSelected.parameters[indexInitialQubits:]
    controlCount = gateSelected.name.count("c")
    qubitsControl = deepcopy(parametersQubitLocal[:controlCount])
    qubitsTarget = deepcopy(parametersQubitLocal[controlCount:])
    parametersQubitLocal = [random.choice(qubitsTarget)]
    qubitsTarget.remove(parametersQubitLocal[0])
    qubits = qubitsControl + qubitsTarget
    random.shuffle(qubits)
    parametersQubitLocal += qubits
    gateSelected.parameters += parametersQubitLocal
    circuitLocal.gates[depth].append(gateSelected)
    return circuitLocal

def mutationNumberGates(circuit:Circuit, maxDepth:int, gatesParameters:dict):
    circuitLocal = deepcopy(circuit)
    gauss = random.gauss(0, 1)
    if gauss == 0:
        random.choice([-1, 1])
    if circuitLocal.m_gates + gauss < 1:
        if circuitLocal.m_gates == 1:
            gauss = -math.floor(gauss)
        else:
            gauss = 1 - circuitLocal.m_gates
    elif circuitLocal.m_gates + gauss > maxDepth:
        if circuitLocal.m_gates == maxDepth:
            gauss = -math.ceil(gauss)
        else:
            gauss = maxDepth - circuitLocal.m_gates
    else:
        if gauss > 0:
            gauss = math.ceil(gauss)
        elif gauss < 0:
            gauss = math.floor(gauss)
    if gauss < 0:
        for _ in range(-gauss):
            gate = random.choice(circuitLocal.gates)
            circuitLocal.gates.remove(gate)
    else:
        for _ in range(gauss):
            if  circuitLocal.m_gates + maxDepth:
                circuitLocal.gates.append([])
                qubitsFree = list(range(circuitLocal.n_qubits))
                gatesParametersLocal = gatesParameters.copy()
                while qubitsFree:
                    gate, qubitsFree = createGateToListQubits(qubitsFree, gatesParametersLocal)
                    circuitLocal.gates[len(circuitLocal.gates) - 1].append(gate)
    circuitLocal.m_gates = circuitLocal.m_gates + gauss
    return circuitLocal

def mutationGateParameters(circuit:Circuit, svTarget:Statevector, listGateParamFloat:list[tuple]):
    circuitLocal = deepcopy(circuit)
    circuitLocal = applyFitnessIntoCircuit(circuitLocal, svTarget)
    fitnessLast = circuitLocal.fitness
    y, x, p = random.choice(listGateParamFloat)
    circuitLocal.gates[y][x].parameters[p][2] = abs(circuitLocal.gates[y][x].parameters[p][2] + random.gauss(0, circuitLocal.gates[y][x].parameters[p][3].variation))%2
    circuitLocal = applyFitnessIntoCircuit(circuitLocal, svTarget)
    circuitLocal.gates[y][x].parameters[p][3].addHit(circuitLocal.fitness > fitnessLast)
    return circuitLocal

def generations(population:list[Circuit], maxGeneration:int, maxDepth:int, svTarget:Statevector, gatesParameters:dict):
    populationLocal = deepcopy(population)
    populationGen = []
    for gen in range(maxGeneration):
        print(gen)
        populationSelected = selection(populationLocal, svTarget, len(populationLocal))
        populationNextGen = crossover(populationSelected, gatesParameters)
        populationNextGen = mutation(populationNextGen, svTarget, maxDepth, gatesParameters)
        populationLocal = selection(populationLocal + populationNextGen, svTarget, len(populationLocal))
        populationGen.append(populationLocal)
    return populationGen


def getGatesIntoModule(module):
    removeString = ['barrier', 'pauli', 'append', 'cast','clear', 'compose','control', 'copy', 'decompose', 'delay', 'depth', 'draw', 'initialize', 'inverse', 'measure','power', 'repeat', 'reset', 'size','store', 'switch', 'tensor', 'unitary', 'width']
    # Talvez -> ctrl_state
    gates = [(name,cls) for name, cls in inspect.getmembers(module) if inspect.isfunction(cls) and not (name.count('add') or name.count('_'))]
    gates = [(name, cls) for name, cls in gates if not name in removeString]
    return gates

def getGatesWithTypesParameters(classes):
    classesLocal = deepcopy(classes)
    typesDict = {
        "QubitSpecifier": ["int"],
        "<class 'qiskit.circuit.quantumregister.Qubit'>": ["int"],
        "Sequence[QubitSpecifier] | None": ["int", "None"],
        "typing.Union[qiskit.circuit.quantumregister.QuantumRegister, typing.List[qiskit.circuit.quantumregister.Qubit]]": ["int", "list[int]"],
        "Sequence[QubitSpecifier]": ["list[int]"],
        "QubitSpecifier | Sequence[QubitSpecifier] | None": ["int", "list[int]", "None"],
        "typing.Union[qiskit.circuit.quantumregister.QuantumRegister, typing.Tuple[qiskit.circuit.quantumregister.QuantumRegister, int], NoneType]": ["int", "list[int]", "None"],
        "typing.Union[qiskit.circuit.parameterexpression.ParameterExpression, float]": ["float"],
        "ParameterValueType": ["float"],
        "str": ["str"],
    }
    gatesParameters = {}
    parametersOk = ['pauli_string', 'vz', 'target_qubit1', 'vy', 'phi','vx', 'qargs', 'control_qubits', 'q_target', 'target_qubit2', 'qubits', 'theta', 'qubit2', 'q_controls', 'target_qubit','gamma', 'qubit', 'control_qubit3', 'ancilla_qubits', 'control_qubit1', 'control_qubit', 'q_ancillae', 'control_qubit2', 'qubit1', 'lam']
    # Iterando sobre os parâmetros
    for name, classe in classesLocal:
        init_signature = inspect.signature(classe)
        #print(classe)
        gatesParameters[name] = dict()
        for parameter_name, parameter in init_signature.parameters.items():
            if parameter_name in parametersOk:
                gatesParameters[name][parameter_name] = typesDict[str(parameter.annotation)]
                #print(f"    Parâmetro: {parameter_name}, Tipo anotado: {parameter.annotation} -> {type(parameter.annotation)}")
    #parameters = [name for gateName, gateInfo in gatesParameters.items() for name in gateInfo.keys()]
    #print(set(parameters))
    return gatesParameters

def getGatesWithCombinations(gates):
    gatesLocal = deepcopy(gates)
    for gatename, gateInfo in gatesLocal.items():
        valores = [list(v) for v in gateInfo.values()]
        combinacoes = itertools.product(*valores)
        gateInfo["info"] = {}
        # (Qubits, Parameters, Strs)
        gateInfo["info"]["combinations"] = [(x, x.count("int") + x.count("list[int]"), x.count("float"), x.count("str")) for x in combinacoes]
    return gatesLocal

def main(seed:int, numQubits:int, maxDepth:int, minDepth:int, lenPopulation:int, countGenerations:int):
    print(f"---   TEST {seed}   ---")
    inicio = time.time()
    classes = getGatesIntoModule(QuantumCircuit)
    gatesParameters = getGatesWithTypesParameters(classes)
    gatesParameters = getGatesWithCombinations(gatesParameters)
    random.seed(seed)
    circuitTarget = createCircuit(numQubits, maxDepth, maxDepth, gatesParameters)
    stateTarget = Statevector.from_instruction(circuitTarget.circuit)
    populationInitial = initialPopulation(lenPopulation, circuitTarget.n_qubits, circuitTarget.m_gates, minDepth, gatesParameters)
    for x, circuit in enumerate(populationInitial):
        populationInitial[x] = applyFitnessIntoCircuit(circuit, stateTarget)
    populationGen = generations(populationInitial, countGenerations, circuitTarget.m_gates, stateTarget, gatesParameters)
    fim = time.time() - inicio
    print(f"Fim Test {seed} -- {fim}")
    result = {
        "target": {
            "circuit": circuitTarget,
            "stateVector": stateTarget
        },
        "populationInitial": {
            "list": populationInitial,
            "bestCircuit": max(populationInitial, key=lambda x: x.fitness),
            "worseCircuit": min(populationInitial, key=lambda x: x.fitness)
        },
        "populationGen": {
            "list": populationGen,
            "bestCircuits": [max(population, key=lambda x: x.fitness) for population in populationGen],
            "worseCircuits": [max(population, key=lambda x: x.fitness) for population in populationGen],
            "fitnessAvg": [sum(x.fitness for x in population)/len(population) for population in populationGen],
            "fitnessStd": [float(np.std(populationFitness, ddof=0)) for populationFitness in ([[x.fitness for x in geracao if x.fitness >= 0.3] for geracao in populationGen])]
        }
    }
    result["populationGen"]["lowerBound"] = [max(result["populationGen"]["fitnessAvg"][i] - result["populationGen"]["fitnessStd"][i], 0) for i in range(len(populationGen))]
    result["populationGen"]["upperBound"] = [min(result["populationGen"]["fitnessAvg"][i] + result["populationGen"]["fitnessStd"][i], 1) for i in range(len(populationGen))]
    return result

def multProcessesTest(seed:int, countTest:int, numQubits:int, maxDepth:int, minDepth:int, lenPopulation:int, countGenerations:int):
    from multiprocessing import Pool
    parameters = [[i, numQubits, maxDepth, minDepth, lenPopulation, countGenerations] for i in range(seed, seed+countTest)]
    with Pool(countTest) as pool:
        print("Iniciando todos")
        inicio = time.time()
        result = pool.starmap(main, parameters)  # Replace ... with your list of arguments
        fim = time.time() - inicio
        print(f"Fim de todos -- {fim}")
        return result

if __name__ == "__main__":
    results = multProcessesTest(seed=10, countTest=10, numQubits=4, maxDepth=20, minDepth=1, lenPopulation=200, countGenerations=1)