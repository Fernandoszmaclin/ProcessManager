from process_manager.models import Process
from process_manager.schedulers.base import Scheduler


class PriorityScheduler(Scheduler):
    def pick_next(self) -> Process:
        # busca o processo prioritario da fila de prontos, desempata por creation_time e pid
        next_process = min(
            self._ready,
            key=lambda process: (
                process.priority_or_tickets,
                process.creation_time,
                process.pid,
            ),
        )
        self._ready.remove(next_process)
        return next_process
