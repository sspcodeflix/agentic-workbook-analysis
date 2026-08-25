# Acceptance Baseline — Template

The agent's entry exam: before automation is trusted, a human verifies one
snapshot's numbers by hand (pivots, filters + status bar, COUNTIFS,
cross-table arithmetic). The pipeline's FIRST run must reproduce every
value exactly. Later periods: values drift; the verification identities in
the playbook must still hold.

Update this file only after hand-verifying a new baseline; note the
snapshot date.

## How to build one (the method that worked)

1. Extract each analysis table once via pivots (exact headers, TOTAL rows
   covering the full population).
2. Verify independently: rebuild one pivot yourself; spot-check cells with
   filters + the status-bar Count; run cross-table identities
   (subtotal + remainder = category total; total − resolved = remaining).
3. Record every verified number below with its snapshot date.

## Baseline — snapshot ⟨date⟩ (hand-verified)

| Metric | Value |
|---|---|
| Dashboard total (cached Summary value) | ⟨N⟩ |
| — status splits | ⟨…⟩ |
| Visible source rows | ⟨N⟩ |
| Distinct identifiers behind the dashboard total | ⟨N⟩ |
| Open total (by entity / by category — note both) | ⟨N⟩ / ⟨N⟩ |
| Distinct entities / categories / pairs | ⟨N⟩ / ⟨N⟩ / ⟨N⟩ |
| Top entity, top category, top pair (with values) | ⟨…⟩ |
| Dependency rows / resolved / remaining | ⟨N⟩ / ⟨N⟩ / ⟨N⟩ |
| Distinct base components | ⟨N⟩ |
| Exceptions (false-positive analog) total | ⟨N⟩ |
| Recurrence (reopened) total / combinations | ⟨N⟩ / ⟨N⟩ |
