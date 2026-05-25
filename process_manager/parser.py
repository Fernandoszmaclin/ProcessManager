from pathlib import Path

from .models import Process, SimulationConfig


def parse_input_file(file_path: str) -> tuple[SimulationConfig, list[Process]]:
    lines = Path(file_path).read_text(encoding="utf-8-sig").splitlines()

    algorithm, cpu_fraction = lines[0].split("|")
    config = SimulationConfig(
        algorithm=algorithm.strip(),
        cpu_fraction=int(cpu_fraction),
    )

    processes = []
    for line in lines[1:]:
        creation_time, pid, total_time, priority_or_tickets = line.split("|")
        processes.append(
            Process.create(
                creation_time=int(creation_time),
                pid=pid,
                total_time=int(total_time),
                priority_or_tickets=int(priority_or_tickets),
            )
        )

    return config, sorted(processes, key=lambda process: process.creation_time)
