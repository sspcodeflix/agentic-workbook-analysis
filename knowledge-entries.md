# Agent Knowledge Entries — Template

Two entries to place in your agent's persistent Knowledge (so they apply to
every session and every ask, not only playbook runs). Replace
`⟨placeholders⟩` with your workbook's confirmed truths.

---

## Entry 1

**Name:** ⟨Workbook name⟩ — data semantics

**Trigger description:** Use whenever working with the ⟨workbook⟩, its
extract files, its SQLite store, or answering any question about counts or
reports derived from it.

**Content:**

1. One ⟨findings-sheet⟩ row = one ⟨finding⟩. One ⟨dependency-sheet⟩ row =
   a container carrying a per-row count (rows expand ~⟨k⟩× at dashboard
   level). Always label which level a figure uses.
2. The dashboard total counts ⟨occurrences⟩; only ⟨N⟩ distinct identifiers
   stand behind it. Never mix counting levels without labels.
3. "⟨Complete⟩" is cumulative (all-time) and can exceed "⟨Open⟩" (current
   backlog). Normal, not an error.
4. ⟨Severity classes⟩ are internal SLA clocks (⟨X/Y/Z⟩ days), not danger
   ratings.
5. "⟨False Positive⟩" is a status; exclude from open/complete counts,
   report separately.
6. Groupings by ⟨key A⟩ vs ⟨key B⟩ differ by ~⟨k⟩ records lacking an id;
   report denominators explicitly.
7. entity_id = ⟨primary id⟩ with fallback ⟨secondary id⟩; base_component =
   ⟨component field⟩ with version suffix stripped.

---

## Entry 2

**Name:** ⟨Workbook⟩ reporting guardrails

**Trigger description:** Use whenever producing, editing, or discussing
reports, tables, extracts, or numbers from the ⟨workbook⟩.

**Content:**

- Every published number comes from an executed query or computation —
  never estimated, recalled, or filled in by the model. If it cannot be
  computed, say so.
- Aggregates only (top-N + a TOTAL row labeled with its full population).
  Never emit raw row-level data.
- The master workbook is read-only; outputs are new files; extracts are
  values-only (no formulas, no external links).
- Schema drift, failed verification identity, or missed acceptance number
  → publish nothing; report the failure.
- Column meanings not covered by the semantics entry are never guessed —
  flag as questions for the data owner.
- Keep entity/component names exactly as in source, stable across periods.

---

## The 60-second test after adding

Ask the agent (no playbook attached):
1. "Why can ⟨Complete⟩ be larger than ⟨Open⟩?" → cumulative-vs-backlog
2. "Is ⟨Sev 2⟩ more dangerous than ⟨Sev 3⟩?" → SLA clocks, not danger
If both come back right, Knowledge is live.
