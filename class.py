class circuit:
    def __init__(self, n_qubits, m_gates) -> None:
        self.n_qubits = n_qubits
        self.m_gates = m_gates
        self.matrix = [[None for _ in range(m_gates)] for _ in range(n_qubits)]
        self.fitness = None
        
class gate:
    def __init__(self, name:str, qubit_id:int, affected_qubits:list, parameters:list = [], control_qubits:list = [],  target_qubits:list = []) -> None:
        name =  name
        qubit_id = qubit_id
        affected_qubits = affected_qubits
        parameters = parameters
        control_qubits= control_qubits
        target_qubits= target_qubits