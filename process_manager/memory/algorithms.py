from collections import OrderedDict, defaultdict
from operator import attrgetter

from process_manager.models import Process, SimulationConfig
from process_manager.memory.models import MemoryFrame
from process_manager.memory.replacement import PageReplacementAlgorithm


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
