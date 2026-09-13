from pathlib import Path
from process_manager.io import IODeviceConfig
from process_manager.models import Process, SimulationConfig

def parse_input_file(file_path: str) -> tuple[SimulationConfig, list[Process]]:
    lines = [
        line
        for line in Path(file_path).read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]

    config, device_lines = _parse_config(lines[0], lines[1:])
    process_start = 1 + len(device_lines)
    processes = [_parse_process(line, config) for line in lines[process_start:]]
    return config, sorted(processes, key=lambda process: process.creation_time)

def _parse_config(
    line: str, remaining_lines: list[str]
) -> tuple[SimulationConfig, list[str]]:
    fields = [field.strip() for field in line.split("|")]

    if len(fields) == 2:
        return SimulationConfig.create(fields[0], int(fields[1])), []

    if len(fields) == 6:
        (algorithm,cpu_fraction,memory_policy,main_memory_size,page_frame_size,allocation_percentage) = fields
        return SimulationConfig.create(algorithm=algorithm,cpu_fraction=int(cpu_fraction),memory_policy=memory_policy,main_memory_size=int(main_memory_size),page_frame_size=int(page_frame_size),allocation_percentage=int(allocation_percentage)), []

    if len(fields) == 7:
        (algorithm,cpu_fraction,memory_policy,main_memory_size,page_frame_size,allocation_percentage,device_count,) = fields
        count = int(device_count)
        device_lines = remaining_lines[:count]
        devices = tuple(_parse_device(device_line) for device_line in device_lines)
        return SimulationConfig.create(algorithm=algorithm,cpu_fraction=int(cpu_fraction),memory_policy=memory_policy,main_memory_size=int(main_memory_size),page_frame_size=int(page_frame_size),allocation_percentage=int(allocation_percentage),io_devices=devices,
        ), device_lines

def _parse_device(line) :
    fields = [field.strip() for field in line.split("|")]
    device_id, simultaneous_uses, operation_time = fields
    simultaneous_uses = int(simultaneous_uses)
    operation_time = int(operation_time)
    return IODeviceConfig(device_id, simultaneous_uses, operation_time)

def _parse_process(line: str, config: SimulationConfig) -> Process:
    fields = [field.strip() for field in line.split("|")]

    if len(fields) == 4:
        creation_time, pid, total_time, priority_or_tickets = fields
        return Process.create(int(creation_time), pid, int(total_time), int(priority_or_tickets))

    if len(fields) in (6, 7):
        (creation_time,pid,total_time,priority_or_tickets,memory_amount,page_access_sequence,*io_fields,
        ) = fields
        return Process.create(creation_time=int(creation_time),pid=pid,total_time=int(total_time),priority_or_tickets=int(priority_or_tickets),memory_amount=int(memory_amount),page_access_sequence=[int(page_id) for page_id in page_access_sequence.split()],page_frame_size=config.page_frame_size,io_request_chance=_parse_chance(io_fields[0]) if io_fields else 0,)

def _parse_chance(value):
    chance = int(value)
    return chance
