from process_manager.models import Process
from process_manager.schedulers.base import Scheduler


class PriorityScheduler(Scheduler):
    def __init__(self, cpu_fraction: int) -> None:
        super().__init__(cpu_fraction)
        self._ready: list[Process] = []

    def add_process(self, process: Process) -> None:
        self._ready.append(process)

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

    def on_process_preempted(self, process: Process) -> None:
        self._ready.append(process)

    def has_ready_process(self) -> bool:
        return bool(self._ready)

    def ready_processes(self) -> list[Process]:
        return list(self._ready)
