from collections import deque

from process_manager.models import Process
from process_manager.schedulers.base import Scheduler


class RoundRobinScheduler(Scheduler):

    def __init__(self, cpu_fraction: int) -> None:
        super().__init__(cpu_fraction)
        self._queue: deque[Process] = deque()

    def add_process(self, process: Process) -> None:
        self._queue.append(process)

    def pick_next(self) -> Process:
        return self._queue.popleft()

    def on_process_preempted(self, process: Process) -> None:
        self._queue.append(process)

    def has_ready_process(self) -> bool:
        return bool(self._queue)

    def ready_processes(self) -> list[Process]:
        return list(self._queue)
