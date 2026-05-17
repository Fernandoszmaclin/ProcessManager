from dataclasses import dataclass

from .models import Process


@dataclass(frozen=True)
class TimelineEntry:
    start_time: int
    end_time: int
    pid: str
    remaining_time: int


class SimulationReport:
    def __init__(self, timeline: list[TimelineEntry], processes: list[Process]) -> None:
        self.timeline = timeline
        self.processes = sorted(processes, key=lambda process: process.pid)

    def print_timeline(self) -> None:
        print("Linha do tempo:")
        for entry in self.timeline:
            print(
                f"t={entry.start_time}..{entry.end_time}: "
                f"PID {entry.pid} na CPU, faltam {entry.remaining_time}"
            )

    def print_summary(self) -> None:
        print()
        print("Resumo:")
        print("PID | criado | terminou | execucao total | tempo pronto")
        for process in self.processes:
            turnaround = process.turnaround_time
            print(
                f"{process.pid} | {process.creation_time} | {process.finish_time} | "
                f"{turnaround} | {process.ready_time}"
            )
