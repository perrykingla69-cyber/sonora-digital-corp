from functools import lru_cache

from packages.memory.mystic_memory import MemoryService


@lru_cache(maxsize=1)
def get_memory_service() -> MemoryService:
    return MemoryService()
