## Formato de entrada

O formato original do escalonador continua aceito:

```text
algoritmoDeEscalonamento|fracaoDeCPU
momentoDeCriacao|PID|tempoDeExecucao|prioridadeOuBilhetes
```

Para ativar a simulacao de memoria paginada, use configuracao de memoria na
primeira linha e dados de memoria em cada processo:

```text
algoritmoDeEscalonamento|fracaoDeCPU|politicaMemoria|tamanhoMemoria|tamanhoPaginasMolduras|percentualAlocacao
momentoDeCriacao|PID|tempoDeExecucao|prioridadeOuBilhetes|qtdeMemoria|sequenciaAcessoPaginasProcesso
```

Campos de memoria:

- `politicaMemoria`: `global` ou `local`.
- `tamanhoMemoria`: tamanho da memoria principal.
- `tamanhoPaginasMolduras`: tamanho usado para calcular a quantidade de molduras.
- `percentualAlocacao`: percentual da memoria virtual permitido na politica local.
- `qtdeMemoria`: memoria virtual do processo.
- `sequenciaAcessoPaginasProcesso`: paginas acessadas, separadas por espaco.

Exemplo:

```text
alternanciaCircular|1|global|2|1|100
0|p1|4|1|3|1 2 1 3
```

## Memoria

A cada ciclo de CPU, o processo executando consome o proximo acesso de memoria.
Se a pagina ja estiver carregada, ocorre hit. Se nao estiver, ocorre page miss.
Adicionar pagina em moldura livre nao conta como troca; troca e apenas substituir
uma pagina ja carregada por outra.

Algoritmos comparados:

- `fifo`: remove a pagina carregada ha mais tempo.
- `lru`: remove a pagina menos recentemente usada.
- `nuf`: NFU com aging; a cada ciclo os contadores fazem shift para a direita
  (`/2`) e a pagina acessada recebe `+128`.
- `otimo`: remove a pagina cujo proximo uso esta mais distante no futuro.

Desempates:

- No `nuf`, paginas igualmente indicadas sao desempatadas pelo menor ID.
- Se dois ou mais algoritmos forem igualmente melhores, o resultado imprime
  `empate`.

Com memoria configurada, a saida adicional tem o formato:

```text
FIFO|LRU|NUF|Otimo|Melhor
```

Exemplo:

```text
7|5|5|5|empate
```

