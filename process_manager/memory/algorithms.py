from collections import OrderedDict, defaultdict
from heapq import heappop, heappush

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
    

class _FrequencyBuckets:
    def __init__(self) -> None:
        self._active_keys: dict[int, set[tuple[str, int]]] = {}
        self._heaps: dict[int, list[tuple[int, str, tuple[str, int]]]] = {}
        self._min_freq: int | None = None

    def __bool__(self) -> bool:
        return self._min_freq is not None

    def add(self, key: tuple[str, int], freq: int) -> None:
        self._active_keys.setdefault(freq, set()).add(key)
        self._heaps.setdefault(freq, [])
        heappush(self._heaps[freq], (key[1], key[0], key))
        if self._min_freq is None or freq < self._min_freq:
            self._min_freq = freq

    def remove(
        self,
        key: tuple[str, int],
        freq: int,
        refresh_min: bool = True,
    ) -> None:
        bucket = self._active_keys.get(freq)
        if bucket is None:
            return

        bucket.discard(key)
        if bucket:
            return

        del self._active_keys[freq]
        self._heaps.pop(freq, None)
        if self._min_freq == freq:
            self._min_freq = (
                min(self._active_keys)
                if refresh_min and self._active_keys
                else None
            )

    def move(
        self,
        key: tuple[str, int],
        old_freq: int,
        new_freq: int,
        refresh_min: bool = True,
    ) -> None:
        if old_freq == new_freq:
            return

        self.remove(key, old_freq, refresh_min=refresh_min)
        self.add(key, new_freq)

    def refresh_min(self) -> None:
        self._min_freq = min(self._active_keys) if self._active_keys else None

    def smallest_min_key(self) -> tuple[str, int]:
        if self._min_freq is None:
            raise ValueError("NUF precisa de ao menos uma moldura candidata.")

        active_keys = self._active_keys[self._min_freq]
        heap = self._heaps[self._min_freq]
        while heap:
            _, _, key = heap[0]
            if key in active_keys:
                return key
            heappop(heap)

        raise ValueError("Bucket de frequencia esta vazio.")


class NUFPageReplacement(PageReplacementAlgorithm):
    """
    NFU/NUF com aging por deslocamento.

    Operacoes esperadas:
    - escolha da vitima em O(1) amortizado
    - a cada ciclo, todos os contadores sao deslocados para a direita
    - a pagina acessada recebe o bit mais significativo: contador += 128
    """

    ACCESS_BIT = 128
    MAX_COUNTER = 255
    needs_candidate_frames = False

    def __init__(self) -> None:
        self._global_buckets = _FrequencyBuckets()
        self._local_buckets: defaultdict[str, _FrequencyBuckets] = defaultdict(
            _FrequencyBuckets
        )
        self._frames_by_key: dict[tuple[str, int], MemoryFrame] = {}
        self._freq_by_key: dict[tuple[str, int], int] = {}
        self._last_aging_time = 0

    def before_page_access(
        self,
        process: Process,
        page_id: int,
        current_time: int,
    ) -> None:
        self._age_until(current_time)

    def on_page_loaded(self, frame: MemoryFrame) -> None:
        key = self._key(frame)
        freq = self.ACCESS_BIT
        self._frames_by_key[key] = frame
        self._freq_by_key[key] = freq
        self._global_buckets.add(key, freq)
        self._local_buckets[frame.owner_pid].add(key, freq)

    def on_page_accessed(self, frame: MemoryFrame) -> None:
        key = self._key(frame)
        old_freq = self._freq_by_key.get(key)
        if old_freq is None:
            return

        self._set_frequency(
            key,
            frame.owner_pid,
            min(self.MAX_COUNTER, old_freq + self.ACCESS_BIT),
        )

    def on_page_removed(self, frame: MemoryFrame) -> None:
        key = self._key(frame)
        freq = self._freq_by_key.pop(key, None)
        if freq is None:
            return

        self._frames_by_key.pop(key, None)
        self._global_buckets.remove(key, freq, refresh_min=False)
        self._local_buckets[frame.owner_pid].remove(key, freq, refresh_min=False)

    def select_victim(
        self,
        frames: list[MemoryFrame],
        process: Process,
        page_id: int,
        current_time: int,
        config: SimulationConfig,
    ) -> MemoryFrame:
        buckets = (
            self._local_buckets[process.pid]
            if config.memory_policy == "local"
            else self._global_buckets
        )
        if config.memory_policy == "local" and not buckets:
            buckets = self._global_buckets

        if not buckets:
            raise ValueError("NUF precisa de ao menos uma moldura candidata.")

        return self._frames_by_key[buckets.smallest_min_key()]

    def _age_until(self, current_time: int) -> None:
        if current_time <= self._last_aging_time:
            return

        shifts = current_time - self._last_aging_time
        self._last_aging_time = current_time

        for key, old_freq in list(self._freq_by_key.items()):
            frame = self._frames_by_key[key]
            new_freq = old_freq >> shifts if shifts < old_freq.bit_length() else 0
            self._set_frequency(key, frame.owner_pid, new_freq, refresh_min=False)

        self._global_buckets.refresh_min()
        for buckets in self._local_buckets.values():
            buckets.refresh_min()

    def _set_frequency(
        self,
        key: tuple[str, int],
        pid: str,
        new_freq: int,
        refresh_min: bool = True,
    ) -> None:
        old_freq = self._freq_by_key[key]
        self._freq_by_key[key] = new_freq
        self._global_buckets.move(key, old_freq, new_freq, refresh_min)
        self._local_buckets[pid].move(key, old_freq, new_freq, refresh_min)

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
