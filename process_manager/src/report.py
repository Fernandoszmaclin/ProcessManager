from dataclasses import dataclass

from process_manager.models import Process


@dataclass(frozen=True)
class TimelineEntry:
    start_time: int
    end_time: int
    pid: str
    remaining_time: int


class SimulationReport:
    def __init__(
        self,
        timeline: list[TimelineEntry],
        processes: list[Process],
        state_log: list[str] | None = None,
    ) -> None:
        self.timeline = timeline
        self.processes = sorted(processes, key=lambda process: process.pid)
        self.state_log = state_log or []

    def print_timeline(self) -> None:
        print("Linha do tempo:")
        for index, entry in enumerate(self.timeline):
            if index < len(self.state_log):
                print()
                print(f"[t={entry.start_time}] Estado antes da fatia:")
                print(self.state_log[index])
                print(
                    f"Execução: PID {entry.pid} de t={entry.start_time} "
                    f"até t={entry.end_time}; restante {entry.remaining_time}"
                )
                continue
            print(
                f"t={entry.start_time}..{entry.end_time}: "
                f"PID {entry.pid} na CPU, faltam {entry.remaining_time}"
            )

    def print_summary(self) -> None:
        print()
        print("Resumo:")
        header = "PID | criado | terminou | execucao total | tempo pronto"
        if any(process.io_request_chance for process in self.processes):
            header += " | tempo bloqueado"
        print(header)
        for process in self.processes:
            values = [
                process.pid,
                process.creation_time,
                process.finish_time,
                process.turnaround_time,
                process.ready_time,
            ]
            if any(item.io_request_chance for item in self.processes):
                values.append(process.blocked_time)
            print(" | ".join(str(value) for value in values))
