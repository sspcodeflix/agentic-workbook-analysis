# Expected Schema — Template

The contract exploration (Phase A) diffs against. Reference row counts are
from your baseline snapshot — they drift each period; sheet and column
NAMES should not. Missing/renamed → STOP. New → report, don't interpret.

## Sheets (EXAMPLE shape — replace with yours)

| Sheet | ~Rows at baseline | Role |
|---|---|---|
| Summary | ⟨n⟩ | Dashboard (model-backed pivots; cached values readable) |
| ⟨Findings⟩ | ⟨n⟩ | One row = one finding (unique id) |
| ⟨Dependencies⟩ | ⟨n⟩ | One row = a container (per-row count expands) |
| ⟨Framework⟩ | ⟨n⟩ | Component findings |
| ⟨…⟩ | ⟨n⟩ | ⟨…⟩ |

Hidden data-model queries (not readable as sheets): ⟨list them⟩ — see the
playbook's three extraction routes.

## Must-exist columns

### ⟨Findings sheet⟩
- ⟨unique id⟩, ⟨primary entity id⟩, ⟨secondary entity id⟩
- ⟨category⟩, ⟨status⟩, ⟨severity/SLA class⟩
- ⟨reopened indicator⟩, ⟨remediation/date fields⟩

### ⟨Dependencies sheet⟩
- ⟨wave/campaign⟩, ⟨entity id⟩, ⟨component⟩, ⟨current version⟩,
  ⟨target version(s)⟩, ⟨resolved flag⟩, ⟨per-row count — confirm with
  data owner⟩, ⟨feasibility flags⟩, ⟨due date⟩

## Known quirks (expected; do not "fix")

Record every quirk you confirm, e.g.:
- ~⟨k⟩ records lack an entity id under the fallback rule
- Some components: most-common current version == target (harmonize or
  bookkeeping-lag — ask, don't assume)
- ⟨Legacy component⟩ shows target < current — route to "review"
- Pre-release versions in production: ⟨list⟩
