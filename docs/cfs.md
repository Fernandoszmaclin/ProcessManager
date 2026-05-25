# Escalonador CFS

## Requisitos do trabalho

O trabalho pede um pequeno modulo de gerenciamento de processos com
escalonamento preemptivo. A entrada deve ter este formato:

```text
algoritmoDeEscalonamento|fracaoDeCPU
momentoDeCriacao|PID|tempoDeExecucao|prioridadeOuBilhetes
```

Cada linha depois da primeira representa um processo. O programa deve:

- criar processos no tempo indicado por `momentoDeCriacao`;
- escolher qual processo fica na CPU;
- manter o processo na CPU ate acabar sua fatia de CPU ou finalizar;
- mostrar na linha do tempo qual PID executou e quanto tempo ainda falta;
- ao final, mostrar o tempo total desde a criacao ate a conclusao e o tempo em
  que o processo ficou no estado pronto.

Neste projeto foi implementado somente o algoritmo CFS, conforme solicitado.

## Como executar CFS

Use `CFS` na primeira linha do arquivo de entrada:

```text
CFS|2
0|P1|6|0
0|P2|4|0
1|P3|3|0
```

Depois execute:

```bash
python3 -m process_manager entradaEscalonador.txt
```

No Windows, se `python3` nao estiver disponivel:

```powershell
python -m process_manager entradaEscalonador.txt
```

## Funcionamento do script

1. `process_manager/main.py` recebe o caminho do arquivo pela linha de comando.
2. `process_manager/parser.py` le a entrada, monta a configuracao da simulacao
   e cria os objetos `Process`.
3. `process_manager/scheduler_factory.py` verifica o nome do algoritmo. Quando
   ele recebe `CFS`, instancia `CFSScheduler`.
4. `process_manager/simulation.py` controla o relogio da simulacao:
   - admite novos processos quando chega o tempo de criacao;
   - pergunta ao escalonador qual processo deve executar;
   - executa no maximo `fracaoDeCPU` unidades de tempo por vez;
   - atualiza o tempo em estado pronto dos processos que ficaram esperando;
   - finaliza o processo ou devolve ele ao escalonador.
5. `process_manager/report.py` imprime a linha do tempo e o resumo final.

## Como o CFS foi implementado

O CFS real do Linux usa uma arvore ordenada por `vruntime` para sempre escolher
a tarefa que recebeu menos tempo justo de CPU. Nesta versao didatica, a mesma
ideia foi aplicada com uma lista simples porque o projeto e pequeno.

O arquivo `process_manager/schedulers/cfs.py` mantem:

- `_ready`: lista de processos prontos;
- `_vruntime_by_pid`: tempo virtual acumulado de cada PID;
- `_executed_by_pid`: quanto cada processo ja executou de fato.

Quando um processo novo entra na fila, ele recebe o menor `vruntime` entre os
processos prontos. Isso evita que um processo novo seja colocado muito atras na
ordem de execucao.

Quando o simulador chama `pick_next`, o CFS escolhe o processo com menor
`vruntime`. Em caso de empate, usa `creation_time` e depois `pid` para deixar o
resultado deterministico.

Quando a fatia de CPU termina e o processo ainda nao finalizou, o simulador
chama `on_process_preempted`. Nesse momento o CFS calcula quanto o processo
executou na ultima fatia e soma esse valor ao seu `vruntime`. Depois coloca o
processo de volta na fila de prontos.

Como todos os processos aumentam o `vruntime` conforme usam CPU, quem executou
menos tende a ser escolhido primeiro. Assim o tempo de CPU fica distribuido de
forma mais equilibrada entre os processos prontos.
