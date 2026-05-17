import heapq
from dataclasses import dataclass, field

from scheduler.core.process import Process
from scheduler.core.scheduler import Scheduler


NICE_0_LOAD = 1024


@dataclass(order=True)
class _CfsEntry:
    vruntime: float
    sequence: int
    process: Process = field(compare=False)


class CfsScheduler(Scheduler):
    """
    Simplified Completely Fair Scheduler.

    The ready queue is a min-heap ordered by vruntime. The process that has
    received proportionally less CPU time is selected first.
    """

    def __init__(self) -> None:
        self._ready_heap: list[_CfsEntry] = []
        self._sequence = 0

    def add_process(self, process: Process) -> None:
        heapq.heappush(
            self._ready_heap,
            _CfsEntry(process.vruntime, self._sequence, process),
        )
        self._sequence += 1

    def pick_next(self) -> Process | None:
        if not self._ready_heap:
            return None
        return heapq.heappop(self._ready_heap).process

    def on_tick(self, process: Process) -> None:
        process.vruntime += NICE_0_LOAD / process.weight

    def should_preempt(self, current: Process | None) -> bool:
        if current is None or not self._ready_heap:
            return False
        return self._ready_heap[0].vruntime < current.vruntime

