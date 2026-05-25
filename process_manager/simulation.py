from .models import Process, ProcessState, SimulationConfig
from .report import SimulationReport, TimelineEntry
from .schedulers.base import Scheduler


class Simulation:
    def __init__(
        self,
        config: SimulationConfig,
        processes: list[Process],
        scheduler: Scheduler,
    ) -> None:
        self.config = config
        self.processes = processes
        self.scheduler = scheduler
        self.timeline: list[TimelineEntry] = []     # historico de execucao
        self.current_time = 0                       # relogio virtual da simulacao

    def run(self) -> SimulationReport:
        # copia de lista de processos
        pending = list(self.processes)
        finished_count = 0

        while finished_count < len(self.processes):
            self._admit_new_processes(pending)

            if not self.scheduler.has_ready_process():
                self.current_time = pending[0].creation_time
                continue

            process = self.scheduler.pick_next()
            process.state = ProcessState.RUNNING

            slice_start = self.current_time
            time_to_run = min(self.config.cpu_fraction, process.remaining_time)

            for _ in range(time_to_run):
                # aumenta o tempo de espera de quem ficou na fila
                for ready_process in self.scheduler.ready_processes():
                    ready_process.ready_time += 1

                self.current_time += 1
                process.remaining_time -= 1
                self._admit_new_processes(pending)      # verifica se algum processo novo chegou no meio da execucao atual

            # registra o que aconteceu nesse slice de tempo
            self.timeline.append(
                TimelineEntry(
                    start_time=slice_start,
                    end_time=self.current_time,
                    pid=process.pid,
                    remaining_time=process.remaining_time,
                )
            )

            # verifica estado do processo após usar a fatia de tempo
            if process.remaining_time == 0:
                process.state = ProcessState.FINISHED
                process.finish_time = self.current_time
                finished_count += 1
            else:
                process.state = ProcessState.READY
                self.scheduler.on_process_preempted(process)

        return SimulationReport(self.timeline, self.processes)

    def _admit_new_processes(self, pending: list[Process]) -> None:
        # verifica se existe processo pendente e se o tempo de criacao do processo e menor ou igual ao tempo atual da simulacao
        while pending and pending[0].creation_time <= self.current_time:
            process = pending.pop(0)
            process.state = ProcessState.READY
            self.scheduler.add_process(process)
