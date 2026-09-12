import random
import unittest
from copy import deepcopy
from dataclasses import astuple

from process_manager.memory.comparison import MemoryComparisonRunner
from process_manager.models import Process, ProcessState, SimulationConfig
from process_manager.src.scheduler_factory import create_scheduler
from process_manager.src.simulation import Simulation


class SimulationRegressionTest(unittest.TestCase):
    def test_scheduling_and_memory_match_original_results(self) -> None:
        # Inclui chegada durante uma fatia, preempcao, CPU ociosa e sequencia curta.
        expected = {
            "alternanciaCircular": (
                "p2 p1 p3 p2 p1 p3 p2 p4",
                [(11, 6), (14, 7), (13, 6), (19, 0)],
                (10, 10, 10, 8, "empate"),
            ),
            "prioridade": (
                "p1 p1 p2 p2 p2 p3 p3 p4",
                [(5, 0), (10, 3), (14, 7), (19, 0)],
                (6, 6, 8, 6, "empate"),
            ),
            "loteria": (
                "p2 p1 p2 p1 p2 p3 p3 p4",
                [(9, 4), (10, 3), (14, 7), (19, 0)],
                (9, 8, 10, 6, "lru"),
            ),
            "CFS": (
                "p1 p2 p3 p1 p2 p3 p2 p4",
                [(9, 4), (14, 7), (13, 6), (19, 0)],
                (10, 10, 9, 8, "nuf"),
            ),
        }
        self.addCleanup(random.setstate, random.getstate())
        for name, (order, timings, exchanges) in expected.items():
            with self.subTest(scheduler=name):
                processes = [
                    Process.create(t, pid, duration, priority, 5, pages, 1)
                    for t, pid, duration, priority, pages in (
                        (2, "p2", 5, 2, [1, 2, 1, 3, 2]),
                        (2, "p1", 3, 1, [2, 1, 2]),
                        (3, "p3", 4, 3, [1, 2, 3, 1]),
                        (17, "p4", 2, 1, [1]),
                    )
                ]
                config = SimulationConfig.create(name, 2, "global", 3, 1, 100)
                original = deepcopy(processes)
                random.seed(73)
                result = MemoryComparisonRunner(config, processes).run()
                self.assertEqual(astuple(result), exchanges)
                self.assertEqual(processes, original)

                random.seed(73)
                scheduler = create_scheduler(name, 2)
                report = Simulation(config, processes, scheduler).run()
                self.assertEqual([entry.pid for entry in report.timeline], order.split())
                self.assertEqual(
                    [(p.finish_time, p.ready_time) for p in report.processes], timings
                )
                self.assertTrue(all(p.state == ProcessState.FINISHED for p in processes))
                self.assertFalse(scheduler.has_ready_process())


if __name__ == "__main__":
    unittest.main()
