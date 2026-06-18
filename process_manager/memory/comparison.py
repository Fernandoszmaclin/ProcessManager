from process_manager.models import Process, SimulationConfig
from process_manager.memory.algorithms import (
    FIFOPageReplacement,
    LRUPageReplacement,
    NUFPageReplacement,
    OptimalPageReplacement,
)
from process_manager.memory.models import MemorySimulationResult


class MemoryComparisonRunner:
    def __init__(
        self,
        config: SimulationConfig,
        processes: list[Process],
    ) -> None:
        self.config = config
        self.processes = processes
        self.algorithms = {
            "fifo": FIFOPageReplacement(),
            "lru": LRUPageReplacement(),
            "nuf": NUFPageReplacement(),
            "otimo": OptimalPageReplacement(),
        }

    def run(self) -> MemorySimulationResult:
        raise NotImplementedError(
            "Comparacao de algoritmos de memoria sera implementada em etapa futura."
        )
