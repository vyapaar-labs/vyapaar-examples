# 0003 — vyapaar-data-nav-loaders

**Status**: open
**Owning repo**: `vyapaar-data` (Python + DuckDB lakehouse: loaders, store, coverage
ledger).

## Symptom
`vyapaar_data` has no installed surface yet: `vx.loaders.{nse, yfinance}`,
`vx.loaders.amfi` NAV ingestion, `store.coverage`, and the lakehouse paths the
screener/sip harness resolve are absent, so the ported consumers keep in-repo shims.

## What stands in
* `vyapaar_examples/amfi.py` — AMFI NAV loader (`nav_bars`, `AmfiNavLoader`, `NavRow`,
  `parse_navall`) with parquet persistence over the mirrored store; the NAV loading
  capability whose store surface (`store.mutual_funds`) the wheel data repo will provide.
* `vyapaar_examples/screening/paths.py` — `VYAAPAAR_DATA_DIR` env seam prepended to the
  catalog / `fundamentals.duckdb` / `mutual_funds.duckdb` discovery lists, and
  `tests/unit/conftest.py` `catalog_dir` / `add_series` / `fund_db` synthetic fixtures
  power it; offline screener/sip tests build their catalog there when no
  `vyapaar-data` checkout exists beside the repo.
* Coverage/interval handling rides the `_kernel.coverage` mirror (gap 0006) until the
  data owning surface exists.
* `vyapaar_examples/bhavcopy.py` — NSE bhavcopy dialect-sniffing CSV parser (UDiFF/Sec-Bhavdata/
  legacy), used by `storage/02_import_nse_bhavcopy.py`.

## How to close
Land `vyapaar-data` with the loaders/store/coverage surface (point-in-time NSE parquet
catalog, `fundamentals.duckdb`, `mutual_funds.duckdb`, NAV ingestion). Then delete
`amfi.py`'s loader duplication and the env/test seam; retarget the D5 `vyapaar_data.*`
imports and drop the conftest synthetic catalog fixtures where the real surface covers CI.
