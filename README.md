## Formato de entrada

As entradas sao geradas por `examples/geradorEntrada.py`, entao o parser assume o
formato abaixo sem validar casos especiais. O formato original do escalonador
continua aceito:

```text
algoritmoDeEscalonamento|fracaoDeCPU
momentoDeCriacao|PID|tempoDeExecucao|prioridadeOuBilhetes
```

Tambem existe a estrutura inicial para o modulo de memoria, que aceita o novo
formato de entrada:

```text
algoritmoDeEscalonamento|fracaoDeCPU|politicaMemoria|tamanhoMemoria|tamanhoPaginasMolduras|percentualAlocacao
momentoDeCriacao|PID|tempoDeExecucao|prioridadeOuBilhetes|qtdeMemoria|sequenciaAcessoPaginasProcesso
```

As politicas de substituicao FIFO, LRU, NUF e Otimo ainda estao apenas como
pontos de extensao para implementacao futura.

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
