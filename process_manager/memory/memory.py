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
        self.frames: list[MemoryFrame] = []
        self.exchange_count = 0

    def access_page(
        self,
        process: Process,
        page_id: int,
        current_time: int,
    ) -> None:
        loaded_frame = self.find_loaded_page(process.pid, page_id)
        if loaded_frame is not None:
            loaded_frame.register_access(current_time)
            return

        if self.has_free_frame(process):
            self.load_page(process, page_id, current_time)
            return

        self.replace_page(process, page_id, current_time)

    def find_loaded_page(self, pid: str, page_id: int) -> MemoryFrame | None:
        for frame in self.frames:
            if frame.matches(pid, page_id):
                return frame
        return None

    def has_free_frame(self, process: Process) -> bool:
        if self.config.total_frames is None:
            return False

        if self.config.memory_policy == "local":
            return (
                len(self.frames) < self.config.total_frames
                and self._local_frame_count(process.pid)
                < self._process_frame_limit(process)
            )

        return len(self.frames) < self.config.total_frames

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
        self.frames.append(frame)
        return frame

    def replace_page(
        self,
        process: Process,
        page_id: int,
        current_time: int,
    ) -> MemoryFrame:
        candidate_frames = self._replacement_candidates(process)
        victim = self.replacement_algorithm.select_victim(
            candidate_frames,
            process,
            page_id,
            current_time,
            self.config,
        )
        self.frames.remove(victim)
        self.exchange_count += 1
        return self.load_page(process, page_id, current_time)

    def _replacement_candidates(self, process: Process) -> list[MemoryFrame]:
        if self.config.memory_policy == "local":
            return [
                frame for frame in self.frames if frame.owner_pid == process.pid
            ]
        return list(self.frames)

    def _local_frame_count(self, pid: str) -> int:
        return len([frame for frame in self.frames if frame.owner_pid == pid])

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
