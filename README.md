# Agentic Workbook Analysis — Playbook Template

A battle-tested template for having an AI agent (Devin, Copilot, or any
code-executing assistant) **reliably** analyze a recurring Excel workbook
and publish verified reports — without the agent ever inventing a number.

Distilled from a real production deployment (a weekly enterprise
vulnerability workbook, ~600K records, 10 sheets, hidden Power Pivot data
model). All organization-specific names and values have been replaced with
`⟨placeholders⟩` or clearly marked EXAMPLEs — fill them in for your own
workbook.

## The method in one paragraph

The agent works in four phases — **Explore → Verify → Report → Converse** —
under one dividing rule: *exploration discovers structure; the playbook
supplies meaning; arithmetic decides every published number.* Exploration
is computed (executed code, quoted raw outputs), never described from
perception. Nothing publishes until a verification suite of internal
identities passes, and the very first run must reproduce a hand-verified
**acceptance baseline** exactly.

## Contents

| File | Purpose |
|---|---|
| `playbook.md` | The agent playbook: phases, procedure, guardrails, acceptance test |
| `knowledge-entries.md` | Template "Knowledge" entries: data semantics + reporting guardrails |
| `expected_schema.md` | The schema contract exploration diffs against |
| `acceptance_baseline.md` | How (and why) to build a hand-verified baseline |
| `scripts/generate_readout.py` | Extract-CSVs → markdown report generator with week-over-week deltas |
| `scripts/make_sample_data.py` | Synthetic data generator — run the pipeline end-to-end with zero real data |

## Try it

```bash
python3 scripts/make_sample_data.py          # writes data/sample-W1, data/sample-W2
python3 scripts/generate_readout.py data/sample-W2
# → reports/sample-W2-readout.md (with deltas vs sample-W1)
```

## Hard-won design rules baked in

1. **Computed exploration** — the agent maps the workbook via executed
   pandas, quotes raw outputs, and diffs against the schema contract; new
   columns are findings to report, never obstacles to route around.
2. **Semantics are supplied, not inferred** — the truths that aren't
   discoverable by inspection (what a status means, what one row
   represents, which fields are cumulative) live in a semantics list the
   agent must not override.
3. **Two counting levels, always labeled** — source rows vs expanded
   occurrences; mixing them unlabeled is the #1 way dashboards and
   analyses "contradict" each other.
4. **Acceptance baseline** — hand-verify one snapshot's numbers, then make
   reproducing them the agent's entry exam.
5. **Publish nothing on failure** — schema drift or a failed identity
   stops the run; a loud halt beats a silently wrong report.
6. **Values-only outputs** — published extracts carry no formulas or
   external links, TOTAL rows labeled with their full population, and a
   README tab of reading notes that travels with the file.

## License

MIT — use it, adapt it.
