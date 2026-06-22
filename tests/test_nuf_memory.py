import unittest

from process_manager.memory.algorithms import NUFPageReplacement
from process_manager.memory.memory import Memory
from process_manager.models import Process, SimulationConfig


class MemoryNUFTest(unittest.TestCase):
    def test_global_nuf_replaces_least_frequently_used_frame(self) -> None:
        config = SimulationConfig.create(
            algorithm="alternanciaCircular",
            cpu_fraction=1,
            memory_policy="global",
            main_memory_size=2,
            page_frame_size=1,
            allocation_percentage=100,
        )
        memory = Memory(config, NUFPageReplacement())
        process = Process.create(0, "p1", 1, 1, memory_amount=3, page_frame_size=1)

        memory.access_page(process, page_id=1, current_time=1)
        memory.access_page(process, page_id=2, current_time=2)
        memory.access_page(process, page_id=1, current_time=3)
        memory.access_page(process, page_id=3, current_time=4)

        loaded_pages = sorted(frame.page_id for frame in memory.frames)
        self.assertEqual(loaded_pages, [1, 3])
        self.assertEqual(memory.exchange_count, 1)

    def test_global_nuf_breaks_frequency_tie_by_smallest_page_id(self) -> None:
        config = SimulationConfig.create(
            algorithm="alternanciaCircular",
            cpu_fraction=1,
            memory_policy="global",
            main_memory_size=2,
            page_frame_size=1,
            allocation_percentage=100,
        )
        memory = Memory(config, NUFPageReplacement())
        process = Process.create(0, "p1", 1, 1, memory_amount=3, page_frame_size=1)

        memory.access_page(process, page_id=2, current_time=1)
        memory.access_page(process, page_id=1, current_time=1)
        memory.access_page(process, page_id=3, current_time=2)

        loaded_pages = sorted(frame.page_id for frame in memory.frames)
        self.assertEqual(loaded_pages, [2, 3])
        self.assertEqual(memory.exchange_count, 1)

    def test_local_nuf_replaces_only_process_owned_frame(self) -> None:
        config = SimulationConfig.create(
            algorithm="alternanciaCircular",
            cpu_fraction=1,
            memory_policy="local",
            main_memory_size=4,
            page_frame_size=1,
            allocation_percentage=50,
        )
        memory = Memory(config, NUFPageReplacement())
        process1 = Process.create(0, "p1", 1, 1, memory_amount=4, page_frame_size=1)
        process2 = Process.create(0, "p2", 1, 1, memory_amount=4, page_frame_size=1)

        memory.access_page(process1, page_id=1, current_time=1)
        memory.access_page(process1, page_id=2, current_time=2)
        memory.access_page(process2, page_id=1, current_time=3)
        memory.access_page(process1, page_id=1, current_time=4)
        memory.access_page(process1, page_id=3, current_time=5)

        p1_pages = sorted(
            frame.page_id for frame in memory.frames if frame.owner_pid == "p1"
        )
        p2_pages = sorted(
            frame.page_id for frame in memory.frames if frame.owner_pid == "p2"
        )

        self.assertEqual(p1_pages, [1, 3])
        self.assertEqual(p2_pages, [1])
        self.assertEqual(memory.exchange_count, 1)


if __name__ == "__main__":
    unittest.main()
