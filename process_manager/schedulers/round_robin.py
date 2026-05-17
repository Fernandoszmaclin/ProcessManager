from collections import deque

from process_manager.models import Process
from process_manager.schedulers.base import Scheduler


class RoundRobinScheduler(Scheduler):
    """Alternancia circular.

    Este arquivo e a parte que vamos implementar em seguida.
    """

    def __init__(self, cpu_fraction: int) -> None:
        super().__init__(cpu_fraction)
        self._queue: deque[Process] = deque()

    def add_process(self, process: Process) -> None:
        raise NotImplementedError("Round Robin ainda sera implementado.")

    def pick_next(self) -> Process:
        raise NotImplementedError("Round Robin ainda sera implementado.")

    def on_process_preempted(self, process: Process) -> None:
        raise NotImplementedError("Round Robin ainda sera implementado.")

    def has_ready_process(self) -> bool:
        return bool(self._queue)

    def ready_processes(self) -> list[Process]:
        return list(self._queue)
