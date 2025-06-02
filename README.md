# Relatório de Resultados do Algoritmo Genético
## Ambiente Virtual
Para garantir a reprodutibilidade dos resultados, utilize um ambiente virtual:
```bash
pip install -r requirements.txt
```
## Configuração do Algoritmo Genético
### Componentes:
- **Taxa de Cruzamento**: 80%
- **Taxa de Mutação**: 8%
- **Cromossomo**: Gates e Gates com EE aplicada
    ```python
    class Gate:
        def __init__(self, name:str, affected_qubits:list[int], gateInfo:dict={}) -> None:
            self.name =  name
            self.affected_qubits = affected_qubits
            self.parameters = gateInfo["combinations"][0]
    ```
    ```python
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
    ```
- **Indivíduos**: Circuitos
    ```python
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
                        parametersString += f"{parameter[0]}"
                        if type == "float":
                            parametersString += f"*{pi}"
                        parametersString += ","
                    parametersString = parametersString[:-1]
                    exec(f"self.circuit.{gate.name}({parametersString})")
    ```
- **População**: 200
    ```python
    def initialPopulation(numPopulation:int, numQubits:int, maxDepth:int, minDepth:int, gatesParameters:dict):
        gatesParametersLocal = deepcopy(gatesParameters)
        population = []
        for _ in range(numPopulation):
            circuit = createCircuit(numQubits, maxDepth, minDepth, gatesParametersLocal)
            population.append(circuit)
        return population
    ```
- **Gerações**: 1000
    ```python
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
    ```
### Principais Funções do Algoritmo:
- **Aptidão**: Recebe o Circuito solução e o Statevector alvo e retorna a fidelidade entre eles
    ```python
    def fidelityFitnessFunction(circuit:Circuit, svTarget:Statevector):
        svTargetLocal = Statevector(svTarget)
        svSolution = Statevector.from_instruction(circuit.circuit)
        fidelity = state_fidelity(svSolution, svTargetLocal)
        return max(0, fidelity)
    ```
- **Seleção de Indivíduos**: Recebe a população e seleciona pelo menos 1x melhor indivíduo e em seguida realiza torneio até preencher todas as vagas solicitadas (parenteSelection = 2xlen(population) e suvivorSelection = len(population))
    ```python
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
    ```
- **Cruzamento**: Recebe a população e as gates disponíveis e realiza um cruzamento entre pares de indivíduos. Cada par irá realizar cruzamento por múltiplos pontos, sempre respeitando a profundidade dos indivíduos.
    ```python
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
                # Substituir os qubits Livres por outras Gates
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
    ```
- **Mutação**: Verifica e aplica mutação a cada indivíduo respeitando os seus limites e suas particularidades (EE). Ex: Caso ele não tenha Gates de Controle a mutação *`mutationSwapControlQubit`* não irá participar do sorteio.
    ```python
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
    ```
## Código Fonte e Experimentos
- **Código principal**:**`main.py`** contém o código do algoritmo genético desenvolvido.
- **Experimentos**: O notebook **`Seed100-109.ipynb`** pode ser utilizado para executar os testes.
## Resultados
### Melhor resultado
O melhor resultado foi obtido com a semente 103, alcançando um valor de fitness de 99.23%.
- **Comparação Visual**

| Descrição | Imagem |
|---|---|
|Resultado obtido|<img src="Antigo/files/Teste_103_Best_0.992305.png" alt="Resultado obtido com a semente 103">|
|Circuito Alvo|<img src="Antigo/files/Target_103.png" alt="Resultado esperado">|
|Circuito otimizado|<img src="Antigo/files/Best_103.png" alt="Circuito otimizado">|

**Observação**: As imagens acima demonstram a qualidade da solução encontrada pelo algoritmo, que possui profundidade 7, em comparação com o circuito alvo com profundidade 20.

### Média dos Resultado
O resultado médio foi calculado a partir de 10 testes com sementes entre 100 e 109, aplicando o intervalo de confiança de 95%.
- **Comparação Visual**

| Descrição | Imagem |
|---|---|
|Resultado Testes|<img src="Antigo/files/Teste_Global_100-109.png" alt="Resultado médio">|
|Resultado Alvo |<img src="Antigo/files/Teste_Comparar.png" alt="Resultado Alvo">|

**Observação**: As imagens acima demonstram que ambos algoritmos possuem resultados próximos e com convergências parecidas. Entretanto, os resultados dos testes demonstram ter taxas superiores tanto no melhor fitness quanto no fitness médio,com ~94.9% em comparação a ~83% de melhor fitness e com ~72,5% em comparação a ~67% de fitness médio.
