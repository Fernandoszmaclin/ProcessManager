from collections import deque
import random

from process_manager.memory import Memory
from process_manager.io import IOManager
from process_manager.models import Process, ProcessState, SimulationConfig
from process_manager.schedulers.base import Scheduler

from .report import SimulationReport, TimelineEntry


class Simulation:
    def __init__(self,config: SimulationConfig,processes: list[Process],scheduler: Scheduler,memory: Memory | None = None) -> None:
        self.config = config
        self.processes = processes
        self.scheduler = scheduler
        self.memory = memory
        self.io = IOManager(config.io_devices)
        self.timeline: list[TimelineEntry] = []
        self.state_log: list[str] = []
        self.current_time = 0

    def run(self) -> SimulationReport:
        pending = deque(self.processes)
        finished_count = 0

        while finished_count < len(self.processes):
            self._admit_new_processes(pending)

            if not self.scheduler.has_ready_process():
                self._jump_to_next_event(pending)
                continue

            process = self.scheduler.pick_next()
            process.state = ProcessState.RUNNING
            slice_start = self.current_time
            time_to_run = min(self.config.cpu_fraction, process.remaining_time)
            io_request = self._plan_io(process, time_to_run)
            if self.config.has_io_config:
                self.state_log.append(self._describe_state(process))

            blocked = False
            for cycle in range(1, time_to_run + 1):
                for ready_process in self.scheduler.ready_processes():
                    ready_process.ready_time += 1
                for blocked_process in self.io.blocked_processes():
                    blocked_process.blocked_time += 1

                self.current_time += 1
                for released in self.io.advance(self.current_time):
                    self.scheduler.add_process(released)
                process.remaining_time -= 1
                self._access_memory(process)
                self._admit_new_processes(pending)

                if (
                    io_request is not None
                    and cycle == io_request[0]
                    and process.remaining_time > 0
                ):
                    self.io.request(process, io_request[1], self.current_time)
                    blocked = True
                    break

            self.timeline.append(
                TimelineEntry(
                    start_time=slice_start,
                    end_time=self.current_time,
                    pid=process.pid,
                    remaining_time=process.remaining_time,
                )
            )

            if process.remaining_time == 0:
                process.state = ProcessState.FINISHED
                process.finish_time = self.current_time
                finished_count += 1
            elif not blocked:
                process.state = ProcessState.READY
                self.scheduler.on_process_preempted(process)

        return SimulationReport(self.timeline, self.processes, self.state_log)

    def _jump_to_next_event(self, pending: deque[Process]) -> None:
        candidates = []
        if pending:
            candidates.append(pending[0].creation_time)
        if self.io.next_completion() is not None:
            candidates.append(self.io.next_completion())
        if not candidates:
            raise RuntimeError("A simulacao ficou sem processos executaveis.")

        next_time = min(candidates)
        elapsed = next_time - self.current_time
        for process in self.io.blocked_processes():
            process.blocked_time += elapsed
        self.current_time = next_time
        for released in self.io.advance(self.current_time):
            self.scheduler.add_process(released)

    def _plan_io(self, process, time_to_run):
        if not self.io.devices or process.io_request_chance <= 0 or time_to_run <= 0:
            return None
        if random.randrange(100) >= process.io_request_chance:
            return None
        return random.randint(1, time_to_run), random.choice(tuple(self.io.devices))

    def _describe_state(self, running: Process) -> str:
        ready = [f"{p.pid}({p.remaining_time})" for p in self.scheduler.ready_processes()]
        blocked = [
            f"{p.pid}({p.remaining_time}, {p.blocked_device}/{p.io_status})"
            for p in self.io.blocked_processes()
        ]
        devices = "\n".join(f"  {line}" for line in self.io.describe())
        return (
            f"Estado t={self.current_time}: CPU {running.pid}({running.remaining_time})\n"
            f"Prontos: {', '.join(ready) or '-'}\n"
            f"Bloqueados: {', '.join(blocked) or '-'}\n"
            f"Dispositivos:\n{devices or '  -'}"
        )

    def _admit_new_processes(self, pending: deque[Process]) -> None:
        while pending and pending[0].creation_time <= self.current_time:
            process = pending.popleft()
            process.state = ProcessState.READY
            self.scheduler.add_process(process)

    def _access_memory(self, process: Process) -> None:
        if self.memory is None:
            return
        page_id = process.next_page_access()
        if page_id is not None:
            self.memory.access_page(process, page_id, self.current_time)
