from __future__ import annotations

from pathlib import Path
from typing import Any


def load_named(
    name: str, strategies_dir: Path | None = None, search_from: Path | None = None
) -> Any:
    """Load a named catalog strategy (find_catalog/load_catalog in vyapaar-strategies loader)."""
    from vyapaar_examples._kernel.loader import find_catalog, load_catalog_strategy

    catalog_path = find_catalog(strategies_dir, search_from=search_from)
    return load_catalog_strategy(name, catalog_path)


def strategies_catalog_dir() -> Path:
    """The vyapaar-strategies checkout: ``$VYAAPAAR_STRATEGIES_DIR``, else the sibling checkout.

    Raises ``vyapaar.strategies.loader.CatalogError`` saying how to point at one when absent.
    """
    from vyapaar_examples._kernel.loader import find_catalog

    return find_catalog(search_from=Path(__file__))


def load_catalog_tool(module: str) -> Any:
    """Import ``tools.<module>`` from the vyapaar-strategies catalog (e.g. ``validate_chain``).

    The catalog's ``tools`` package is imported by path with ``sys.path`` and ``sys.modules``
    restored afterwards, so it cannot shadow or be shadowed by another ``tools`` package.
    """
    import importlib
    import sys

    root = str(strategies_catalog_dir())
    saved = {k: sys.modules.pop(k) for k in list(sys.modules) if k.split(".")[0] == "tools"}
    sys.path.insert(0, root)
    try:
        loaded = importlib.import_module(f"tools.{module}")
        for k in [k for k in sys.modules if k.split(".")[0] == "tools"]:
            del sys.modules[k]
    finally:
        sys.path.remove(root)
        sys.modules.update(saved)
    return loaded
