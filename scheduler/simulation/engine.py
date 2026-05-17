from dataclasses import dataclass, field

from scheduler.core.process import Process, ProcessState
from scheduler.core.scheduler import Scheduler


@dataclass
class SimulationEvent:
    time: int
    message: str


@dataclass
class Simulation:
    processes: list[Process]
    scheduler: Scheduler
    clock: int = 0
    events: list[SimulationEvent] = field(default_factory=list)

    def run(self) -> None:
        while not self._all_finished():
            self._admit_arrived_processes()

            current = self.scheduler.pick_next()
            if current is None:
                self._log("CPU idle")
                self.clock += 1
                continue

            self._run_one_tick(current)

            if current.remaining_time == 0:
                current.state = ProcessState.FINISHED
                current.finish_time = self.clock
                self._log(f"P{current.pid} finished")
            else:
                current.state = ProcessState.READY
                self.scheduler.add_process(current)

    def metrics(self) -> dict[str, float]:
        finished = [p for p in self.processes if p.finish_time is not None]
        if not finished:
            return {
                "average_turnaround_time": 0.0,
                "average_waiting_time": 0.0,
                "average_response_time": 0.0,
            }

        return {
            "average_turnaround_time": self._average(
                p.turnaround_time for p in finished
            ),
            "average_waiting_time": self._average(p.waiting_time for p in finished),
            "average_response_time": self._average(p.response_time for p in finished),
        }

    def _run_one_tick(self, process: Process) -> None:
        if process.start_time is None:
            process.start_time = self.clock

        process.state = ProcessState.RUNNING
        process.remaining_time -= 1
        self._log(f"P{process.pid} running")

        self.scheduler.on_tick(process)
        self.clock += 1

    def _admit_arrived_processes(self) -> None:
        for process in self.processes:
            if (
                process.state == ProcessState.NEW
                and process.arrival_time <= self.clock
            ):
                process.state = ProcessState.READY
                self.scheduler.add_process(process)
                self._log(f"P{process.pid} admitted")

    def _all_finished(self) -> bool:
        return all(process.state == ProcessState.FINISHED for process in self.processes)

    def _log(self, message: str) -> None:
        self.events.append(SimulationEvent(self.clock, message))

    @staticmethod
    def _average(values: object) -> float:
        numbers = [value for value in values if value is not None]
        return sum(numbers) / len(numbers)

