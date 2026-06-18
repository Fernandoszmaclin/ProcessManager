from process_manager.models import Process, SimulationConfig
from process_manager.memory.models import MemoryFrame
from process_manager.memory.replacement import PageReplacementAlgorithm


class FIFOPageReplacement(PageReplacementAlgorithm):
    def select_victim(
        self,
        frames: list[MemoryFrame],
        process: Process,
        page_id: int,
        current_time: int,
        config: SimulationConfig,
    ) -> MemoryFrame:
        raise NotImplementedError("FIFO sera implementado em uma etapa futura.")


class LRUPageReplacement(PageReplacementAlgorithm):
    def select_victim(
        self,
        frames: list[MemoryFrame],
        process: Process,
        page_id: int,
        current_time: int,
        config: SimulationConfig,
    ) -> MemoryFrame:
        raise NotImplementedError("LRU sera implementado em uma etapa futura.")


class NUFPageReplacement(PageReplacementAlgorithm):
    def select_victim(
        self,
        frames: list[MemoryFrame],
        process: Process,
        page_id: int,
        current_time: int,
        config: SimulationConfig,
    ) -> MemoryFrame:
        raise NotImplementedError("NUF sera implementado em uma etapa futura.")


class OptimalPageReplacement(PageReplacementAlgorithm):
    def select_victim(
        self,
        frames: list[MemoryFrame],
        process: Process,
        page_id: int,
        current_time: int,
        config: SimulationConfig,
    ) -> MemoryFrame:
        raise NotImplementedError("Otimo sera implementado em uma etapa futura.")
