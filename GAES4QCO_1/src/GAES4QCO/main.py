# No seu ponto de entrada (Composition Root)

# from GAES4QCO.config import EvolutionConfig # Objeto que carrega suas configurações
from .domain.factories.gate_factory import GateFactory
from .domain.builders.step_size_builder import StepSizeBuilder
from .domain.builders.gate_builder import GateBuilder
from .domain.builders.column_component_builder import ColumnBuilder
from .domain.builders.circuit_builder import CircuitBuilder

# --- Montando a cadeia de dependências ---

# Carrega os parâmetros de um ponto central
config = {
    "step_size_initial_variation": 0.1,
    "step_size_c_factor": 0.85,
    "step_size_history_len": 20
}

# 1. Crie as dependências mais básicas
gate_factory = GateFactory()
step_size_builder = StepSizeBuilder(
    initial_variation=config["step_size_initial_variation"],
    c_factor=config["step_size_c_factor"],
    history_len=config["step_size_history_len"]
)

# 2. Injete as dependências nos builders de nível superior
gate_comp_builder = GateBuilder(gate_factory, step_size_builder)
column_builder = ColumnBuilder(gate_comp_builder)
circuit_builder = CircuitBuilder(column_builder)
# ... etc.

# --- Chamada final simples ---
circuit = circuit_builder.build(num_qubits=4, depth=20)
# print("Circuito gerado com StepSizes corretamente instanciados.")