import unittest

from process_manager.memory.algorithms import LRUPageReplacement
from process_manager.memory.memory import Memory
from process_manager.memory.models import MemoryFrame
from process_manager.models import Process, SimulationConfig

class LRUPageReplacementTest(unittest.TestCase):
    def test_selects_least_recently_used_frame(self) -> None:
        frames = [
            MemoryFrame("p1", 1, load_time=10, last_used_time=20),
            MemoryFrame("p2", 1, load_time=3, last_used_time=30),
            MemoryFrame("p3", 1, load_time=15, last_used_time=10),
        ]

        victim = LRUPageReplacement().select_victim(
            frames,
            Process.create(0, "p4", 1, 1),
            page_id=1,
            current_time=40,
            config=SimulationConfig.create("alternanciaCircular", 1),
        )

        self.assertEqual(victim.owner_pid, "p3")
        self.assertEqual(victim.page_id, 1)
    
    def test_selects_smallest_pid_and_page_id_on_tie(self) -> None:
        frames = [
            MemoryFrame("p2", 2, load_time=10, last_used_time=20),
            MemoryFrame("p2", 1, load_time=15, last_used_time=20), # empate no tempo. page 1 ganha de page 2
            MemoryFrame("p1", 8, load_time=5,  last_used_time=20), # empate no tempo. "p1" ganha de "p2"
        ]

        victim = LRUPageReplacement().select_victim(
            frames,
            Process.create(0, "p4", 1, 1),
            page_id=1,
            current_time=40,
            config=SimulationConfig.create("alternanciaCircular", 1),
        )

        # como todos tem last_used_time = 20, o desempate cai para o owner_pid (p1 ganha de p2).
        self.assertEqual(victim.owner_pid, "p1")
        self.assertEqual(victim.page_id, 8)

class MemoryLRUTest(unittest.TestCase):
    def test_global_lru_replaces_least_recently_used_frame(self) -> None:
        config = SimulationConfig.create(
            algorithm="alternanciaCircular",
            cpu_fraction=1,
            memory_policy="global",
            main_memory_size=2,
            page_frame_size=1,
            allocation_percentage=100,
        )
        memory = Memory(config, LRUPageReplacement())
        process = Process.create(
            creation_time=0,
            pid="p1",
            total_time=1,
            priority_or_tickets=1,
            memory_amount=3,
            page_frame_size=1,
        )

        memory.access_page(process, page_id=1, current_time=1)
        memory.access_page(process, page_id=2, current_time=2)
        memory.access_page(process, page_id=1, current_time=3)
        memory.access_page(process, page_id=3, current_time=4)

        loaded_pages = sorted(frame.page_id for frame in memory.frames)
        self.assertEqual(loaded_pages, [1, 3])
        self.assertEqual(memory.exchange_count, 1)

    def test_local_lru_replaces_only_process_owned_frame(self) -> None:
        config = SimulationConfig.create(
            algorithm="alternanciaCircular",
            cpu_fraction=1,
            memory_policy="local",
            main_memory_size=4,
            page_frame_size=1,
            allocation_percentage=50,
        )
        memory = Memory(config, LRUPageReplacement())
        process1 = Process.create(
            creation_time=0,
            pid="p1",
            total_time=1,
            priority_or_tickets=1,
            memory_amount=4,
            page_frame_size=1,
        )
        process2 = Process.create(
            creation_time=0,
            pid="p2",
            total_time=1,
            priority_or_tickets=1,
            memory_amount=4,
            page_frame_size=1,
        )

        # processo 1 ocupa 2 frames
        memory.access_page(process1, page_id=1, current_time=1)
        memory.access_page(process1, page_id=2, current_time=2)

        # processo 2 ocupa 1 frame
        memory.access_page(process2, page_id=1, current_time=3)

        # processo 1 rejuvenece a pagina 1
        memory.access_page(process1, page_id=1, current_time=4)

        # processo 1 acessa a nova pagina. estoura o limite local (2) --> deve substituir a pagina 2 
        memory.access_page(process1, page_id=3, current_time=5)

        p1_pages = sorted(frame.page_id for frame in memory.frames if frame.owner_pid == "p1")
        p2_pages = sorted(frame.page_id for frame in memory.frames if frame.owner_pid == "p2")

        # processo 1 deve ficar com [1, 3], diferente do FIFO que ficaria com [2, 3]
        self.assertEqual(p1_pages, [1, 3])

        # processo 2 nao deve ser afetado, pois a politica eh local
        self.assertEqual(p2_pages, [1])
        self.assertEqual(memory.exchange_count, 1)

if __name__ == "__main__":
    unittest.main()