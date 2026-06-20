from collections import defaultdict, deque

from process_manager.models import Process, SimulationConfig
from process_manager.memory.models import MemoryFrame
from process_manager.memory.replacement import PageReplacementAlgorithm
from collections import defaultdict, deque, OrderedDict

class FIFOPageReplacement(PageReplacementAlgorithm):
    needs_candidate_frames = False

    def __init__(self) -> None:
        self._global_order: deque[tuple[str, int]] = deque()
        self._local_order: defaultdict[str, deque[tuple[str, int]]] = defaultdict(deque)
        self._frames_by_key: dict[tuple[str, int], MemoryFrame] = {}

    def on_page_loaded(self, frame: MemoryFrame) -> None:
        key = self._key(frame)
        self._frames_by_key[key] = frame
        self._global_order.append(key)
        self._local_order[frame.owner_pid].append(key)

    def on_page_removed(self, frame: MemoryFrame) -> None:
        key = self._key(frame)
        self._frames_by_key.pop(key, None)
        self._remove_key(self._global_order, key)
        self._remove_key(self._local_order[frame.owner_pid], key)

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
            raise ValueError("FIFO precisa de ao menos uma moldura candidata.")

        return min(
            frames,
            key=lambda frame: (
                frame.load_time,
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
            raise ValueError("FIFO precisa de ao menos uma moldura candidata.")

        return self._frames_by_key[order[0]]

    @staticmethod
    def _key(frame: MemoryFrame) -> tuple[str, int]:
        return (frame.owner_pid, frame.page_id)

    @staticmethod
    def _remove_key(
        order: deque[tuple[str, int]],
        key: tuple[str, int],
    ) -> None:
        if order and order[0] == key:
            order.popleft()
            return

        try:
            order.remove(key)
        except ValueError:
            pass


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
    def select_victim(
        self,
        frames: list[MemoryFrame],
        process: Process,
        page_id: int,
        current_time: int,
        config: SimulationConfig,
    ) -> MemoryFrame:
        raise NotImplementedError("Otimo sera implementado em uma etapa futura.")
