from abc import ABC, abstractmethod

from process_manager.models import Process, SimulationConfig
from process_manager.memory.models import MemoryFrame


class PageReplacementAlgorithm(ABC):
    needs_candidate_frames = True

    def prepare(self, processes: list[Process]) -> None:
        pass

    def before_page_access(
        self,
        process: Process,
        page_id: int,
        current_time: int,
    ) -> None:
        pass

    def on_page_loaded(self, frame: MemoryFrame) -> None:
        pass

    def on_page_accessed(self, frame: MemoryFrame) -> None:
        pass

    def on_page_removed(self, frame: MemoryFrame) -> None:
        pass

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
