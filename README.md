# Simulador de Escalonamento - Base Fernando

Esta base implementa apenas o escopo arquitetural, o nucleo da simulacao e o
algoritmo CFS. Round Robin, Prioridade e Loteria ficam como modulos externos da
equipe, integrados futuramente pelo contrato `Scheduler`.

## Executar demo

```bash
python examples/run_cfs_demo.py
```

## Estrutura

```text
scheduler/
├── core/
│   ├── process.py
│   └── scheduler.py
├── simulation/
│   └── engine.py
└── algorithms/
    ├── cfs.py
    └── stubs.py
```

