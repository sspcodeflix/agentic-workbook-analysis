#!/usr/bin/env python3
"""Leverage model — which fix units close the most open OSS vulnerabilities.

Greedy weighted set-cover over "fix units":
  - repo units     = one dependency-bump PR in that repo (covers all its rows)
  - package units  = one org-wide upgrade campaign (covers that package's rows)
  - mixed (default) = greedy may pick either kind each step

Input: long-format CSV with headers  repo, package, remaining
(one row per repo × package combination, remaining = unremediated count;
a TOTAL row is ignored). Output: the ranked plan and the headline
"fixing these K units closes N of M open rows (X%)".

Usage:
    python3 scripts/leverage_model.py repo_package_remaining.csv [-k 10]
        [--mode mixed|repo|package]
"""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path


def load_atoms(path: Path):
    atoms = []  # (repo, package, remaining)
    with path.open(newline="", encoding="utf-8-sig") as fh:
        for raw in csv.DictReader(fh):
            row = {(k or "").strip().lower(): (v or "").strip() for k, v in raw.items()}
            repo, pkg = row.get("repo", ""), row.get("package", "")
            if not repo or repo.lower() in ("total", "grand total"):
                continue
            value = (row.get("remaining", "0") or "0").replace(",", "")
            n = int(float(value)) if value else 0
            if n > 0:
                atoms.append((repo, pkg, n))
    if not atoms:
        raise SystemExit(f"{path}: no usable rows (need repo, package, remaining)")
    return atoms


def greedy_cover(atoms, k: int, mode: str):
    covered = [False] * len(atoms)
    total = sum(n for _, _, n in atoms)
    by_repo, by_pkg = defaultdict(list), defaultdict(list)
    for i, (repo, pkg, _) in enumerate(atoms):
        by_repo[repo].append(i)
        by_pkg[pkg].append(i)

    units: dict[tuple[str, str], list[int]] = {}
    if mode in ("repo", "mixed"):
        units.update({("repo PR", r): idxs for r, idxs in by_repo.items()})
    if mode in ("package", "mixed"):
        units.update({("package campaign", p): idxs for p, idxs in by_pkg.items()})

    plan, cum = [], 0
    for _ in range(k):
        best, best_gain = None, 0
        for unit, idxs in units.items():
            gain = sum(atoms[i][2] for i in idxs if not covered[i])
            if gain > best_gain:
                best, best_gain = unit, gain
        if best is None:
            break
        for i in units[best]:
            covered[i] = True
        cum += best_gain
        detail = ""
        if best[0] == "repo PR":
            pkgs = {atoms[i][1] for i in units[best]}
            detail = f"{len(pkgs)} packages bundled"
        else:
            repos = {atoms[i][0] for i in units[best]}
            detail = f"{len(repos)} repos touched"
        plan.append((best[0], best[1], best_gain, cum, 100.0 * cum / total, detail))
    return plan, total


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("csv_path", type=Path)
    ap.add_argument("-k", type=int, default=10, help="number of fix units (default 10)")
    ap.add_argument("--mode", choices=("mixed", "repo", "package"), default="mixed")
    args = ap.parse_args()

    atoms = load_atoms(args.csv_path)
    plan, total = greedy_cover(atoms, args.k, args.mode)

    print(f"| # | Fix unit | Target | Closes | Cumulative | Cum. % | Note |")
    print("|---|---|---|---|---|---|---|")
    for rank, (kind, name, gain, cum, pct, detail) in enumerate(plan, 1):
        print(f"| {rank} | {kind} | {name} | {gain:,} | {cum:,} | {pct:.1f}% | {detail} |")

    if plan:
        _, _, _, cum, pct, _ = plan[-1]
        print(f"\nHEADLINE: fixing these {len(plan)} units closes "
              f"{cum:,} of {total:,} open OSS rows ({pct:.1f}%).")


if __name__ == "__main__":
    main()
