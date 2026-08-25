#!/usr/bin/env python3
"""Generate the weekly Concentration Readout from workbook summary extracts.

Usage:
    python3 scripts/generate_readout.py data/<week-folder> [--prev data/<older-week>]

If --prev is omitted, the previous sibling folder (sorted by name) is used
automatically when one exists, so ISO-week folder names (2026-W34, 2026-W35, ...)
give week-over-week deltas for free.

Expected files in the week folder (any subset; a missing file just skips its
section):
    app_concentration.csv   columns: app_id, open [, complete, false_positive, ...]
    cwe_concentration.csv   columns: cwe, open
    oss_packages.csv        columns: package, findings [, distinct_apps, distinct_cves]

Values may contain thousands separators. A row labeled TOTAL / GRAND TOTAL is
used as the authoritative total when present; a row labeled "others" /
"all others" is treated as the rolled-up remainder from the pivot.

Output: reports/<week-folder-name>-readout.md
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
from pathlib import Path

INSTANCE_DASHBOARD_NOTE = (
    "Counting basis: **unique records** (visible sheet rows). A workbook "
    "dashboard may separately count *instances/occurrences* (one per "
    "affected asset); state both levels explicitly and never mix them "
    "without labels."
)


NULL_TOKENS = {"", "-", "–", "—", "n/a", "na", "none"}
OTHERS_LABELS = {"other", "others", "all other", "all others", "remainder"}


def parse_num(value: str) -> int:
    value = (value or "").strip().replace(",", "").replace(" ", "")
    if value.lower() in NULL_TOKENS:
        return 0
    try:
        return int(float(value))
    except ValueError:
        raise SystemExit(f"cannot parse count value {value!r}") from None


def load_extract(path: Path, key_field_candidates: list[str], value_field: str):
    """Return (named_rows, others_value, total_value_or_None, extra_columns)."""
    with path.open(newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        fields = [f.strip().lower() for f in reader.fieldnames or []]
        rows = []
        for raw in reader:
            rows.append({(k or "").strip().lower(): (v or "").strip() for k, v in raw.items()})

    key_field = next((k for k in key_field_candidates if k in fields), None)
    if key_field is None or value_field not in fields:
        raise SystemExit(
            f"{path.name}: need a key column ({'/'.join(key_field_candidates)}) "
            f"and a '{value_field}' column; found {fields}"
        )

    named, others, total = [], 0, None
    extra_cols = [f for f in fields if f not in (key_field, value_field)]
    for row in rows:
        label = row[key_field]
        low = label.lower()
        value = parse_num(row.get(value_field, "0"))
        if low in ("total", "grand total"):
            total = value
        elif low in OTHERS_LABELS:
            others += value
        elif label:
            named.append((label, value, {c: row.get(c, "") for c in extra_cols}))

    named.sort(key=lambda item: item[1], reverse=True)
    return named, others, total, extra_cols


def concentration(named, others, total):
    """Compute total and cumulative top-N shares."""
    named_sum = sum(v for _, v, _ in named)
    grand = total if total is not None else named_sum + others
    shares = {}
    for n in (5, 10, 20):
        top = sum(v for _, v, _ in named[:n])
        shares[n] = (top, (100.0 * top / grand) if grand else 0.0)
    return grand, shares


def fmt(n: int) -> str:
    return f"{n:,}"


def fmt_extra(text: str) -> str:
    cleaned = text.replace(",", "").replace(" ", "")
    try:
        return fmt(int(float(cleaned)))
    except ValueError:
        return text


def md_table(header: list[str], rows: list[list[str]]) -> str:
    out = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    out += ["| " + " | ".join(r) + " |" for r in rows]
    return "\n".join(out)


def section(title, named, others, total, value_name, extra_cols=(), top=10):
    grand, shares = concentration(named, others, total)
    lines = [f"## {title}", ""]
    lines.append(
        f"Top 5 hold **{shares[5][1]:.1f}%**, top 10 hold **{shares[10][1]:.1f}%**, "
        f"top 20 hold **{shares[20][1]:.1f}%** of {fmt(grand)} {value_name}."
    )
    lines.append("")
    header = ["#", "Name", value_name.title(), "Cum. %"] + [c.replace("_", " ").title() for c in extra_cols]
    rows, running = [], 0
    for idx, (label, value, extras) in enumerate(named[:top], start=1):
        running += value
        rows.append(
            [str(idx), label, fmt(value), f"{100.0 * running / grand:.1f}%"]
            + [fmt_extra(extras.get(c, "")) for c in extra_cols]
        )
    remainder = grand - running
    if remainder > 0:
        rows.append(["", f"All others ({max(len(named) - top, 0)}+ named)", fmt(remainder), "100.0%"]
                    + ["" for _ in extra_cols])
    lines.append(md_table(header, rows))
    lines.append("")
    return "\n".join(lines), grand, shares


def delta_section(title, current, previous, value_name, movers=5):
    cur_named, cur_others, cur_total = current
    prev_named, prev_others, prev_total = previous
    cur = {label: value for label, value, _ in cur_named}
    prev = {label: value for label, value, _ in prev_named}
    cur_grand = cur_total if cur_total is not None else sum(cur.values()) + cur_others
    prev_grand = prev_total if prev_total is not None else sum(prev.values()) + prev_others
    diff = cur_grand - prev_grand
    if diff == 0:
        movement = "no change"
    else:
        movement = f"{'down' if diff < 0 else 'up'} {fmt(abs(diff))}"
    lines = [f"### {title}: {fmt(prev_grand)} → {fmt(cur_grand)} ({movement})"]
    changes = []
    for label in set(cur) | set(prev):
        d = cur.get(label, 0) - prev.get(label, 0)
        if d:
            changes.append((label, d))
    changes.sort(key=lambda item: abs(item[1]), reverse=True)
    for label, d in changes[:movers]:
        sign = "+" if d > 0 else ""
        lines.append(f"- {label}: {sign}{fmt(d)} {value_name}")
    if not changes:
        lines.append("- no movement among named rows")
    residual = diff - (sum(cur.values()) - sum(prev.values()))
    if residual:
        sign = "+" if residual > 0 else ""
        lines.append(f"- rolled-up 'all others' remainder: {sign}{fmt(residual)} {value_name}")
    lines.append("")
    return "\n".join(lines)


SPECS = [
    ("app_concentration.csv", "Application concentration",
     ["app_id", "app id", "app", "application id", "application"], "open", "open findings"),
    ("cwe_concentration.csv", "Weakness (CWE) concentration",
     ["cwe"], "open", "open findings"),
    ("oss_packages.csv", "Open-source package concentration",
     ["package"], "findings", "findings"),
    ("oss_remaining.csv", "OSS remaining load (unremediated, by base package)",
     ["package", "base_package"], "remaining", "remaining findings"),
    ("spring_rollup.csv", "Framework (Spring/Spring Boot) concentration",
     ["item", "framework", "component"], "findings", "findings"),
    ("fp_by_cwe.csv", "False positives by CWE",
     ["cwe"], "fp", "false positives"),
    ("fp_by_app.csv", "False positives by application",
     ["app_id", "app id", "app"], "fp", "false positives"),
]


def load_pairs(path: Path, value_field: str = "open"):
    """App × CWE pair files: app_id, cwe, <value> → named rows 'APP · CWE'."""
    with path.open(newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        rows = [{(k or "").strip().lower(): (v or "").strip() for k, v in raw.items()}
                for raw in reader]
    named, others, total = [], 0, None
    for row in rows:
        app = row.get("app_id", "")
        low = app.lower()
        value = parse_num(row.get(value_field, "0"))
        if low in ("total", "grand total"):
            total = value
        elif low in OTHERS_LABELS:
            others += value
        elif app:
            named.append((f"{app} · {row.get('cwe', '')}", value, {}))
    named.sort(key=lambda item: item[1], reverse=True)
    return named, others, total


def recurrence_rollup(named, min_apps=2):
    """Group visible pairs by CWE → the 'same weakness across many apps' evidence."""
    by_cwe: dict[str, list[tuple[str, int]]] = {}
    for label, value, _ in named:
        app, _, cwe = label.partition(" · ")
        by_cwe.setdefault(cwe, []).append((app, value))
    hits = [(cwe, apps) for cwe, apps in by_cwe.items() if len(apps) >= min_apps]
    hits.sort(key=lambda item: (len(item[1]), sum(v for _, v in item[1])), reverse=True)
    lines = ["### Same weakness, many applications (from the top pairs)", ""]
    for cwe, apps in hits[:5]:
        apps_txt = ", ".join(f"{a} {fmt(v)}" for a, v in apps)
        lines.append(f"- **{cwe}** in {len(apps)} apps: {apps_txt} "
                     f"(subtotal {fmt(sum(v for _, v in apps))})")
    lines.append("")
    return "\n".join(lines) if hits else ""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("week_folder", type=Path)
    parser.add_argument("--prev", type=Path, default=None,
                        help="previous week folder for deltas (default: previous sibling)")
    parser.add_argument("--out-dir", type=Path, default=Path("reports"))
    args = parser.parse_args()

    week = args.week_folder
    if not week.is_dir():
        raise SystemExit(f"not a folder: {week}")

    prev = args.prev
    if prev is None:
        siblings = sorted((p for p in week.parent.iterdir() if p.is_dir()),
                          key=lambda p: p.name)
        names = [p.name for p in siblings]
        idx = names.index(week.name) if week.name in names else -1
        prev = siblings[idx - 1] if idx > 0 else None

    label = week.name
    body = [
        f"# Concentration Readout — {label}",
        "",
        f"_Generated {dt.date.today().isoformat()} from summary extracts (no raw data)._",
        "",
        INSTANCE_DASHBOARD_NOTE,
        "",
    ]
    headline_bits = []
    deltas = []

    for filename, title, key_candidates, value_field, value_name in SPECS:
        path = week / filename
        if not path.exists():
            body.append(f"## {title}\n\n_(extract `{filename}` not provided this week)_\n")
            continue
        named, others, total, extra_cols = load_extract(path, key_candidates, value_field)
        text, grand, shares = section(title, named, others, total, value_name, extra_cols)
        body.append(text)
        headline_bits.append(f"{title.split(' ')[0]}: top 10 = {shares[10][1]:.0f}% of {fmt(grand)}")

        if prev and (prev / filename).exists():
            prev_named, prev_others, prev_total, _ = load_extract(prev / filename, key_candidates, value_field)
            deltas.append(delta_section(title, (named, others, total),
                                        (prev_named, prev_others, prev_total), value_name))

    pairs_path = week / "app_cwe_pairs.csv"
    if pairs_path.exists():
        p_named, p_others, p_total = load_pairs(pairs_path)
        text, grand, shares = section("Repeat-weakness pairs (Application × CWE)",
                                      p_named, p_others, p_total, "open findings", (), top=15)
        body.append(text)
        rollup = recurrence_rollup(p_named)
        if rollup:
            body.append(rollup)
        headline_bits.append(f"Pairs: top 10 = {shares[10][1]:.0f}% of {fmt(grand)}")
        if prev and (prev / "app_cwe_pairs.csv").exists():
            pp_named, pp_others, pp_total = load_pairs(prev / "app_cwe_pairs.csv")
            deltas.append(delta_section("Repeat-weakness pairs",
                                        (p_named, p_others, p_total),
                                        (pp_named, pp_others, pp_total), "open findings"))

    reopened_path = week / "reopened_pairs.csv"
    if reopened_path.exists():
        r_named, r_others, r_total = load_pairs(reopened_path, value_field="reopened")
        text, grand, _ = section("Reopened recurrence (closed, then back again)",
                                 r_named, r_others, r_total, "reopened findings", (), top=15)
        body.append(text)
        rollup = recurrence_rollup(r_named)
        if rollup:
            body.append(rollup)
        headline_bits.append(f"Reopened: {fmt(grand)}")

    if deltas:
        body.append(f"## Week-over-week (vs {prev.name})\n")
        body.extend(deltas)

    if headline_bits:
        body.insert(4, "**Headline:** " + " · ".join(headline_bits) + "\n")

    args.out_dir.mkdir(parents=True, exist_ok=True)
    out_path = args.out_dir / f"{label}-readout.md"
    out_path.write_text("\n".join(body), encoding="utf-8")
    print(f"wrote {out_path}")
    for bit in headline_bits:
        print("  ", bit)


if __name__ == "__main__":
    main()
