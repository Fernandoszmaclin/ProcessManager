import random
from process_manager.models import Process
from process_manager.schedulers.base import Scheduler

class LotteryScheduler(Scheduler):
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
                
        return self._ready.pop()
