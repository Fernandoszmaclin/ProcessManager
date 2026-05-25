# Visao geral do projeto

## Objetivo

O projeto simula um gerenciador de processos de um sistema operacional. Ele le
um arquivo de entrada com processos, escolhe um escalonador e executa uma
simulacao de uso da CPU.

Durante a simulacao, cada processo passa por estados parecidos com os vistos em
Sistemas Operacionais:

- `NEW`: processo criado no arquivo, mas ainda nao chegou ao tempo de entrada;
- `READY`: processo pronto para executar, aguardando CPU;
- `RUNNING`: processo atualmente usando a CPU;
- `FINISHED`: processo terminou toda sua execucao.

## Estrutura de pastas

```text
process_manager/
  __main__.py              ponto de entrada para python -m process_manager
  main.py                  coordena leitura, escalonador, simulacao e relatorio
  parser.py                le o arquivo de entrada
  models.py                define Process, ProcessState e SimulationConfig
  scheduler_factory.py     escolhe a classe de escalonador
  simulation.py            executa o laco principal da simulacao
  report.py                imprime linha do tempo e resumo final
  schedulers/
    base.py                contrato comum dos escalonadores
    round_robin.py         alternancia circular
    priority.py            prioridade
    lottery.py             loteria, ainda nao implementado
    cfs.py                 Completely Fair Scheduler
```

## Entrada

O arquivo de entrada segue este formato:

```text
algoritmoDeEscalonamento|fracaoDeCPU
momentoDeCriacao|PID|tempoDeExecucao|prioridadeOuBilhetes
```

Exemplo usando CFS:

```text
CFS|2
0|P1|6|0
0|P2|4|0
1|P3|3|0
```

Campos:

- `algoritmoDeEscalonamento`: nome do algoritmo usado na simulacao;
- `fracaoDeCPU`: quantidade maxima de tempo que um processo fica na CPU por vez;
- `momentoDeCriacao`: instante em que o processo entra no sistema;
- `PID`: identificador do processo;
- `tempoDeExecucao`: tempo total necessario para terminar;
- `prioridadeOuBilhetes`: prioridade ou bilhetes, dependendo do algoritmo.

## Saida

O programa imprime duas partes.

A primeira e a linha do tempo:

```text
t=0..2: PID P1 na CPU, faltam 4
```

Isso significa que `P1` executou do tempo `0` ate o tempo `2` e ainda precisa de
mais `4` unidades de tempo para terminar.

A segunda e o resumo:

```text
PID | criado | terminou | execucao total | tempo pronto
```

- `criado`: momento em que o processo chegou ao sistema;
- `terminou`: momento em que finalizou;
- `execucao total`: tempo entre criacao e finalizacao;
- `tempo pronto`: tempo aguardando CPU no estado `READY`.

## Como executar

Gerar entrada pelo script auxiliar:

```bash
python3 examples/geradorEntrada.py
```

Executar simulador:

```bash
python3 -m process_manager entradaEscalonador.txt
```

No Windows, se `python3` nao estiver disponivel:

```powershell
python -m process_manager entradaEscalonador.txt
```
