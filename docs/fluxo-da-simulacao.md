# Fluxo da simulacao

## Entrada no programa

O arquivo `process_manager/__main__.py` chama `main()`. Isso permite executar o
projeto com:

```bash
python3 -m process_manager entradaEscalonador.txt
```

Em `process_manager/main.py`, o fluxo principal e:

1. ler o arquivo de entrada;
2. criar o escalonador pedido;
3. executar a simulacao;
4. imprimir o relatorio.

## Leitura da entrada

`process_manager/parser.py` abre o arquivo e separa os campos pelo caractere
`|`.

A primeira linha cria `SimulationConfig`, que guarda:

- `algorithm`: algoritmo escolhido;
- `cpu_fraction`: fatia maxima de CPU.

As demais linhas criam objetos `Process`. Depois, os processos sao ordenados por
`creation_time`, porque a simulacao precisa admitir primeiro quem chega antes.

## Criacao do escalonador

`process_manager/scheduler_factory.py` recebe o nome do algoritmo e instancia a
classe correta:

- `alternanciaCircular`: `RoundRobinScheduler`;
- `prioridade`: `PriorityScheduler`;
- `loteria`: `LotteryScheduler`;
- `CFS`: `CFSScheduler`.

Todos seguem o contrato definido em `process_manager/schedulers/base.py`.

## Contrato dos escalonadores

Todo escalonador precisa implementar:

- `add_process(process)`: adiciona processo na fila de prontos;
- `pick_next()`: escolhe e remove o proximo processo que vai para CPU;
- `on_process_preempted(process)`: recebe processo que nao terminou sua fatia;
- `has_ready_process()`: informa se existe processo pronto;
- `ready_processes()`: devolve processos prontos para atualizar tempo de espera.

Esse contrato permite trocar o algoritmo sem mudar o laco principal da
simulacao.

## Laco principal

`process_manager/simulation.py` controla o tempo com `current_time`.

Enquanto nem todos os processos terminarem:

1. processos cujo `creation_time` ja chegou entram no estado `READY`;
2. se nao houver processo pronto, o relogio avanca ate a proxima chegada;
3. o escalonador escolhe um processo com `pick_next()`;
4. o processo vai para `RUNNING`;
5. ele executa por `min(fracaoDeCPU, remaining_time)`;
6. a cada unidade de tempo:
   - processos prontos acumulam `ready_time`;
   - o relogio avanca;
   - o processo em CPU reduz `remaining_time`;
   - novos processos podem entrar no sistema;
7. a execucao da fatia entra na linha do tempo;
8. se `remaining_time` chegou a zero, o processo vira `FINISHED`;
9. se ainda falta tempo, ele volta para `READY` e retorna ao escalonador.

## Linha do tempo

Cada fatia executada gera um `TimelineEntry` com:

- `start_time`: inicio da fatia;
- `end_time`: fim da fatia;
- `pid`: processo que executou;
- `remaining_time`: tempo restante depois da fatia.

O relatorio imprime esses registros para mostrar exatamente qual processo usou
a CPU em cada intervalo.

## Metricas finais

O resumo usa dados guardados em cada `Process`.

`turnaround_time` e calculado assim:

```text
finish_time - creation_time
```

Esse valor mostra quanto tempo o processo demorou no sistema desde sua chegada
ate terminar.

`ready_time` e incrementado pela simulacao sempre que o processo esta pronto,
mas nao esta executando.
