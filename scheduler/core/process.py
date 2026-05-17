from dataclasses import dataclass
from enum import Enum, auto


class ProcessState(Enum):
    NEW = auto()
    READY = auto()
    RUNNING = auto()
    FINISHED = auto()


@dataclass
class Process:
    pid: int
    arrival_time: int
    burst_time: int
    priority: int = 0
    weight: int = 1024

    remaining_time: int = 0
    vruntime: float = 0.0
    state: ProcessState = ProcessState.NEW
    start_time: int | None = None
    finish_time: int | None = None

    def __post_init__(self) -> None:
        if self.burst_time <= 0:
            raise ValueError("burst_time must be positive")
        if self.arrival_time < 0:
            raise ValueError("arrival_time cannot be negative")
        if self.weight <= 0:
            raise ValueError("weight must be positive")

        self.remaining_time = self.burst_time

    @property
    def turnaround_time(self) -> int | None:
        if self.finish_time is None:
            return None
        return self.finish_time - self.arrival_time

    @property
    def waiting_time(self) -> int | None:
        turnaround = self.turnaround_time
        if turnaround is None:
            return None
        return turnaround - self.burst_time

    @property
    def response_time(self) -> int | None:
        if self.start_time is None:
            return None
        return self.start_time - self.arrival_time

