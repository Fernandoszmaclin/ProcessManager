from process_manager.models import Process
from process_manager.schedulers.base import Scheduler


class CFSScheduler(Scheduler):
    def __init__(self, cpu_fraction: int) -> None:
        super().__init__(cpu_fraction)
        self._ready: list[Process] = []
        self._vruntime_by_pid: dict[str, int] = {}                                  # guarda o tempo virtual que o processo ja executou
        self._executed_by_pid: dict[str, int] = {}                                  # guarda o tempo real total que o processo ja executou

    def add_process(self, process: Process) -> None:
        # ganha como valor inicial o menor vruntime da fila
        self._vruntime_by_pid.setdefault(process.pid, self._minimum_vruntime())
        self._executed_by_pid.setdefault(process.pid, 0)
        self._ready.append(process)

    def pick_next(self) -> Process:
        # escolhe processo com menor vruntime, desempata por creation_time e pid
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

        # quanto menor a prioridade, mais devagar vruntime cresce
        weighted_time = executed_in_last_slice * process.priority_or_tickets
        self._vruntime_by_pid[process.pid] += weighted_time

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
