import json
def openFIle(gate):
    with open(gate, 'r') as f:
        data = json.load(f)
        return data
    
def fidelityFitnessFunction(circuit):
    pass