from process_manager.memory.models import MemorySimulationResult


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
