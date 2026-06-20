import copy
import sys
from .memory.comparison import MemoryComparisonRunner
from .memory.formatter import MemoryResultFormatter
from .parser import parse_input_file
from .scheduler_factory import create_scheduler
from .simulation import Simulation


def main() -> None:
    run(sys.argv[1])


def run(input_path: str) -> None:
    config, processes = parse_input_file(input_path)                            # funcao para chamar a simulacao a partir da linha de comando
    memory_processes = copy.deepcopy(processes)
    scheduler = create_scheduler(config.algorithm, config.cpu_fraction)         # define qual algoritmo sera usado
    report = Simulation(config, processes, scheduler).run()                     # executa simulacao e gera o relatorio

    report.print_timeline()
    report.print_summary()

    if config.has_memory_config:
        memory_result = MemoryComparisonRunner(config, memory_processes).run()
        print()
        print("Memoria:")
        print(MemoryResultFormatter().format(memory_result))
