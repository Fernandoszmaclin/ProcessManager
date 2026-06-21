from collections import OrderedDict, defaultdict

from process_manager.models import Process, SimulationConfig
from process_manager.memory.models import MemoryFrame
from process_manager.memory.replacement import PageReplacementAlgorithm


class FIFOPageReplacement(PageReplacementAlgorithm):
    needs_candidate_frames = False

    def __init__(self):
        self._global_order = OrderedDict()
        self._local_order = defaultdict(OrderedDict)
        self._frames_by_key = {} # dict para recuperar página com acesso O(1)

    def on_page_loaded(self, frame):
        # pagina recem carregada entra no fim da fila
        key = self._key(frame)
        self._frames_by_key[key] = frame
        self._global_order[key] = None
        self._local_order[frame.owner_pid][key] = None

    def on_page_removed(self, frame):
        # remove a pagina dos indices internos quando ela sai da memoria
        key = self._key(frame)
        self._frames_by_key.pop(key, None)
        self._global_order.pop(key, None)
        self._local_order[frame.owner_pid].pop(key, None)

    def select_victim(self,_frames,process,_page_id,_current_time,config):
        return self._select_from_order(process, config)

    def _select_from_order(self,process,config):
        order = (
            self._local_order[process.pid]
            if config.memory_policy == "local"
            else self._global_order
        )

        if not order:
            raise ValueError("FIFO precisa de ao menos uma moldura candidata.")

        # primeira chave representa a pagina mais antiga em memoria
        victim_key = next(iter(order))
        return self._frames_by_key[victim_key]

    @staticmethod
    def _key(frame):
        return (frame.owner_pid, frame.page_id)


class LRUPageReplacement(PageReplacementAlgorithm):
    needs_candidate_frames = False

    def __init__(self) -> None:
        # orderedDict mantem a ordem O(1) --> inicio é o mais antigo, fim é o mais recente
        self._global_order: OrderedDict[tuple[str, int], None] = OrderedDict()
        self._local_order: defaultdict[str, OrderedDict[tuple[str, int], None]] = defaultdict(OrderedDict)
        self._frames_by_key: dict[tuple[str, int], MemoryFrame] = {}

    def on_page_loaded(self, frame: MemoryFrame) -> None:
        """quando uma pagina é carregada (MISS), entra no final da fila (mais recente)"""
        key = self._key(frame)
        self._frames_by_key[key] = frame
        self._global_order[key] = None
        self._local_order[frame.owner_pid][key] = None

    def on_page_accessed(self, frame: MemoryFrame) -> None:
        """quando ocorre um HIT, movemos para o final da fila (mais recente) em O(1)"""
        key = self._key(frame)
        
        if key in self._global_order:
            self._global_order.move_to_end(key)
        
        if key in self._local_order[frame.owner_pid]:
            self._local_order[frame.owner_pid].move_to_end(key)

    def on_page_removed(self, frame: MemoryFrame) -> None:
        """quando a vitima é removida, deletamos da memória e da fila em O(1)"""
        key = self._key(frame)
        self._frames_by_key.pop(key, None)
        self._global_order.pop(key, None)
        self._local_order[frame.owner_pid].pop(key, None)

    def select_victim(
        self,
        frames: list[MemoryFrame],
        process: Process,
        page_id: int,
        current_time: int,
        config: SimulationConfig,
    ) -> MemoryFrame:
        if self._frames_by_key:
            return self._select_from_order(process, config)

        if not frames:
            raise ValueError("Nenhuma moldura disponivel para substituicao.")
        return min(
            frames,
            key=lambda frame: (
                frame.last_used_time,
                frame.owner_pid,
                frame.page_id,
            ),
        )

    def _select_from_order(
        self,
        process: Process,
        config: SimulationConfig,
    ) -> MemoryFrame:
        order = (
            self._local_order[process.pid]
            if config.memory_policy == "local"
            else self._global_order
        )

        if not order:
            raise ValueError("LRU precisa de ao menos uma moldura candidata.")

        # pega a chave da primeira posição do dicionário (a mais antiga/menos usada)
        lru_key = next(iter(order))
        return self._frames_by_key[lru_key]

    @staticmethod
    def _key(frame: MemoryFrame) -> tuple[str, int]:
        return (frame.owner_pid, frame.page_id)
    

class NUFPageReplacement(PageReplacementAlgorithm):
    def select_victim(
        self,
        frames: list[MemoryFrame],
        process: Process,
        page_id: int,
        current_time: int,
        config: SimulationConfig,
    ) -> MemoryFrame:
        raise NotImplementedError("NUF sera implementado em uma etapa futura.")


class OptimalPageReplacement(PageReplacementAlgorithm):
    def __init__(self):
        self._processes: dict[str, Process] = {}

    def prepare(self, processes: list[Process]) -> None:
        for process in processes:
            self._processes[process.pid] = process

    def select_victim(
        self,
        frames: list[MemoryFrame],
        process: Process,
        page_id: int,
        current_time: int,
        config: SimulationConfig,
    ) -> MemoryFrame:
        if not frames:
            raise ValueError("Nenhuma moldura disponivel para substituicao.")

        def distance_key(frame: MemoryFrame) -> tuple:
            proc = self._processes.get(frame.owner_pid)
            if not proc:
                return (float('-inf'), frame.owner_pid, frame.page_id)

            current_index = proc.current_page_access_index
            future = proc.page_access_sequence[current_index:]

            for idx, page in enumerate(future):
                if page == frame.page_id:
                    return (-idx, frame.owner_pid, frame.page_id)

            return (float('-inf'), frame.owner_pid, frame.page_id)

        return min(frames, key=distance_key)
