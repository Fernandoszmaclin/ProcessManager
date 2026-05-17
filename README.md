# Process Manager

Simulador em Python para comparar algoritmos de escalonamento preemptivo:

- Round Robin / alternancia circular
- Prioridade
- Loteria
- CFS

## Estrutura

```text
process_manager/
  main.py                   # entrada via terminal
  models.py                 # Process, estados e configuracao
  parser.py                 # leitura do arquivo de entrada
  report.py                 # impressao da linha do tempo e resumo
  simulation.py             # loop comum da simulacao
  scheduler_factory.py      # escolhe o escalonador pelo nome
  schedulers/
    base.py                 # contrato comum dos escalonadores
    round_robin.py          # parte do Round Robin
    priority.py             # parte da prioridade
    lottery.py              # parte da loteria
    cfs.py                  # parte do CFS
examples/
  geradorEntrada.py         # gera entradaEscalonador.txt
```

## Formato de entrada

As entradas sao geradas por `examples/geradorEntrada.py`, entao o parser assume o
formato abaixo sem validar casos especiais.

```text
algoritmoDeEscalonamento|fracaoDeCPU
momentoDeCriacao|PID|tempoDeExecucao|prioridadeOuBilhetes
```

## Como executar

Gere primeiro o arquivo de entrada:

```bash
python3 examples/geradorEntrada.py
```

O gerador cria `entradaEscalonador.txt` na pasta onde o comando foi executado.
Depois execute o simulador apontando para esse arquivo:

```bash
python3 -m process_manager entradaEscalonador.txt
```

## Divisao sugerida

Cada pessoa do grupo deve implementar apenas o arquivo do seu algoritmo dentro de
`process_manager/schedulers/`. O parser, o loop da simulacao e o relatorio ficam
compartilhados para manter a comparacao justa entre os algoritmos.

O contrato de cada escalonador esta em `process_manager/schedulers/base.py`:

- `add_process`: recebe um processo que acabou de entrar no estado pronto.
- `pick_next`: escolhe e remove o proximo processo da estrutura de prontos.
- `on_process_preempted`: recebe de volta um processo que usou a fatia de CPU e ainda nao terminou.
- `has_ready_process`: informa se existe algum processo pronto.
- `ready_processes`: devolve os processos prontos para o simulador calcular tempo de espera.
