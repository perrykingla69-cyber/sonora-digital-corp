from functools import lru_cache

from ..core.settings import get_settings
from packages.memory.mystic_memory import MemoryService


@lru_cache(maxsize=1)
def get_memory_service() -> MemoryService:
    settings = get_settings()
    return MemoryService(data_dir=settings.memory_data_dir)
