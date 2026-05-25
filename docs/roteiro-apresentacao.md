# Roteiro para apresentacao

## 1. Problema

O projeto representa uma parte de um sistema operacional: o gerenciamento de
processos. A ideia e simular como processos entram no sistema, ficam prontos,
usam a CPU por fatias de tempo e terminam.

O foco principal da entrega foi implementar o escalonador CFS, mantendo a
estrutura ja criada pelo grupo.

## 2. Entrada e configuracao

Explique que o programa recebe um arquivo texto. A primeira linha escolhe o
algoritmo e a fatia de CPU. As linhas seguintes descrevem os processos.

Exemplo:

```text
CFS|2
0|P1|6|0
0|P2|4|0
1|P3|3|0
```

Nesse exemplo:

- algoritmo: `CFS`;
- fatia de CPU: `2`;
- `P1`, `P2` e `P3` entram em momentos diferentes e precisam de tempos
  diferentes de execucao.

## 3. Arquitetura do projeto

Mostre que o codigo foi dividido por responsabilidade:

- `parser.py`: transforma arquivo em objetos;
- `models.py`: define dados do processo e estados;
- `scheduler_factory.py`: escolhe o escalonador;
- `simulation.py`: executa o tempo da simulacao;
- `report.py`: mostra os resultados;
- `schedulers/`: contem os algoritmos.

Essa divisao deixa o simulador independente do algoritmo. Para trocar o
escalonador, basta trocar o valor da primeira linha da entrada.

## 4. Estados do processo

Apresente os quatro estados:

- `NEW`: processo ainda nao chegou;
- `READY`: processo pronto esperando CPU;
- `RUNNING`: processo em execucao;
- `FINISHED`: processo concluido.

Durante a simulacao, o processo normalmente segue:

```text
NEW -> READY -> RUNNING -> READY -> RUNNING -> FINISHED
```

Ele pode voltar para `READY` se sua fatia acabar antes de terminar.

## 5. Preempcao

O simulador e preemptivo porque o processo nao fica na CPU ate terminar
necessariamente. Ele executa no maximo a `fracaoDeCPU`.

Se ainda restar tempo depois da fatia, ele sai da CPU e volta para a fila de
prontos. Depois o escalonador decide quem executa em seguida.

## 6. CFS

O CFS tenta distribuir a CPU de forma justa. A ideia usada no projeto e o
`vruntime`, ou tempo virtual.

Quanto mais um processo executa, maior fica seu `vruntime`. O escalonador sempre
escolhe o processo com menor `vruntime`, ou seja, quem recebeu menos CPU ate
aquele momento.

No projeto:

- processos prontos ficam em uma lista;
- cada PID tem um `vruntime`;
- ao final de uma fatia, o tempo executado e somado ao `vruntime`;
- em empate, o projeto usa tempo de criacao e PID para manter resultado
  deterministico.

## 7. Saida

Mostre a linha do tempo:

```text
t=0..2: PID P1 na CPU, faltam 4
```

Explique que isso mostra o intervalo executado e o tempo restante.

Depois mostre o resumo:

```text
PID | criado | terminou | execucao total | tempo pronto
```

`execucao total` e o tempo desde a criacao ate terminar. `tempo pronto` e quanto
tempo o processo ficou esperando CPU.

## 8. Pontos importantes para falar

- O projeto simula tempo em unidades discretas.
- A cada unidade de tempo, processos prontos acumulam espera.
- O escalonador nao altera o relogio; ele apenas escolhe a ordem.
- A simulacao controla quando processos chegam, executam e terminam.
- O CFS implementado e uma versao didatica baseada em `vruntime`.
- Nenhum outro algoritmo foi implementado nesta etapa.

## 9. Possivel demonstracao

Execute:

```powershell
python -m process_manager entradaEscalonador.txt
```

Durante a demonstracao, destaque:

1. a primeira linha do arquivo define `CFS`;
2. a fatia de CPU limita cada execucao;
3. a linha do tempo mostra alternancia entre processos;
4. o resumo mostra tempo total e tempo pronto.
