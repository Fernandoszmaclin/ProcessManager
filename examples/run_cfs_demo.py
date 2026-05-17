from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from scheduler.algorithms.cfs import CfsScheduler
from scheduler.core.process import Process
from scheduler.simulation.engine import Simulation


def main() -> None:
    processes = [
        Process(pid=1, arrival_time=0, burst_time=6, weight=1024),
        Process(pid=2, arrival_time=1, burst_time=4, weight=1024),
        Process(pid=3, arrival_time=2, burst_time=3, weight=2048),
    ]

    simulation = Simulation(processes=processes, scheduler=CfsScheduler())
    simulation.run()

    print("Execution log:")
    for event in simulation.events:
        print(f"t={event.time:02d}: {event.message}")

    print("\nFinal process table:")
    for process in processes:
        print(
            f"P{process.pid}: "
            f"start={process.start_time}, "
            f"finish={process.finish_time}, "
            f"turnaround={process.turnaround_time}, "
            f"waiting={process.waiting_time}, "
            f"response={process.response_time}, "
            f"vruntime={process.vruntime:.2f}"
        )

    print("\nAverages:")
    for name, value in simulation.metrics().items():
        print(f"{name}: {value:.2f}")


if __name__ == "__main__":
    main()
