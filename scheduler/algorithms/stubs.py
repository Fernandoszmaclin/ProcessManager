from scheduler.core.process import Process
from scheduler.core.scheduler import Scheduler


class NotImplementedTeamScheduler(Scheduler):
    """Integration stub for algorithms owned by other team members."""

    def __init__(self, name: str) -> None:
        self.name = name

    def add_process(self, process: Process) -> None:
        raise NotImplementedError(f"{self.name} belongs to another module")

    def pick_next(self) -> Process | None:
        raise NotImplementedError(f"{self.name} belongs to another module")

    def on_tick(self, process: Process) -> None:
        raise NotImplementedError(f"{self.name} belongs to another module")

