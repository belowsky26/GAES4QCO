### Estrutura do Código:
```
src/
└── gaes4qco/
    ├── __init__.py
    │
    ├── evolutionary_algorithm/ # Feature: A lógica central da evolução
    │   ├── __init__.py
    │   ├── interfaces.py       # <<< NOVO: Contratos para as estratégias
    │   ├── population.py       # Entidade que agrupa os indivíduos
    │   ├── crossover.py        # Implementação concreta de ICrossoverStrategy
    │   ├── mutation.py         # Implementação concreta de IMutationStrategy
    │   └── selection.py        # Implementação concreta de ISelectionStrategy
    │
    ├── quantum_circuit/        # Feature: A representação do circuito e a comunicação com o hardware/simulador
    │   ├── __init__.py
    │   ├── interfaces.py       # <<< NOVO: Contrato para o Adapter do circuito
    │   ├── circuit.py          # Entidade 'Circuit' (representação agnóstica)
    │   ├── gate.py             # Entidade 'Gate' (representação agnóstica)
    │   └── qiskit_adapter.py   # Implementação concreta de IQuantumCircuitAdapter (Wrapper)
    │
    ├── optimization/           # Feature: O orquestrador de alto nível
    │   ├── __init__.py
    │   ├── interfaces.py       # <<< NOVO: Contrato para a função de avaliação (fitness)
    │   ├── optimizer.py        # Lógica de alto nível, depende apenas de INTERFACES
    │   └── fitness.py          # Implementação concreta de IFitnessEvaluator
    │
    └── shared/                 # Código e contratos compartilhados
        ├── __init__.py
        ├── exceptions.py       # Exceções customizadas
        └── value_objects.py    # Objetos de valor reutilizáveis (se houver)

```