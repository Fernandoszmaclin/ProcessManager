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
    if name == "Memory":
        from .memory import Memory

        return Memory
    if name == "MemoryComparisonRunner":
        from .comparison import MemoryComparisonRunner

        return MemoryComparisonRunner
    if name == "MemoryFrame":
        from .models import MemoryFrame

        return MemoryFrame
    if name == "MemoryResultFormatter":
        from .formatter import MemoryResultFormatter

        return MemoryResultFormatter
    if name == "MemorySimulationResult":
        from .models import MemorySimulationResult

        return MemorySimulationResult
    if name == "PageReplacementAlgorithm":
        from .replacement import PageReplacementAlgorithm

        return PageReplacementAlgorithm
    if name == "create_page_replacement_algorithm":
        from .factory import create_page_replacement_algorithm

        return create_page_replacement_algorithm

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
