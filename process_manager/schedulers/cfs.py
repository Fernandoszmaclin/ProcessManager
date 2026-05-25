from process_manager.models import Process
from process_manager.schedulers.base import Scheduler


class CFSScheduler(Scheduler):
    def __init__(self, cpu_fraction: int) -> None:
        super().__init__(cpu_fraction)
        self._ready: list[Process] = []
        self._vruntime_by_pid: dict[str, int] = {}
        self._executed_by_pid: dict[str, int] = {}

    def add_process(self, process: Process) -> None:
        self._vruntime_by_pid.setdefault(process.pid, self._minimum_vruntime())
        self._executed_by_pid.setdefault(process.pid, 0)
        self._ready.append(process)

    def pick_next(self) -> Process:
        next_process = min(
            self._ready,
            key=lambda process: (
                self._vruntime_by_pid[process.pid],
                process.creation_time,
                process.pid,
            ),
        )
        self._ready.remove(next_process)
        return next_process

    def on_process_preempted(self, process: Process) -> None:
        executed = process.total_time - process.remaining_time
        executed_in_last_slice = executed - self._executed_by_pid[process.pid]

        self._vruntime_by_pid[process.pid] += executed_in_last_slice
        self._executed_by_pid[process.pid] = executed
        self._ready.append(process)

    def has_ready_process(self) -> bool:
        return bool(self._ready)

    def ready_processes(self) -> list[Process]:
        return list(self._ready)

    def _minimum_vruntime(self) -> int:
        if not self._ready:
            return 0
        return min(self._vruntime_by_pid[process.pid] for process in self._ready)
