from dataclasses import dataclass


@dataclass
class MemoryFrame:
    owner_pid: str
    page_id: int
    load_time: int
    last_used_time: int
    use_count: int = 1

    def matches(self, pid: str, page_id: int) -> bool:
        return self.owner_pid == pid and self.page_id == page_id

    def register_access(self, current_time: int) -> None:
        self.last_used_time = current_time
        self.use_count += 1


@dataclass(frozen=True)
class MemorySimulationResult:
    fifo_exchanges: int | None = None
    lru_exchanges: int | None = None
    nuf_exchanges: int | None = None
    optimal_exchanges: int | None = None
    best_algorithm: str | None = None
