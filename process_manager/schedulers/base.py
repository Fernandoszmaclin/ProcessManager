from abc import ABC, abstractmethod

from process_manager.models import Process


class Scheduler(ABC):
    def __init__(self, cpu_fraction: int) -> None:
        self.cpu_fraction = cpu_fraction

    @abstractmethod
    def add_process(self, process: Process) -> None:
        raise NotImplementedError

    @abstractmethod
    def pick_next(self) -> Process:
        raise NotImplementedError

    @abstractmethod
    def on_process_preempted(self, process: Process) -> None:
        raise NotImplementedError

    @abstractmethod
    def has_ready_process(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def ready_processes(self) -> list[Process]:
        raise NotImplementedError