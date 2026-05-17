from .schedulers.base import Scheduler
from .schedulers.cfs import CFSScheduler
from .schedulers.lottery import LotteryScheduler
from .schedulers.priority import PriorityScheduler
from .schedulers.round_robin import RoundRobinScheduler


def create_scheduler(algorithm: str, cpu_fraction: int) -> Scheduler:
    if algorithm == "alternanciaCircular":
        return RoundRobinScheduler(cpu_fraction)
    if algorithm == "prioridade":
        return PriorityScheduler(cpu_fraction)
    if algorithm == "loteria":
        return LotteryScheduler(cpu_fraction)
    if algorithm == "CFS":
        return CFSScheduler(cpu_fraction)