from abc import ABC, abstractmethod

from scheduler.core.process import Process


class Scheduler(ABC):
    """Common contract used by the simulation core."""

    @abstractmethod
    def add_process(self, process: Process) -> None:
        """Add a ready process to the scheduler."""

    @abstractmethod
    def pick_next(self) -> Process | None:
        """Return the next process selected to run."""

    @abstractmethod
    def on_tick(self, process: Process) -> None:
        """Update scheduler-specific accounting after one CPU tick."""

    def should_preempt(self, current: Process | None) -> bool:
        """Hook for schedulers that need explicit preemption decisions."""
        return False

