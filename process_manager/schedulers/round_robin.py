from collections import deque

from process_manager.models import Process
from process_manager.schedulers.base import Scheduler


class RoundRobinScheduler(Scheduler):
    def __init__(self, cpu_fraction: int) -> None:
        super().__init__(cpu_fraction)
        self._ready: deque[Process] = deque()

    def pick_next(self) -> Process:
        return self._ready.popleft()
