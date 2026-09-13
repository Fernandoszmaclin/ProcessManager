import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from process_manager.io import IODeviceConfig
from process_manager.models import Process, ProcessState, SimulationConfig
from process_manager.src.parser import parse_input_file
from process_manager.src.scheduler_factory import create_scheduler
from process_manager.src.simulation import Simulation


class IOTest(unittest.TestCase):
    def test_parser_reads_devices_and_request_chance(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "entrada.txt"
            path.write_text(
                "alternanciaCircular|2|global|4|1|100|1\n"
                "disk|1|3\n"
                "0|p1|5|1|2|1 2|75\n",
                encoding="utf-8",
            )
            config, processes = parse_input_file(str(path))

        self.assertEqual(config.io_devices, (IODeviceConfig("disk", 1, 3),))
        self.assertEqual(processes[0].io_request_chance, 75)

    def test_blocking_queue_and_completion(self) -> None:
        config = SimulationConfig.create(
            "alternanciaCircular",
            2,
            "global",
            4,
            1,
            100,
            (IODeviceConfig("disk", 1, 2),),
        )
        processes = [
            Process.create(0, "p1", 3, 1, io_request_chance=100),
            Process.create(0, "p2", 3, 1, io_request_chance=100),
        ]

        with patch("process_manager.src.simulation.random.randrange", return_value=0),              patch("process_manager.src.simulation.random.randint", return_value=1),              patch("process_manager.src.simulation.random.choice", return_value="disk"):
            report = Simulation(
                config,
                processes,
                create_scheduler("alternanciaCircular", 2),
            ).run()

        self.assertTrue(all(process.state is ProcessState.FINISHED for process in processes))
        self.assertTrue(all(process.blocked_time > 0 for process in processes))
        self.assertGreater(max(process.finish_time for process in processes), 3)
        self.assertTrue(report.state_log)
        self.assertIn("disk", report.state_log[0])


if __name__ == "__main__":
    unittest.main()
