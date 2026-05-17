from dataclasses import dataclass
from enum import Enum


class ProcessState(Enum):
    NEW = "new"
    READY = "ready"
    RUNNING = "running"
    FINISHED = "finished"


@dataclass(frozen=True)
class SimulationConfig:
    algorithm: str
    cpu_fraction: int


@dataclass
class Process:
    creation_time: int
    pid: str
    total_time: int
    priority_or_tickets: int
    remaining_time: int
    state: ProcessState = ProcessState.NEW
    finish_time: int | None = None
    ready_time: int = 0

    @classmethod
    def create(
        cls,
        creation_time: int,
        pid: str,
        total_time: int,
        priority_or_tickets: int,
    ) -> "Process":
        return cls(
            creation_time=creation_time,
            pid=pid,
            total_time=total_time,
            priority_or_tickets=priority_or_tickets,
            remaining_time=total_time,
        )

    @property
    def turnaround_time(self) -> int | None:
        if self.finish_time is None:
            return None
        return self.finish_time - self.creation_time
