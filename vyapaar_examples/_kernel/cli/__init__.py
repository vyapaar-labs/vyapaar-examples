# mirror: kernel-verbatim port (gap 0004: wheel display/client surface)

from __future__ import annotations

from vyapaar_examples._kernel.store import ParquetBarStore

__all__ = ["_STORE", "get_store"]

_STORE = ParquetBarStore()


def get_store() -> ParquetBarStore:
    """Get the global data store instance."""
    return _STORE
