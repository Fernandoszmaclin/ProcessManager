from abc import ABC, abstractmethod
from collections import OrderedDict, defaultdict
from dataclasses import dataclass
from operator import attrgetter

from process_manager.models import Process, SimulationConfig

@dataclass
class MemoryFrame:
    owner_pid: str
    page_id: int
    load_time: int
    last_used_time: int
    use_count: int = 1

    def register_access(self, current_time: int) -> None:
        self.last_used_time = current_time
        self.use_count += 1

class PageReplacementAlgorithm(ABC):
    needs_candidate_frames = True

    def prepare(self, processes: list[Process]) -> None:
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

class FIFOPageReplacement(PageReplacementAlgorithm):
    needs_candidate_frames = False

    def __init__(self) -> None:
        self._global_order: OrderedDict[tuple[str, int], MemoryFrame] = OrderedDict()
        self._local_order = defaultdict(OrderedDict)

    def on_page_loaded(self, frame: MemoryFrame) -> None:
        key = (frame.owner_pid, frame.page_id)
        self._global_order[key] = frame
        self._local_order[frame.owner_pid][key] = frame

    def on_page_removed(self, frame: MemoryFrame) -> None:
        key = (frame.owner_pid, frame.page_id)
        self._global_order.pop(key, None)
        self._local_order[frame.owner_pid].pop(key, None)

    def select_victim(self, _frames, process, _page_id, _current_time, config):
        return self._select_from_order(process, config)

    def _select_from_order(self, process: Process, config: SimulationConfig) -> MemoryFrame:
        order = self._global_order
        if config.memory_policy == "local":
            order = self._local_order[process.pid] or order
        if not order:
            raise ValueError("FIFO precisa de ao menos uma moldura candidata.")
        return next(iter(order.values()))

class LRUPageReplacement(FIFOPageReplacement):
    def on_page_accessed(self, frame: MemoryFrame) -> None:
        # No hit, a pagina passa a ser a mais recente em ambas as filas, em O(1).
        key = (frame.owner_pid, frame.page_id)
        for order in (self._global_order, self._local_order[frame.owner_pid]):
            if key in order:
                order.move_to_end(key)

    def select_victim(
        self,
        frames: list[MemoryFrame],
        process: Process,
        page_id: int,
        current_time: int,
        config: SimulationConfig,
    ) -> MemoryFrame:
        if self._global_order:
            return self._select_from_order(process, config)
        if not frames:
            raise ValueError("Nenhuma moldura disponivel para substituicao.")
        return min(frames, key=attrgetter("last_used_time", "owner_pid", "page_id"))

class NUFPageReplacement(PageReplacementAlgorithm):
    needs_candidate_frames = False

    def __init__(self) -> None:
        self._global_buckets: dict[int, set[tuple[str, int]]] = {}
        self._local_buckets = defaultdict(dict)
        # (pid, page_id) -> {"frame": MemoryFrame, "freq": int}
        self._frames_by_key: dict = {}

    def on_page_loaded(self, frame: MemoryFrame) -> None:
        key = (frame.owner_pid, frame.page_id)
        self._frames_by_key[key] = {"frame": frame, "freq": 128}
        for buckets in (self._global_buckets, self._local_buckets[frame.owner_pid]):
            buckets.setdefault(128, set()).add(key)

    def on_page_accessed(self, frame: MemoryFrame) -> None:
        key = (frame.owner_pid, frame.page_id)
        meta = self._frames_by_key.get(key)
        if not meta:
            return

        self._remove_from_buckets(frame, meta["freq"])
        meta["freq"] += 128
        for buckets in (self._global_buckets, self._local_buckets[frame.owner_pid]):
            buckets.setdefault(meta["freq"], set()).add(key)

    def on_page_removed(self, frame: MemoryFrame) -> None:
        meta = self._frames_by_key.pop((frame.owner_pid, frame.page_id), None)
        if meta:
            self._remove_from_buckets(frame, meta["freq"])

    def _remove_from_buckets(self, frame: MemoryFrame, freq: int) -> None:
        for buckets in (self._global_buckets, self._local_buckets[frame.owner_pid]):
            if freq in buckets:
                buckets[freq].discard((frame.owner_pid, frame.page_id))
                if not buckets[freq]:
                    del buckets[freq]

    def select_victim(
        self,
        frames: list[MemoryFrame],
        process: Process,
        page_id: int,
        current_time: int,
        config: SimulationConfig,
    ) -> MemoryFrame:
        buckets = self._global_buckets
        if config.memory_policy == "local":
            buckets = self._local_buckets[process.pid] or buckets

        if not self._frames_by_key:
            if not frames:
                raise ValueError("Nenhuma moldura disponivel para substituicao.")
            return min(frames, key=attrgetter("last_used_time", "owner_pid", "page_id"))

        if not buckets:
            raise ValueError("NUF precisa de ao menos uma moldura candidata.")
        bucket = buckets[min(buckets)]
        if not bucket:
            raise ValueError("Bucket de frequência está vazio.")

        victim_key = min(bucket, key=lambda key: (key[1], key[0]))
        return self._frames_by_key[victim_key]["frame"]

class OptimalPageReplacement(PageReplacementAlgorithm):
    def __init__(self):
        self._processes: dict[str, Process] = {}

    def prepare(self, processes: list[Process]) -> None:
        for process in processes:
            self._processes[process.pid] = process

    def select_victim(
        self,
        frames: list[MemoryFrame],
        process: Process,
        page_id: int,
        current_time: int,
        config: SimulationConfig,
    ) -> MemoryFrame:
        if not frames:
            raise ValueError("Nenhuma moldura disponivel para substituicao.")

        def distance_key(frame: MemoryFrame) -> tuple:
            proc = self._processes.get(frame.owner_pid)
            if not proc:
                return (float('-inf'), frame.owner_pid, frame.page_id)

            current_index = proc.current_page_access_index
            try:
                next_index = proc.page_access_sequence.index(frame.page_id, current_index)
            except ValueError:
                return (float('-inf'), frame.owner_pid, frame.page_id)
            return (current_index - next_index, frame.owner_pid, frame.page_id)

        return min(frames, key=distance_key)

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

class Memory:
    def __init__(
        self,
        config: SimulationConfig,
        replacement_algorithm: PageReplacementAlgorithm,
    ) -> None:
        self.config = config
        self.replacement_algorithm = replacement_algorithm
        self._frames_by_key: dict[tuple[str, int], MemoryFrame] = {}
        self._frame_count_by_pid: defaultdict[str, int] = defaultdict(int)
        self.exchange_count = 0

    @property
    def frames(self) -> list[MemoryFrame]:
        return list(self._frames_by_key.values())

    def access_page(
        self,
        process: Process,
        page_id: int,
        current_time: int,
    ) -> None:
        loaded_frame = self.find_loaded_page(process.pid, page_id)
        if loaded_frame is not None:
            loaded_frame.register_access(current_time)
            self.replacement_algorithm.on_page_accessed(loaded_frame)
            return

        if self.has_free_frame(process):
            self.load_page(process, page_id, current_time)
            return

        self.replace_page(process, page_id, current_time)

    def find_loaded_page(self, pid: str, page_id: int) -> MemoryFrame | None:
        return self._frames_by_key.get((pid, page_id))

    def has_free_frame(self, process: Process) -> bool:
        if self.config.total_frames is None:
            return False

        if self.config.memory_policy == "local":
            return (
                len(self._frames_by_key) < self.config.total_frames
                and self._frame_count_by_pid[process.pid]
                < self._process_frame_limit(process)
            )

        return len(self._frames_by_key) < self.config.total_frames

    def load_page(
        self,
        process: Process,
        page_id: int,
        current_time: int,
    ) -> MemoryFrame:
        frame = MemoryFrame(
            owner_pid=process.pid,
            page_id=page_id,
            load_time=current_time,
            last_used_time=current_time,
        )
        self._frames_by_key[(process.pid, page_id)] = frame
        self._frame_count_by_pid[process.pid] += 1
        self.replacement_algorithm.on_page_loaded(frame)
        return frame

    def replace_page(
        self,
        process: Process,
        page_id: int,
        current_time: int,
    ) -> MemoryFrame:
        candidate_frames = (
            self._replacement_candidates(process)
            if self.replacement_algorithm.needs_candidate_frames
            else []
        )
        victim = self.replacement_algorithm.select_victim(
            candidate_frames,
            process,
            page_id,
            current_time,
            self.config,
        )
        self._frames_by_key.pop((victim.owner_pid, victim.page_id))
        self._frame_count_by_pid[victim.owner_pid] -= 1
        self.replacement_algorithm.on_page_removed(victim)
        self.exchange_count += 1
        return self.load_page(process, page_id, current_time)

    def _replacement_candidates(self, process: Process) -> list[MemoryFrame]:
        if self.config.memory_policy == "local":
            local_candidates = [
                frame
                for frame in self._frames_by_key.values()
                if frame.owner_pid == process.pid
            ]
            return local_candidates or self.frames
        return self.frames

    def _process_frame_limit(self, process: Process) -> int:
        if (
            process.virtual_pages is None
            or self.config.allocation_percentage is None
        ):
            return 0

        allocated_pages = (
            process.virtual_pages * self.config.allocation_percentage
        ) // 100
        return max(1, allocated_pages)
