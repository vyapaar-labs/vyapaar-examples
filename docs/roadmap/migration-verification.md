# `vyapaar-examples` — Migration Verification Milestone

Verification commands for the `honba-examples → vyapaar-examples` migration:

```bash
cd /home/pmallapp/Devel/Finance/vyapaar-labs/vyapaar-examples
pytest -q
ruff check .
ruff format --check .
mypy vyapaar_examples
```

## Migration Milestone Status

| Milestone | Status |
|-----------|--------|
| `pyproject.toml` fixed | Complete |
| Entry journey (`examples/01`–`15`) | Complete |
| Staged port Stages 0–8 (all 94 topic scripts) | Complete |
| Shared harness modules (`vyapaar_examples/`) | Complete |
| Test suite (137 test modules) | Complete |
| Gaps 0001–0008 documented | Complete |
| `pytest -q` (922 passed, 70 skipped, 0 failures) | Passing |
| `ruff check .` | Clean |
| `ruff format --check .` | Clean |
| `mypy vyapaar_examples` | Clean |
| `make check` | Green |
| Zero `honba` identifiers across repo | Complete |
