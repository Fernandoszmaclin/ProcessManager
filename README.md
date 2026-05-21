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
