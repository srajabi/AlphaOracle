# REPRODUCE — finding → script → output

**Every claim in `findings.md` must be re-derivable.** Finding 25
established that findings.md is not evidence until a test re-derives it;
this file is the index that makes that practical.

Run everything with the repo venv:

```
.venv/Scripts/python.exe tools/<script>.py
```

Bulk data paths resolve through `src/archive_paths.py`. **Never hardcode
`E:/ColdStorage/...`** — the originals were renamed during archival and
hardcoded paths silently broke six tools once already.

---

## Recent findings (41–53) — exact provenance

| finding | script | output | runtime |
|---|---|---|---|
| 41a/41b band width + adaptive bands | `backtest_adaptive_bands.py` | `data/adaptive_band_study.json` | ~3 min |
| **41c** band width on US distribution | `backtest_band_upside_us.py` | `data/band_upside_us.json` | ~2 min |
| 42 breadth as a regime detector | `backtest_breadth_regime.py` | `data/breadth_regime_study.json` | ~1 min |
| 42c breadth as leverage modulator | inline (see `current.md`) | `data/breadth_leverage_study.json` | ~4 min |
| 43 sector rotation, French universe | `backtest_sector_rotation.py` | `data/sector_rotation_study.json` | ~6 min |
| 44 top-N concentration | `backtest_top_n.py` | `data/top_n_study.json` | **~35 min** |
| **45** sector momentum, tradeable ETFs | `backtest_sector_etf_momentum.py` | `data/sector_etf_momentum.json` | ~5 min |
| 46 CAPE | `backtest_cape.py` | `data/cape_study.json` | ~2 min |
| 47 tar inventory | `ingest_coldstorage_tar.py pigz` | `data/coldstorage_inventory.json` | ~13 min |
| 48 cross-source validation | `validate_alpaca_vs_ohlcv.py` | `data/cross_source_validation.json` | ~10 min |
| 49 bzip2 twin comparison | `inventory_bz2_twin.py` | `data/bz2_twin_inventory.json` | **~73 min** |
| 50 masters built | `build_*_master.py` | see §2 | **~3 h** |
| **51** LETF simulator vs reality | `backtest_letf_path.py` | `data/letf_path_study.json` | ~4 min |
| **52** sleeves with honest financing | `backtest_leverage_with_spread.py` | `data/leverage_spread_study.json` | ~3 min |
| **53** stop-losses intraday | `backtest_stoploss_intraday.py` | `data/stoploss_intraday_study.json` | ~6 min |

Bolded rows are the ones a new agent is most likely to need — they carry
the current strategy parameters (41c), the corrections to every
leveraged number (51, 52) and the two rulings that closed TODOs (45, 53).

`data/_tool_index.json` is a generated index of all 46 tools and the
output each declares.

---

## 2. Rebuilding the data masters from raw

Order matters — the daily Alpaca leg derives from the minute master, not
from the tar.

```
.venv/Scripts/python.exe tools/build_minute_master.py        # ~2 h, resumable
.venv/Scripts/python.exe tools/build_daily_master.py ohlcv1m # ~2.4 h, resumable
.venv/Scripts/python.exe tools/build_daily_master.py alpaca  # ~1 h
.venv/Scripts/python.exe tools/build_daily_master.py yfinance
.venv/Scripts/python.exe tools/build_reference_master.py     # ~1 min
.venv/Scripts/python.exe tools/package_archive.py --move --hash
.venv/Scripts/python.exe tools/package_archive.py --verify
```

Both long builds skip work already on disk, so an interrupted run costs
minutes to resume, not hours. Total from scratch ≈ 6 h.

---

## 3. What "reproducible" requires here

1. **State the falsifier in the docstring, before the code.** Every
   tool written since finding 41 opens with what result would kill the
   hypothesis. A test that cannot fail is not a test.
2. **Run the control that shares the structure.** Equal-weight for a
   concentrated portfolio; same-period for a different-universe claim.
   Three promising results died on the control rather than the headline
   (35, 44, 45).
3. **Exclude, do not patch.** Split days are dropped from statistics,
   not repaired — a patched value is a guess, an excluded one is honest.
4. **Non-overlapping windows for any forward-return p-value** (29), or
   Newey-West with the overlap as the lag.
5. **Gate every ETF series at its inception date.** Ticker reuse gave
   UPRO a beta of −12.6 (51e).
6. **Sanity-check magnitudes against the underlying.** A familiar
   strategy printing an unfamiliar number is a bug until proven
   otherwise — this caught two lookahead bugs and one −100% drawdown.

---

## 4. Known gaps in reproducibility

Stated rather than hidden, so nobody assumes coverage that is not there.

- **Findings 1–17 predate this protocol.** They have no tool mapping and
  several were produced by LLM analysis rather than code. Finding 25
  exists precisely because one of them failed to reproduce (finding 3's
  overlay claim came back −34.8% against a claimed −19%). **Treat any
  finding below 18 as unverified until re-derived.**
- **Findings 39 and 40 do not exist.** `findings.md` jumps 38 → 41. Not
  a deletion — they were never written.
- **`data/breadth_leverage_study.json` came from an inline script**, not
  a committed tool. The numbers are in finding 42c; the code is only in
  the session transcript. Re-implement before relying on it.
- **Dividend yields in finding 51 are assumed (SPY 1.6%, QQQ 0.6%), not
  measured.** No `adj_close` exists anywhere in the archive. That is why
  51's financing spread is a range (0.5–1.5%) rather than a point.
- **Finding 53's economic magnitudes are rule-dependent.** The breach
  census (53a) has no re-entry rule and is the defensible part; the CAGR
  table (53b) is direction-only.
- **`tools/verify_tar_twins.py` was written but never run** —
  `inventory_bz2_twin.py` answered the question more cheaply by scanning
  only the bzip2 side against the saved gzip inventory.
- Eight older tools declare no output path; see `data/_tool_index.json`.
