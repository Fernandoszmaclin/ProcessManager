import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from process_manager.main import run
from process_manager.memory.models import MemorySimulationResult


class MainMemoryIntegrationTest(unittest.TestCase):
    def test_does_not_run_memory_comparison_without_memory_config(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            input_file = Path(temp_dir) / "entrada.txt"
            input_file.write_text(
                "alternanciaCircular|2\n"
                "0|1|2|1\n",
                encoding="utf-8",
            )

            with patch("process_manager.main.MemoryComparisonRunner") as runner:
                with redirect_stdout(io.StringIO()):
                    run(str(input_file))

        runner.assert_not_called()

    def test_runs_memory_comparison_with_memory_config(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            input_file = Path(temp_dir) / "entrada_memoria.txt"
            input_file.write_text(
                "alternanciaCircular|1|global|2|1|100\n"
                "0|1|2|1|3|1 2\n",
                encoding="utf-8",
            )

            fake_runner = patch("process_manager.main.MemoryComparisonRunner")
            with fake_runner as runner_class:
                runner_class.return_value.run.return_value = MemorySimulationResult(
                    fifo_exchanges=1,
                    lru_exchanges=2,
                    nuf_exchanges=3,
                    optimal_exchanges=1,
                    best_algorithm="fifo",
                )

                output = io.StringIO()
                with redirect_stdout(output):
                    run(str(input_file))

        runner_class.assert_called_once()
        self.assertIn("Memoria:", output.getvalue())
        self.assertIn("1|2|3|1|fifo", output.getvalue())


if __name__ == "__main__":
    unittest.main()
