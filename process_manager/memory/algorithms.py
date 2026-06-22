from collections import OrderedDict, defaultdict

from process_manager.models import Process, SimulationConfig
from process_manager.memory.models import MemoryFrame
from process_manager.memory.replacement import PageReplacementAlgorithm


class FIFOPageReplacement(PageReplacementAlgorithm):
    needs_candidate_frames = False

    def __init__(self):
        self._global_order = OrderedDict()
        self._local_order = defaultdict(OrderedDict)
        self._frames_by_key = {} # (pid, page_id) -> frame

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
        if config.memory_policy == "local" and not order:
            order = self._global_order

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
        if config.memory_policy == "local" and not order:
            order = self._global_order

        if not order:
            raise ValueError("LRU precisa de ao menos uma moldura candidata.")

        # pega a chave da primeira posição do dicionário (a mais antiga/menos usada)
        lru_key = next(iter(order))
        return self._frames_by_key[lru_key]

    @staticmethod
    def _key(frame: MemoryFrame) -> tuple[str, int]:
        return (frame.owner_pid, frame.page_id)


class NUFPageReplacement(PageReplacementAlgorithm):

    needs_candidate_frames = False

    def __init__(self) -> None:
        # freq -> OrderedDict[key -> None]
        self._global_buckets: dict = {}
        # pid -> {freq -> OrderedDict[key -> None]}
        self._local_buckets: defaultdict = defaultdict(dict)

        # (pid,page_id) -> {"frame": MemoryFrame, "freq": int}
        self._frames_by_key: dict = {}

    def on_page_loaded(self, frame: MemoryFrame) -> None:
        key = self._key(frame)
        freq = 128
        self._frames_by_key[key] = {"frame": frame, "freq": freq}

        if freq not in self._global_buckets:
            self._global_buckets[freq] = OrderedDict()
        self._global_buckets[freq][key] = None

        if freq not in self._local_buckets[frame.owner_pid]:
            self._local_buckets[frame.owner_pid][freq] = OrderedDict()
        self._local_buckets[frame.owner_pid][freq][key] = None

    def on_page_accessed(self, frame: MemoryFrame) -> None:
        key = self._key(frame)
        meta = self._frames_by_key.get(key)
        if not meta:
            return

        old_freq = meta["freq"]
        new_freq = old_freq + 128
        meta["freq"] = new_freq
        pid = frame.owner_pid

        # remove from old buckets (global/local)
        if old_freq in self._global_buckets:
            self._global_buckets[old_freq].pop(key, None)
            if not self._global_buckets[old_freq]:
                del self._global_buckets[old_freq]

        if old_freq in self._local_buckets[pid]:
            self._local_buckets[pid][old_freq].pop(key, None)
            if not self._local_buckets[pid][old_freq]:
                del self._local_buckets[pid][old_freq]

        # add to new buckets (global/local)
        if new_freq not in self._global_buckets:
            self._global_buckets[new_freq] = OrderedDict()
        self._global_buckets[new_freq][key] = None

        if new_freq not in self._local_buckets[pid]:
            self._local_buckets[pid][new_freq] = OrderedDict()
        self._local_buckets[pid][new_freq][key] = None

    def on_page_removed(self, frame: MemoryFrame) -> None:
        key = self._key(frame)
        meta = self._frames_by_key.pop(key, None)
        if not meta:
            return

        freq = meta["freq"]
        pid = frame.owner_pid

        if freq in self._global_buckets:
            self._global_buckets[freq].pop(key, None)
            if not self._global_buckets[freq]:
                del self._global_buckets[freq]

        if freq in self._local_buckets[pid]:
            self._local_buckets[pid][freq].pop(key, None)
            if not self._local_buckets[pid][freq]:
                del self._local_buckets[pid][freq]

    def select_victim(
        self,
        frames: list[MemoryFrame],
        process: Process,
        page_id: int,
        current_time: int,
        config: SimulationConfig,
    ) -> MemoryFrame:
        # escolher buckets conforme política
        buckets = (
            self._local_buckets[process.pid]
            if config.memory_policy == "local"
            else self._global_buckets
        )
        if config.memory_policy == "local" and not buckets:
            buckets = self._global_buckets

        # se não tivermos estrutura interna (ex: nenhum frame indexado), cair no fallback
        if not self._frames_by_key:
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

        if not buckets:
            raise ValueError("NUF precisa de ao menos uma moldura candidata.")

        min_freq = min(buckets.keys())
        bucket = buckets[min_freq]

        if not bucket:
            raise ValueError("Bucket de frequência está vazio.")

        victim_key = min(bucket, key=lambda key: (key[1], key[0]))
        return self._frames_by_key[victim_key]["frame"]

    @staticmethod
    def _key(frame: MemoryFrame) -> tuple[str, int]:
        return (frame.owner_pid, frame.page_id)


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
