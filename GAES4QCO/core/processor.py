def main(seed:int, numQubits:int, maxDepth:int, minDepth:int, lenPopulation:int, countGenerations:int, gatesParameters:dict):
    gatesParametersLocal = deepcopy(gatesParameters)
    print(f"---   TEST {seed}   ---")
    inicio = time.time()
    random.seed(seed)
    circuitTarget = createCircuit(numQubits, maxDepth, maxDepth, gatesParametersLocal)
    stateTarget = Statevector.from_instruction(circuitTarget.circuit)
    populationInitial = initialPopulation(lenPopulation, circuitTarget.n_qubits, circuitTarget.m_gates, minDepth, gatesParametersLocal)
    for x, circuit in enumerate(populationInitial):
        populationInitial[x] = applyFitnessIntoCircuit(circuit, stateTarget)
    bestCircuit = generations(populationInitial, countGenerations, circuitTarget.m_gates, stateTarget, gatesParametersLocal, f"data/Seed_{seed}.json")
    fim = time.time() - inicio
    print(f"Fim Test {seed} -- {fim}")
    return bestCircuit, circuitTarget

def multProcessesTest(seed:int, countTest:int, numQubits:int, maxDepth:int, minDepth:int, lenPopulation:int, countGenerations:int, gatesParameters:dict):
    parameters = [[i, numQubits, maxDepth, minDepth, lenPopulation, countGenerations, gatesParameters] for i in range(seed, seed+countTest)]
    num_processes = min(countTest, cpu_count())
    with Pool(num_processes) as pool:
        print("Iniciando todos")
        inicio = time.time()
        result = pool.starmap(main, parameters)  # Replace ... with your list of arguments
        fim = time.time() - inicio
        print(f"Fim de todos -- {fim}")
        return result