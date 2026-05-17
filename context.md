Implementar um escalonador preemptivo que selecione processos utilizando os seguintes algoritmos: alternância circular, por prioridade, loteria e CFS (Completely Fair Scheduler). 

O seu programa receberá como entrada um arquivo no seguinte formato:

algoritmoDeEscalonamento|fraçãoDeCPU
momentoDeCriação|PID|tempoDeExecução|prioridade (ou bilhetes)

onde:

    - algoritmoDeEscalonamento é o algoritmo que será utilizado para escalonar os processos
    - fraçãoDeCPU representa o período que um processo pode ficar na CPU por vez
    - momentoDeCriação contém o tempo no qual o processo deve ser criado
    - PID é o identificador único do processo
    - tempoDeExecução informa a quantidade de tempo que um processo necessita para executar
    - prioridade (ou bilhetes) contém a prioridade do processo (ou número de bilhetes para o algoritmo da loteria)

*o arquivo contém informações sobre múltiplos processos, um em cada linha

O seu programa deverá mostrar qual processo está na CPU naquele momento e quanto tempo falta para ele terminar. Nesta etapa do trabalho, um processo somente sairá da CPU quando terminar a sua fatia de tempo. No futuro, os processos poderão sair da CPU devido a alguma operação de E/S solicitada por eles.

Ao final da execução, o seu algoritmo deverá mostrar, de forma clara e organizada, quanto tempo um processo demorou para ser executado, isto é, desde o momento em que foi criado até o momento em que foi concluído, e também o tempo em que ele esteve em estado "pronto". Após executar os algoritmos, compare os resultados para entender as diferenças entre eles.