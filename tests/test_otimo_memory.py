import unittest

from process_manager.memory.algorithms import (
    FIFOPageReplacement,
    OptimalPageReplacement,
)
from process_manager.memory.memory import Memory
from process_manager.memory.models import MemoryFrame
from process_manager.models import Process, SimulationConfig


def _run_reference_string(
    algorithm,
    config: SimulationConfig,
    process: Process,
) -> Memory:
    algorithm.prepare([process])
    memory = Memory(config, algorithm)

    current_time = 0
    while True:
        page_id = process.next_page_access()
        if page_id is None:
            break
        current_time += 1
        memory.access_page(process, page_id, current_time)

    return memory


class OptimalPageReplacementTest(unittest.TestCase):
    def test_evicts_page_used_farthest_in_the_future(self) -> None:
        process = Process.create(0, "p1", 1, 1)
        process.page_access_sequence = [9, 9, 1, 1, 2]
        process.current_page_access_index = 2

        algorithm = OptimalPageReplacement()
        algorithm.prepare([process])

        frames = [
            MemoryFrame("p1", 1, load_time=1, last_used_time=1),
            MemoryFrame("p1", 2, load_time=2, last_used_time=2),
            MemoryFrame("p1", 3, load_time=3, last_used_time=3),
        ]

        victim = algorithm.select_victim(
            frames,
            process,
            page_id=4,
            current_time=10,
            config=SimulationConfig.create("alternanciaCircular", 1),
        )

        self.assertEqual(victim.page_id, 3)

    def test_prefers_reused_page_with_largest_distance(self) -> None:
        process = Process.create(0, "p1", 1, 1)
        process.page_access_sequence = [5, 1, 2]
        process.current_page_access_index = 1

        algorithm = OptimalPageReplacement()
        algorithm.prepare([process])

        frames = [
            MemoryFrame("p1", 1, load_time=1, last_used_time=1),
            MemoryFrame("p1", 2, load_time=2, last_used_time=2),
        ]

        victim = algorithm.select_victim(
            frames,
            process,
            page_id=9,
            current_time=10,
            config=SimulationConfig.create("alternanciaCircular", 1),
        )

        self.assertEqual(victim.page_id, 2)

    def test_breaks_ties_by_pid_then_page_id(self) -> None:
        process = Process.create(0, "p3", 1, 1)
        process.page_access_sequence = [7, 7]
        process.current_page_access_index = 2

        algorithm = OptimalPageReplacement()
        algorithm.prepare([process])

        frames = [
            MemoryFrame("p2", 2, load_time=10, last_used_time=20),
            MemoryFrame("p2", 1, load_time=15, last_used_time=20),
            MemoryFrame("p1", 8, load_time=5, last_used_time=20),
        ]

        victim = algorithm.select_victim(
            frames,
            process,
            page_id=1,
            current_time=40,
            config=SimulationConfig.create("alternanciaCircular", 1),
        )

        self.assertEqual(victim.owner_pid, "p1")
        self.assertEqual(victim.page_id, 8)

    def test_no_context_treats_every_frame_as_never_reused(self) -> None:
        algorithm = OptimalPageReplacement()
        frames = [
            MemoryFrame("p2", 5, load_time=1, last_used_time=1),
            MemoryFrame("p1", 9, load_time=2, last_used_time=2),
        ]

        victim = algorithm.select_victim(
            frames,
            Process.create(0, "p9", 1, 1),
            page_id=1,
            current_time=10,
            config=SimulationConfig.create("alternanciaCircular", 1),
        )

        self.assertEqual(victim.owner_pid, "p1")
        self.assertEqual(victim.page_id, 9)


class MemoryOptimalIntegrationTest(unittest.TestCase):
    REFERENCE_STRING = [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5]

    def _config(self) -> SimulationConfig:
        return SimulationConfig.create(
            algorithm="alternanciaCircular",
            cpu_fraction=1,
            memory_policy="global",
            main_memory_size=3,
            page_frame_size=1,
            allocation_percentage=100,
        )

    def _process(self) -> Process:
        process = Process.create(
            creation_time=0,
            pid="p1",
            total_time=len(self.REFERENCE_STRING),
            priority_or_tickets=1,
            memory_amount=5,
            page_frame_size=1,
        )
        process.page_access_sequence = list(self.REFERENCE_STRING)
        return process

    def test_optimal_matches_belady_minimum(self) -> None:
        memory = _run_reference_string(
            OptimalPageReplacement(), self._config(), self._process()
        )
        self.assertEqual(memory.exchange_count, 4)

    def test_optimal_does_no_worse_than_fifo(self) -> None:
        optimal = _run_reference_string(
            OptimalPageReplacement(), self._config(), self._process()
        )
        fifo = _run_reference_string(
            FIFOPageReplacement(), self._config(), self._process()
        )

        self.assertEqual(fifo.exchange_count, 6)
        self.assertLess(optimal.exchange_count, fifo.exchange_count)


if __name__ == "__main__":
    unittest.main()
