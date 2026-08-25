# Agent Playbook — Recurring Workbook Analysis (Template)

Fill every `⟨placeholder⟩` for your workbook. Items marked EXAMPLE show the
shape with invented values.

## Goal

Given the recurring workbook (`.xlsx`, re-issued ⟨weekly⟩), produce the
standard verified report pack — concentration analyses, recurrence
analyses, remaining-work and upgrade-tier views, and a values-only extract
workbook — with every number verified before publishing.

## Inputs

- `workbook_path` — the current period's .xlsx
- `prior_store_path` (optional) — previous period's normalized SQLite
  store, for period-over-period deltas
- `snapshot_date` — the workbook's refresh date; stamp it on every output

## Environment constraints

- Runs entirely in the approved environment; the workbook and derived data
  never leave it.
- **Read-only on the master workbook.** All outputs are new files; any
  extraction experiment operates on a COPY.
- Python (pandas/openpyxl) reads the visible sheets. If the workbook has a
  Power Pivot Data Model, Python CANNOT read it directly — three routes:
  1. Ask the workbook owner to "Load To" the model tables into worksheets
     (best: permanent, zero engineering).
  2. Self-serve on a copy: Queries & Connections → right-click query →
     Load To → Table on a new worksheet (~2 min per period).
  3. Reconstruct derived model tables from visible sheets when the
     derivation is known — and validate against the dashboard's cached
     cell values, which openpyxl CAN read.
  Never parse the embedded model binary (VertiPaq) for published numbers.

## Operating model — Explore → Verify → Report → Converse

- **Phase A (Explore):** map the workbook first; produce an exploration
  brief BEFORE computing anything.
- **Phase B (Verify & compute):** run the standard pack only on a schema
  that passed exploration.
- **Phase C (Report):** lead with the headlines a human analyst would,
  then the tables.
- **Phase D (Converse):** stay in session for multi-turn drill-downs.

Exploration discovers STRUCTURE; the playbook supplies MEANING. The data
semantics below are not discoverable by inspection — never override them
based on what exploration "suggests"; raise a question instead.

## Phase A — Explore & map (fail loudly, never guess)

**Exploration is COMPUTED, never described.** All exploration is executed
code (pandas); the brief quotes raw outputs. Required brief structure:
1. Sheet inventory: name, row count, column count — as computed
2. Per sheet: exact header list; per column a dtype and 3–5
   `value_counts` samples — as computed
3. Diff vs `expected_schema.md`: missing / renamed / NEW items
4. "New/unknown" section: anything unexpected, WITH sample values and
   WITHOUT assigned meaning — interpretation goes to humans
5. Mechanically observed anomalies (blank key fields, target < current
   version, etc.) — listed, not resolved

First-run calibration: run exploration twice; the briefs must be
identical. A human grades the first brief against the known schema map.

If any expected sheet or key column is missing/renamed: STOP, report the
drift as a diff, and wait. Recurring workbooks drift; silent adaptation is
forbidden.

## Step 2 — Normalize to SQLite

One table per source sheet, plus derived fields, e.g.:
- `entity_id` = ⟨primary id column⟩ with fallback to ⟨secondary id⟩
  (rows with neither: keep, flag NULL)
- `base_component` = ⟨component column⟩ with version suffix stripped
- `is_resolved` = (⟨resolution column⟩ == ⟨resolved value⟩)

## Step 3 — Data semantics (memorize; every output respects these)

Template — replace with YOUR workbook's truths, confirmed by the data
owner, not inferred:
1. What one row represents, per sheet (EXAMPLE: findings sheet — one row =
   one finding; dependency sheet — one row = a container that expands by a
   per-row count). Label which level every figure uses.
2. Whether the dashboard counts a different level than the sheets
  (EXAMPLE: dashboard counts occurrences at ~11× the distinct-ID count).
  Never mix levels without labels.
3. Which measures are cumulative vs point-in-time (EXAMPLE: "Complete" is
   all-time cumulative and can exceed "Open" — normal, not an error).
4. What classification fields actually mean (EXAMPLE: severity classes
   that are really remediation-SLA clocks of ⟨X/Y/Z days⟩).
5. Which statuses are excluded from which counts (EXAMPLE: false
   positives excluded from open/complete, reported separately).
6. Known denominator quirks (EXAMPLE: ~⟨k⟩ records lack an entity id, so
   groupings by different keys differ slightly — report denominators).

## Step 4 — Standard analysis pack

Every table: exact headers, sorted descending, TOTAL row labeled with its
full population ("TOTAL — all ⟨N⟩ ⟨entities⟩"). Typical pack:
1. Entity concentration (top 50 + TOTAL) with top-5/10/20 cumulative shares
2. Category concentration (top 30 + TOTAL)
3. Entity × category pairs (top 50 + TOTAL) — the recurrence evidence
4. Remaining-work rollup: total / resolved / remaining per component
5. Upgrade/action typing over ALL components with remaining work:
   jump_type = harmonize / MAJOR / minor / patch / review (formula-based,
   with a review bucket for anything unparseable) + a tier summary
6. Recurrence-in-time (reopened/recurring items) pairs
7. Exception concentrations (disputed/false-positive analog), by category
   and by entity
8. Aging vs the SLA clocks from semantics rule 4

## Step 5 — Verification suite (ALL must pass before any output)

Internal identities every period, e.g.:
- total − resolved = remaining on every rollup row; column sums reconcile
- Pair subtotals + "all others" = category totals exactly
- Tier sums = total remaining
- Alternate-key denominators differ only by the known quirk; report gap
- Every TOTAL row ≥ sum of its visible top-N rows

**Acceptance baseline (first run only):** must reproduce the hand-verified
numbers in `acceptance_baseline.md` exactly. Later periods: values drift;
identities must still hold.

## Step 6 — Outputs

1. `readout_<snapshot>.md` — headlines, tables with cumulative %,
   period-over-period deltas (totals + top movers)
2. `ranked_view_<snapshot>.md` — action tiers + headlines
3. `extracts_<snapshot>.xlsx` — values-only tabs + a README first tab
   carrying the reading notes (counting levels, interpretation cautions,
   denominator quirks, cumulative-measure note). No formulas, no links.
4. `run_log.md` — row counts, drift notes, verification results, anything
   truncated (no silent caps)

## Guardrails

- Never modify the master workbook. Never emit raw row-level data —
  aggregates, top-N + TOTAL only.
- Every number comes from an executed query; nothing estimated or filled
  in by the model. If it cannot be computed, say so.
- Schema drift, failed identity, or missed acceptance value → publish
  nothing; report the failure.
- Keep entity/component naming exactly as in source, stable across
  periods.

## Deployment (Devin-style agents) — sessions vs ask mode

- Periodic run (Phases A–C): a Session with this playbook attached, on a
  machine snapshot with Python deps preinstalled; workbook COPY uploaded
  at session start; the session persists the SQLite store + report pack
  as artifacts.
- The Step 3 semantics + guardrails ALSO live in the agent's persistent
  Knowledge so every session and every ask inherits them.
- Drill-downs needing computation → sessions (same-day window, or a short
  Q&A session that mounts the persisted store). Questions answerable from
  published outputs → ask mode. Rule: needs a query → session; already in
  the report or Knowledge → ask.

## Phase D — Multi-turn analysis session

Each answer = generated read-only SQL against the store, EXECUTED, returned
as table + one paragraph + the SQL used.
- Carry context across turns ("show only the major ones" filters the
  previous result).
- End each answer with 1–2 suggested drill-downs.
- Always state the counting level. Refuse raw row-level dumps; offer
  aggregates. Unknown column semantics → route to humans, never guess.
- Log every question + query + result summary; the log ships with the run.
