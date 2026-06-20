from collections import defaultdict

from process_manager.models import Process, SimulationConfig
from process_manager.memory.models import MemoryFrame
from process_manager.memory.replacement import PageReplacementAlgorithm


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
                and self._local_frame_count(process.pid)
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
        self._remove_frame(victim)
        self.replacement_algorithm.on_page_removed(victim)
        self.exchange_count += 1
        return self.load_page(process, page_id, current_time)

    def _replacement_candidates(self, process: Process) -> list[MemoryFrame]:
        if self.config.memory_policy == "local":
            return [
                frame
                for frame in self._frames_by_key.values()
                if frame.owner_pid == process.pid
            ]
        return list(self._frames_by_key.values())

    def _local_frame_count(self, pid: str) -> int:
        return self._frame_count_by_pid[pid]

    def _remove_frame(self, frame: MemoryFrame) -> None:
        key = (frame.owner_pid, frame.page_id)
        self._frames_by_key.pop(key)
        self._frame_count_by_pid[frame.owner_pid] -= 1

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
