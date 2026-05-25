import sys
from .parser import parse_input_file
from .scheduler_factory import create_scheduler
from .simulation import Simulation


def main() -> None:
    config, processes = parse_input_file(sys.argv[1])                           # funcao para chamar a simulacao a partir da linha de comando
    scheduler = create_scheduler(config.algorithm, config.cpu_fraction)         # define qual algoritmo sera usado
    report = Simulation(config, processes, scheduler).run()                     # executa simulacao e gera o relatorio

    report.print_timeline()
    report.print_summary()
