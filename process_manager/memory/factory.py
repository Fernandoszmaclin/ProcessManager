from process_manager.memory.algorithms import (
    FIFOPageReplacement,
    LRUPageReplacement,
    NUFPageReplacement,
    OptimalPageReplacement,
)
from process_manager.memory.replacement import PageReplacementAlgorithm


def create_page_replacement_algorithm(name: str) -> PageReplacementAlgorithm:
    if name == "fifo":
        return FIFOPageReplacement()
    if name == "lru":
        return LRUPageReplacement()
    if name == "nuf":
        return NUFPageReplacement()
    if name == "otimo":
        return OptimalPageReplacement()

    raise ValueError(f"erro na entrada: {name}")
