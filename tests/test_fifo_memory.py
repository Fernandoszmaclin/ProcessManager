import unittest

from process_manager.memory.algorithms import FIFOPageReplacement
from process_manager.memory.memory import Memory
from process_manager.memory.models import MemoryFrame
from process_manager.models import Process, SimulationConfig


class FIFOPageReplacementTest(unittest.TestCase):
    def test_selects_oldest_loaded_frame(self) -> None:
        frames = [
            MemoryFrame("p1", 1, load_time=10, last_used_time=20),
            MemoryFrame("p2", 1, load_time=3, last_used_time=30),
            MemoryFrame("p3", 1, load_time=7, last_used_time=10),
        ]

        victim = FIFOPageReplacement().select_victim(
            frames,
            Process.create(0, "p4", 1, 1),
            page_id=1,
            current_time=40,
            config=SimulationConfig.create("alternanciaCircular", 1),
        )

        self.assertEqual(victim.owner_pid, "p2")
        self.assertEqual(victim.page_id, 1)


class MemoryFIFOTest(unittest.TestCase):
    def test_global_fifo_replaces_oldest_loaded_frame(self) -> None:
        config = SimulationConfig.create(
            algorithm="alternanciaCircular",
            cpu_fraction=1,
            memory_policy="global",
            main_memory_size=2,
            page_frame_size=1,
            allocation_percentage=100,
        )
        memory = Memory(config, FIFOPageReplacement())
        process = Process.create(
            creation_time=0,
            pid="p1",
            total_time=1,
            priority_or_tickets=1,
            memory_amount=3,
            page_frame_size=1,
        )

        memory.access_page(process, page_id=1, current_time=1)
        memory.access_page(process, page_id=2, current_time=2)
        memory.access_page(process, page_id=3, current_time=3)

        loaded_pages = sorted(frame.page_id for frame in memory.frames)
        self.assertEqual(loaded_pages, [2, 3])
        self.assertEqual(memory.exchange_count, 1)

    def test_local_fifo_replaces_only_process_owned_frame(self) -> None:
        config = SimulationConfig.create(
            algorithm="alternanciaCircular",
            cpu_fraction=1,
            memory_policy="local",
            main_memory_size=4,
            page_frame_size=1,
            allocation_percentage=50,
        )
        memory = Memory(config, FIFOPageReplacement())
        process_1 = Process.create(0, "p1", 1, 1, memory_amount=4, page_frame_size=1)
        process_2 = Process.create(0, "p2", 1, 1, memory_amount=4, page_frame_size=1)

        memory.access_page(process_1, page_id=1, current_time=1)
        memory.access_page(process_1, page_id=2, current_time=2)
        memory.access_page(process_2, page_id=1, current_time=3)
        memory.access_page(process_1, page_id=3, current_time=4)

        p1_pages = sorted(
            frame.page_id for frame in memory.frames if frame.owner_pid == "p1"
        )
        p2_pages = sorted(
            frame.page_id for frame in memory.frames if frame.owner_pid == "p2"
        )

        self.assertEqual(p1_pages, [2, 3])
        self.assertEqual(p2_pages, [1])
        self.assertEqual(memory.exchange_count, 1)


if __name__ == "__main__":
    unittest.main()
