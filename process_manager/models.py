from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from math import ceil


class ProcessState(Enum):
    NEW = "new"
    READY = "ready"
    RUNNING = "running"
    BLOCKED = "blocked"
    FINISHED = "finished"


@dataclass(frozen=True)
class SimulationConfig:
    algorithm: str
    cpu_fraction: int
    memory_policy: str | None = None
    main_memory_size: int | None = None
    page_frame_size: int | None = None
    allocation_percentage: int | None = None
    total_frames: int | None = None
    io_devices: tuple = ()

    @classmethod
    def create(
        cls,
        algorithm: str,
        cpu_fraction: int,
        memory_policy: str | None = None,
        main_memory_size: int | None = None,
        page_frame_size: int | None = None,
        allocation_percentage: int | None = None,
        io_devices: tuple = (),
    ) -> "SimulationConfig":
        total_frames = None
        if main_memory_size is not None and page_frame_size is not None:
            total_frames = main_memory_size // page_frame_size

        return cls(
            algorithm=algorithm,
            cpu_fraction=cpu_fraction,
            memory_policy=memory_policy,
            main_memory_size=main_memory_size,
            page_frame_size=page_frame_size,
            allocation_percentage=allocation_percentage,
            total_frames=total_frames,
            io_devices=io_devices,
        )

    @property
    def has_memory_config(self) -> bool:
        return (
            self.memory_policy is not None
            and self.main_memory_size is not None
            and self.page_frame_size is not None
            and self.allocation_percentage is not None
            and self.total_frames is not None
        )

    @property
    def has_io_config(self) -> bool:
        return bool(self.io_devices)


@dataclass
class Process:
    creation_time: int
    pid: str
    total_time: int
    priority_or_tickets: int
    remaining_time: int
    memory_amount: int | None = None
    page_access_sequence: list[int] = field(default_factory=list)
    virtual_pages: int | None = None
    state: ProcessState = ProcessState.NEW
    current_page_access_index: int = 0
    finish_time: int | None = None
    ready_time: int = 0
    blocked_time: int = 0
    io_request_chance: int = 0
    blocked_device: str | None = None
    io_status: str | None = None

    @classmethod
    def create(
        cls,
        creation_time: int,
        pid: str,
        total_time: int,
        priority_or_tickets: int,
        memory_amount: int | None = None,
        page_access_sequence: list[int] | None = None,
        page_frame_size: int | None = None,
        io_request_chance: int = 0,
    ) -> "Process":
        virtual_pages = None
        if memory_amount is not None and page_frame_size is not None:
            virtual_pages = ceil(memory_amount / page_frame_size)

        return cls(
            creation_time=creation_time,
            pid=pid,
            total_time=total_time,
            priority_or_tickets=priority_or_tickets,
            memory_amount=memory_amount,
            page_access_sequence=page_access_sequence or [],
            virtual_pages=virtual_pages,
            remaining_time=total_time,
            io_request_chance=io_request_chance,
        )

    @property
    def turnaround_time(self) -> int | None:
        if self.finish_time is None:
            return None
        return self.finish_time - self.creation_time

    def next_page_access(self) -> int | None:
        if self.current_page_access_index >= len(self.page_access_sequence):
            return None
        page_id = self.page_access_sequence[self.current_page_access_index]
        self.current_page_access_index += 1
        return page_id
