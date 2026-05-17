import sys
from .parser import parse_input_file
from .scheduler_factory import create_scheduler
from .simulation import Simulation


def main() -> None:
    config, processes = parse_input_file(sys.argv[1])
    scheduler = create_scheduler(config.algorithm, config.cpu_fraction)
    report = Simulation(config, processes, scheduler).run()

    report.print_timeline()
    report.print_summary()
