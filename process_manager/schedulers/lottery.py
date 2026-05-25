import random
from process_manager.models import Process
from process_manager.schedulers.base import Scheduler

class LotteryScheduler(Scheduler):
    def __init__(self, cpu_fraction: int) -> None:
        super().__init__(cpu_fraction)
        self._ready: list[Process] = []             # fila de processos que estao prontos p/ concorrer ao sorteio

    def add_process(self, process: Process) -> None:
        self._ready.append(process)                 # processo novo é criado, entra na fila de sorteio

    def pick_next(self) -> Process:
        if not self._ready:
            raise ValueError("Nenhum processo está pronto para sorteio.")
        
        # soma os bilhetes de todos os processos na fila de prontos (priority_or_tickets atua como qtd de bilhetes)
        total_tickets = sum(process.priority_or_tickets for process in self._ready)
        
        # sorteia bilhete vencedor 
        winning_ticket = random.randint(1, total_tickets)
        
        # se soma dos bilhetes até o momento alcançar o bilhete vencedor, o processo correspondente eh escolhido para execucao
        current_sum = 0
        for process in self._ready:
            current_sum += process.priority_or_tickets
            if current_sum >= winning_ticket:
                self._ready.remove(process)
                return process
                
        winner = self._ready.pop()
        return winner

    def on_process_preempted(self, process: Process) -> None:
        self._ready.append(process)

    def has_ready_process(self) -> bool:
        return bool(self._ready)

    def ready_processes(self) -> list[Process]:
        return list(self._ready)