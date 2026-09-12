from .factory import create_page_replacement_algorithm
from .formatter import MemoryResultFormatter
from .memory import Memory
from .models import MemoryFrame, MemorySimulationResult
from .replacement import PageReplacementAlgorithm

__all__ = [
    "Memory",
    "MemoryComparisonRunner",
    "MemoryFrame",
    "MemoryResultFormatter",
    "MemorySimulationResult",
    "PageReplacementAlgorithm",
    "create_page_replacement_algorithm",
]


def __getattr__(name: str):
    # comparison imports Simulation, which itself imports memory.
    if name == "MemoryComparisonRunner":
        from .comparison import MemoryComparisonRunner

        return MemoryComparisonRunner
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
