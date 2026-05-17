from process_manager.models import Process
from process_manager.schedulers.base import Scheduler


class LotteryScheduler(Scheduler):
    def __init__(self, cpu_fraction: int) -> None:
        super().__init__(cpu_fraction)
        self._ready: list[Process] = []

    def add_process(self, process: Process) -> None:
        raise NotImplementedError("Escalonador por loteria ainda nao implementado.")

    def pick_next(self) -> Process:
        raise NotImplementedError("Escalonador por loteria ainda nao implementado.")

    def on_process_preempted(self, process: Process) -> None:
        raise NotImplementedError("Escalonador por loteria ainda nao implementado.")

    def has_ready_process(self) -> bool:
        return bool(self._ready)

    def ready_processes(self) -> list[Process]:
        return list(self._ready)
