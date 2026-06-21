from process_manager.schedulers.base import Scheduler
from process_manager.schedulers.cfs import CFSScheduler
from process_manager.schedulers.lottery import LotteryScheduler
from process_manager.schedulers.priority import PriorityScheduler
from process_manager.schedulers.round_robin import RoundRobinScheduler


def create_scheduler(algorithm: str, cpu_fraction: int) -> Scheduler:
    if algorithm in ("alternanciaCircular", "alternancia"):
        return RoundRobinScheduler(cpu_fraction)
    if algorithm == "prioridade":
        return PriorityScheduler(cpu_fraction)
    if algorithm == "loteria":
        return LotteryScheduler(cpu_fraction)
    if algorithm == "CFS":
        return CFSScheduler(cpu_fraction)
