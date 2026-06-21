from copy import deepcopy

from process_manager.models import Process, SimulationConfig
from process_manager.memory.factory import create_page_replacement_algorithm
from process_manager.memory.memory import Memory
from process_manager.memory.models import MemorySimulationResult
from process_manager.src.scheduler_factory import create_scheduler
from process_manager.src.simulation import Simulation


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
        memory = Memory(
            self.config,
            create_page_replacement_algorithm(algorithm_name),
        )

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
