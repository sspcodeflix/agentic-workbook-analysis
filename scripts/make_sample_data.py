#!/usr/bin/env python3
"""Create SYNTHETIC demo extracts in data/sample-W1 and data/sample-W2.

Purely fake numbers with realistic Pareto-ish shapes, used only to prove the
readout pipeline end to end. Entities keep stable IDs across the two weeks
(as real App IDs / packages do); week 2 applies small closures and drift.
Real extracts replace these under data/<ISO-week>/.
"""

from __future__ import annotations

import csv
import random
from pathlib import Path

random.seed(34)

PACKAGES = [
    "openssl", "log4j-core", "spring-core", "jackson-databind", "commons-text",
    "netty-handler", "tomcat-embed-core", "guava", "snakeyaml", "xstream",
    "bouncycastle", "struts2-core", "commons-collections", "httpclient",
    "protobuf-java", "gson", "okhttp", "poi-ooxml", "activemq-client", "junit",
] + [f"lib-{i:02d}" for i in range(30)]

CWES = [
    "CWE-89", "CWE-79", "CWE-287", "CWE-22", "CWE-200", "CWE-352", "CWE-434",
    "CWE-611", "CWE-502", "CWE-798", "CWE-306", "CWE-862", "CWE-918", "CWE-94",
    "CWE-77", "CWE-119", "CWE-125", "CWE-476", "CWE-190", "CWE-362", "CWE-922",
    "CWE-521", "CWE-256", "CWE-312", "CWE-327", "CWE-330", "CWE-400", "CWE-601",
    "CWE-732", "CWE-1104",
]


def zipf_counts(n_items: int, exponent: float, total: int) -> list[int]:
    weights = [1.0 / (rank ** exponent) for rank in range(1, n_items + 1)]
    scale = total / sum(weights)
    return [max(1, int(w * scale)) for w in weights]


def write_csv(path: Path, header: list[str], rows: list[list], total_col: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = sorted(rows, key=lambda r: r[1], reverse=True)
    total_row = ["TOTAL"] + ["" for _ in header[1:]]
    total_row[1] = sum(r[1] for r in rows)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(header)
        writer.writerows(rows)
        writer.writerow(total_row)
    _ = total_col  # kept for signature clarity


def next_week(value: int) -> int:
    """Week 2 = week 1 minus some closures, plus a few new findings."""
    closed = int(value * random.uniform(0.0, 0.08))
    new = int(value * random.uniform(0.0, 0.03))
    return max(0, value - closed + new)


def main() -> None:
    base = Path(__file__).resolve().parent.parent / "data"

    # --- Week 1 (stable entity → count assignments) ---
    apps = [f"APP-{i:03d}" for i in range(1, 211)]
    random.shuffle(apps)  # which app is rank 1 is random, but fixed for both weeks
    app_open = dict(zip(apps, zipf_counts(210, 1.05, 55_000)))
    app_complete = {a: int(v * random.uniform(0.4, 1.3)) for a, v in app_open.items()}

    cwe_open = dict(zip(CWES, zipf_counts(len(CWES), 1.3, 55_000)))

    pkg_findings = dict(zip(PACKAGES, zipf_counts(len(PACKAGES), 1.2, 30_000)))
    pkg_apps = {p: min(210, max(1, int(3 + c ** 0.5 * random.uniform(0.6, 1.1))))
                for p, c in pkg_findings.items()}
    pkg_cves = {p: max(1, int(c ** 0.4 * random.uniform(0.5, 1.2)))
                for p, c in pkg_findings.items()}

    w1 = base / "sample-W1"
    write_csv(w1 / "app_concentration.csv", ["app_id", "open", "complete"],
              [[a, v, app_complete[a]] for a, v in app_open.items()], 1)
    write_csv(w1 / "cwe_concentration.csv", ["cwe", "open"],
              [[c, v] for c, v in cwe_open.items()], 1)
    write_csv(w1 / "oss_packages.csv",
              ["package", "findings", "distinct_apps", "distinct_cves"],
              [[p, v, pkg_apps[p], pkg_cves[p]] for p, v in pkg_findings.items()], 1)

    # --- Week 2 = week 1 with closures/drift, same entity IDs ---
    w2 = base / "sample-W2"
    write_csv(w2 / "app_concentration.csv", ["app_id", "open", "complete"],
              [[a, next_week(v), app_complete[a] + int(v * 0.03)] for a, v in app_open.items()], 1)
    write_csv(w2 / "cwe_concentration.csv", ["cwe", "open"],
              [[c, next_week(v)] for c, v in cwe_open.items()], 1)
    write_csv(w2 / "oss_packages.csv",
              ["package", "findings", "distinct_apps", "distinct_cves"],
              [[p, next_week(v), pkg_apps[p], pkg_cves[p]] for p, v in pkg_findings.items()], 1)

    print("wrote data/sample-W1 and data/sample-W2 (SYNTHETIC demo data)")


if __name__ == "__main__":
    main()
