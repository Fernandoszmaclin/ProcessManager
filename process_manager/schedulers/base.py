from abc import ABC, abstractmethod
from collections import deque

from process_manager.models import Process


class Scheduler(ABC):
    def __init__(self, cpu_fraction: int) -> None:
        self.cpu_fraction = cpu_fraction
        self._ready: list[Process] | deque[Process] = []

    def add_process(self, process: Process) -> None:
        self._ready.append(process)

    @abstractmethod
    def pick_next(self) -> Process:
        raise NotImplementedError

    def on_process_preempted(self, process: Process) -> None:
        self._ready.append(process)

    def has_ready_process(self) -> bool:
        return bool(self._ready)

    def ready_processes(self) -> list[Process]:
        return list(self._ready)
