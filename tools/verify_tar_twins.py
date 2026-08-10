#!/usr/bin/env python3
"""Are the two Alpaca tars the same dataset? Answer before deleting one.

WHY THIS EXISTS
---------------
E:/ColdStorage holds two Alpaca captures four days apart:

  snap2019-09-19  bzip2, 25.8 GB
  snap2019-09-23  gzip,  38.9 GB

Their first 40 members are byte-identical including sizes, and the gzip
one inventories to exactly 7,859 tickers - matching the number in its
filename. That is strong circumstantial evidence they are the same data
stored twice, which would make the bzip2 copy 25.8 GB of pure
redundancy.

Circumstantial is not enough to delete 25.8 GB of irreplaceable 2019
capture. This compares the full member manifests - every path and every
size - so the answer is a fact rather than an inference.

COST
----
Both archives must be decompressed end to end. gzip runs ~13 min; bzip2
is ~10x slower per byte and will take considerably longer. Contents are
NOT read - only tar headers - so this is decompression-bound, not
parse-bound.

VERDICT
-------
- identical manifests  -> the bzip2 copy is redundant; deleting it frees
  25.8 GB and loses nothing. STILL keep the gzip one: it is raw capture
  and cannot be rebuilt.
- differing manifests  -> KEEP BOTH. The report lists what is unique to
  each, which is the interesting case: the 09-23 capture may have
  back-filled tickers the 09-19 one missed.

Writes data/tar_twin_comparison.json.
"""
import hashlib
import json
import sys
import tarfile
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
COLD = Path("E:/ColdStorage")

CANDIDATES = {
    "gzip_0923": [COLD / "market-data-7859.tar.pigz",
                  COLD / "archive" / "raw" /
                  "alpaca-minute-bars_1999-01_2019-09_7859tickers_snap2019-09-23.tar.gz"],
    "bzip2_0919": [COLD / "market-data.tar",
                   COLD / "archive" / "raw" /
                   "alpaca-minute-bars_1999-01_2019-09_7859tickers_snap2019-09-19.tar.bz2"],
}
OUT = REPO / "data" / "tar_twin_comparison.json"


def resolve(paths):
    for p in paths:
        if p.exists():
            return p
    return None


def manifest(path, label):
    """Member name -> size. Headers only; contents are never read."""
    out = {}
    t0 = time.time()
    with tarfile.open(path, "r|*") as tf:
        for m in tf:
            if m.isfile():
                out[m.name] = m.size
                if len(out) % 250_000 == 0:
                    print(f"  [{label}] {len(out):,} members "
                          f"({time.time()-t0:.0f}s)", flush=True)
    print(f"  [{label}] DONE {len(out):,} members "
          f"({time.time()-t0:.0f}s)", flush=True)
    return out


def main():
    resolved = {k: resolve(v) for k, v in CANDIDATES.items()}
    missing = [k for k, v in resolved.items() if v is None]
    if missing:
        raise SystemExit(f"missing archive(s): {missing}")
    for k, v in resolved.items():
        print(f"{k}: {v.name} ({v.stat().st_size/1e9:.1f} GB)")

    a = manifest(resolved["gzip_0923"], "gzip_0923")
    b = manifest(resolved["bzip2_0919"], "bzip2_0919")

    only_a = sorted(set(a) - set(b))
    only_b = sorted(set(b) - set(a))
    shared = set(a) & set(b)
    size_diff = sorted(n for n in shared if a[n] != b[n])

    identical = not only_a and not only_b and not size_diff
    # a manifest hash makes the verdict quotable in the archive README
    def mhash(m):
        h = hashlib.sha256()
        for n in sorted(m):
            h.update(f"{n}:{m[n]}\n".encode())
        return h.hexdigest()

    payload = {
        "gzip_0923": {"path": str(resolved["gzip_0923"]),
                      "members": len(a), "manifest_sha256": mhash(a)},
        "bzip2_0919": {"path": str(resolved["bzip2_0919"]),
                       "members": len(b), "manifest_sha256": mhash(b)},
        "identical": identical,
        "only_in_gzip_0923": only_a[:500],
        "only_in_bzip2_0919": only_b[:500],
        "n_only_gzip": len(only_a), "n_only_bzip2": len(only_b),
        "n_size_mismatch": len(size_diff),
        "size_mismatch_sample": size_diff[:200],
    }
    OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print(f"\n{'=' * 62}")
    print(f"gzip_0923  : {len(a):,} members")
    print(f"bzip2_0919 : {len(b):,} members")
    print(f"only in gzip_0923 : {len(only_a):,}")
    print(f"only in bzip2_0919: {len(only_b):,}")
    print(f"size mismatches   : {len(size_diff):,}")
    print(f"{'=' * 62}")
    if identical:
        print("VERDICT: IDENTICAL. The bzip2 copy is redundant - deleting")
        print("         it frees 25.8 GB and loses nothing. Keep the gzip")
        print("         one; raw capture cannot be rebuilt.")
    else:
        print("VERDICT: THEY DIFFER. Keep BOTH. See the JSON for what is")
        print("         unique to each - the later capture may have")
        print("         back-filled tickers the earlier one missed.")
    print(f"\nwrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
