from pathlib import Path

from .models import Process, SimulationConfig


def parse_input_file(file_path: str) -> tuple[SimulationConfig, list[Process]]:
    # utf-8-sig para ignorar o BOM que o windows add em arquivos .txt
    lines = [
        line
        for line in Path(file_path).read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]

    config = _parse_config(lines[0])

    processes = []
    for line in lines[1:]:
        processes.append(_parse_process(line, config))

    # ordena processos por creation_time --> ordem cronologica
    return config, sorted(processes, key=lambda process: process.creation_time)


def _parse_config(line: str) -> SimulationConfig:
    fields = [field.strip() for field in line.split("|")]

    if len(fields) == 2:
        algorithm, cpu_fraction = fields
        return SimulationConfig.create(
            algorithm=algorithm,
            cpu_fraction=int(cpu_fraction),
        )

    if len(fields) == 6:
        (
            algorithm,
            cpu_fraction,
            memory_policy,
            main_memory_size,
            page_frame_size,
            allocation_percentage,
        ) = fields
        return SimulationConfig.create(
            algorithm=algorithm,
            cpu_fraction=int(cpu_fraction),
            memory_policy=memory_policy,
            main_memory_size=int(main_memory_size),
            page_frame_size=int(page_frame_size),
            allocation_percentage=int(allocation_percentage),
        )

    raise ValueError("Linha de configuracao deve ter 2 ou 6 campos.")


def _parse_process(line: str, config: SimulationConfig) -> Process:
    fields = [field.strip() for field in line.split("|")]

    if len(fields) == 4:
        creation_time, pid, total_time, priority_or_tickets = fields
        return Process.create(
            creation_time=int(creation_time),
            pid=pid,
            total_time=int(total_time),
            priority_or_tickets=int(priority_or_tickets),
        )

    if len(fields) == 6:
        (
            creation_time,
            pid,
            total_time,
            priority_or_tickets,
            memory_amount,
            page_access_sequence,
        ) = fields
        return Process.create(
            creation_time=int(creation_time),
            pid=pid,
            total_time=int(total_time),
            priority_or_tickets=int(priority_or_tickets),
            memory_amount=int(memory_amount),
            page_access_sequence=[
                int(page_id) for page_id in page_access_sequence.split()
            ],
            page_frame_size=config.page_frame_size,
        )

    raise ValueError("Linha de processo deve ter 4 ou 6 campos.")
