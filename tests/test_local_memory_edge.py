import unittest

from process_manager.memory.algorithms import (
    FIFOPageReplacement,
    LRUPageReplacement,
    NUFPageReplacement,
    OptimalPageReplacement,
)
from process_manager.memory.memory import Memory
from process_manager.models import Process, SimulationConfig


class LocalMemoryEdgeTest(unittest.TestCase):
    def test_local_policy_falls_back_when_process_has_no_candidate(self) -> None:
        config = SimulationConfig.create(
            algorithm="alternanciaCircular",
            cpu_fraction=1,
            memory_policy="local",
            main_memory_size=1,
            page_frame_size=1,
            allocation_percentage=100,
        )
        process1 = Process.create(0, "p1", 1, 1, memory_amount=1, page_frame_size=1)
        process2 = Process.create(0, "p2", 1, 1, memory_amount=1, page_frame_size=1)

        for algorithm in (
            FIFOPageReplacement(),
            LRUPageReplacement(),
            NUFPageReplacement(),
            OptimalPageReplacement(),
        ):
            with self.subTest(algorithm=algorithm.__class__.__name__):
                algorithm.prepare([process1, process2])
                memory = Memory(config, algorithm)

                memory.access_page(process1, page_id=1, current_time=1)
                memory.access_page(process2, page_id=1, current_time=2)

                self.assertEqual(memory.exchange_count, 1)
                self.assertEqual(len(memory.frames), 1)
                self.assertEqual(memory.frames[0].owner_pid, "p2")


if __name__ == "__main__":
    unittest.main()
