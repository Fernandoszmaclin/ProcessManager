from copy import deepcopy
from dataclasses import dataclass

from process_manager.models import Process, SimulationConfig
from process_manager.src.scheduler_factory import create_scheduler
from process_manager.src.simulation import Simulation
from process_manager.memory import create_page_replacement_algorithm, Memory

@dataclass(frozen=True)
class MemorySimulationResult:
    fifo_exchanges: int | None = None
    lru_exchanges: int | None = None
    nuf_exchanges: int | None = None
    optimal_exchanges: int | None = None
    best_algorithm: str | None = None

class MemoryComparisonRunner:
    def __init__(
        self,
        config: SimulationConfig,
        processes: list[Process],
    ) -> None:
        self.config = config
        self.processes = processes
        self.algorithm_names = ("fifo", "lru", "nuf", "otimo")

    def run(self) -> MemorySimulationResult:
        exchange_counts = {
            name: self._run_algorithm(name) for name in self.algorithm_names
        }

        return MemorySimulationResult(
            fifo_exchanges=exchange_counts["fifo"],
            lru_exchanges=exchange_counts["lru"],
            nuf_exchanges=exchange_counts["nuf"],
            optimal_exchanges=exchange_counts["otimo"],
            best_algorithm=self._find_best_algorithm(exchange_counts),
        )

    def _run_algorithm(self, algorithm_name: str) -> int:
        processes = deepcopy(self.processes)
        scheduler = create_scheduler(self.config.algorithm, self.config.cpu_fraction)
        algorithm = create_page_replacement_algorithm(algorithm_name)
        algorithm.prepare(processes)
        memory = Memory(self.config, algorithm)

        Simulation(self.config, processes, scheduler, memory).run()
        return memory.exchange_count

    def _find_best_algorithm(self, exchange_counts: dict[str, int]) -> str:
        optimal_exchanges = exchange_counts["otimo"]
        distances = {
            name: abs(exchanges - optimal_exchanges)
            for name, exchanges in exchange_counts.items()
            if name != "otimo"
        }
        best_distance = min(distances.values())
        best_algorithms = [
            name for name, distance in distances.items() if distance == best_distance
        ]

        if len(best_algorithms) > 1:
            return "empate"

        return best_algorithms[0]

class MemoryResultFormatter:
    def format(self, result: MemorySimulationResult) -> str:
        return (
            f"{self._format_value(result.fifo_exchanges)}|"
            f"{self._format_value(result.lru_exchanges)}|"
            f"{self._format_value(result.nuf_exchanges)}|"
            f"{self._format_value(result.optimal_exchanges)}|"
            f"{self._format_value(result.best_algorithm)}"
        )

    def _format_value(self, value: int | str | None) -> str:
        if value is None:
            return ""
        return str(value)
