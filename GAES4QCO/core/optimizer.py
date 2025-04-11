def initialPopulation(numPopulation:int, numQubits:int, maxDepth:int, minDepth:int, gatesParameters:dict):
    gatesParametersLocal = deepcopy(gatesParameters)
    population = []
    for _ in range(numPopulation):
        circuit = createCircuit(numQubits, maxDepth, minDepth, gatesParametersLocal)
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

def selection(population:list[Circuit], svTarget:Statevector, survivor:bool=False):
    populationLocal = deepcopy(population)
    for i, circuit in enumerate(populationLocal):
        populationLocal[i] = applyFitnessIntoCircuit(circuit, svTarget)
    champion = max(populationLocal, key=lambda circuit: circuit.fitness)
    champions = []
    champions.append(champion)
    if not survivor:
        lenNextGen = len(populationLocal)
        for _ in range(1, lenNextGen):
            group = random.sample(populationLocal, 2)
            champion = max(group, key=lambda circuit: circuit.fitness)
            champions.append(champion)
    else:
        lenNextGen = len(populationLocal)//2
        for _ in range(1, lenNextGen):
            group = random.sample(populationLocal, 2)
            champion = max(group, key=lambda circuit: circuit.fitness)
            champions.append(champion)
            populationLocal.remove(champion)            
    return champions

def crossover(population:list[Circuit], gatesParameters:dict):
    populationLocal = deepcopy(population)
    gatesParametersLocal = deepcopy(gatesParameters)
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
            #gatesParametersLocal = {"id": gatesParametersLocal["id"]} # Substituir os qubits Livres por I Gates
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
    gatesParametersLocal = deepcopy(gatesParameters)
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
    indexInitialQubits = len([param for param in gateSelected.parameters if param[0] == "float"])
    parametersQubitLocal, gateSelected.parameters = (list(gateSelected.parameters), []) if indexInitialQubits == 0 else (list(gateSelected.parameters[indexInitialQubits:]), list(gateSelected.parameters[:indexInitialQubits]))
    qubits = list(gateSelected.affected_qubits)
    paramControl = gateSelected.name.count("c")
    countControl = sum([1 if x[0] == "int" else len(x[2]) for x in parametersQubitLocal[:paramControl]])
    newQubits = [qubits.pop(random.randint(countControl, len(qubits) - 1))]
    random.shuffle(qubits)
    newQubits += qubits
    index = 0
    for i, param in enumerate(parametersQubitLocal):
        if param[0] == "int":
            parametersQubitLocal[i][2] = newQubits[index]
            index += 1
        else:
            parametersQubitLocal[i][2] = newQubits[index:index+len(param[2])]
            index += len(param[2])
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
                gatesParametersLocal = deepcopy(gatesParameters)
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

def generations(population:list[Circuit], maxGeneration:int, maxDepth:int, svTarget:Statevector, gatesParameters:dict, nameFile:str):
    populationLocal = deepcopy(population)
    jsonToSave = {
    "fitnessPopulationInitial": sorted([x.fitness for x in populationLocal]),
    "fitnessPopulationGen": [],
    "fitnessAvgPopulationGen":  [],
    "fitnessStdPopulationGen":  [],
    }
    for gen in range(maxGeneration):
        if gen % 50 == 0:
            print(f"Generation {gen}")
        populationSelected = selection(populationLocal, svTarget)
        populationNextGen = crossover(populationSelected, gatesParameters)
        populationSelected = None
        populationNextGen = mutation(populationNextGen, svTarget, maxDepth, gatesParameters)
        populationLocal = selection(populationLocal + populationNextGen, svTarget, survivor=True)
        populationNextGen = None
        jsonToSave["fitnessPopulationGen"].append(sorted([x.fitness for x in populationLocal]))
        jsonToSave["fitnessAvgPopulationGen"].append(sum(jsonToSave["fitnessPopulationGen"][-1])/len(jsonToSave["fitnessPopulationGen"][-1]))
        jsonToSave["fitnessStdPopulationGen"].append(np.std(jsonToSave["fitnessPopulationGen"][-1], ddof=0))
    saveJson(jsonToSave, nameFile)
    bestCircuit = max(populationLocal, key=lambda x: x.fitness)
    jsonToSave = None
    populationLocal = None
    return bestCircuit
