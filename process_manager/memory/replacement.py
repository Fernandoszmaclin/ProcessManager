from abc import ABC, abstractmethod

from process_manager.models import Process, SimulationConfig
from process_manager.memory.models import MemoryFrame


class PageReplacementAlgorithm(ABC):
    @abstractmethod
    def select_victim(
        self,
        frames: list[MemoryFrame],
        process: Process,
        page_id: int,
        current_time: int,
        config: SimulationConfig,
    ) -> MemoryFrame:
        raise NotImplementedError
