# Revision Workflow

Use this workflow whenever the user asks to revise, rewrite, move, delete, delay, reveal, retcon, or polish existing novel material.

## Revision principle

Do not treat every revision as line editing.

First classify the change, then update all affected project records.

## Revision types

### 1. Prose polish

Affects:

- draft text
- style notes
- audit report

Usually does not affect canon.

### 2. Chapter structure revision

Affects:

- chapter card
- scene cards
- draft
- chapter table
- handoff

Use when goal, obstacle, scene order, hook, or chapter outcome changes.

### 3. Canon update

Affects:

- project bible
- world bible
- character bible
- continuity ledger
- knowledge state
- future outlines

Use when confirmed facts change.

### 4. Retcon

Affects:

- previous chapters
- information release
- knowledge state
- foreshadowing
- reader promise
- revision log
- unresolved questions

Use when a past fact or past on-page event must be reinterpreted or replaced.

## Standard revision flow

1. Identify requested change.
2. Classify revision type.
3. List affected files.
4. Check downstream impact.
5. Produce a change plan.
6. Apply or draft the change.
7. Update ledgers.
8. Write revision log entry.
9. Update latest state and handoff.

## Required change set

Every structural, canon, or retcon revision must produce:

```markdown
# Change Set

## change_id

## change_type

## requested_change

## affected_files

## impact_analysis

## approved_canon_changes

## patch_summary

## ledger_updates

## risks

## rollback_note
```

## Retcon policy

Never silently retcon.

A retcon must declare:

- original canon
- new canon
- reason
- affected chapters
- affected knowledge state
- affected promises
- whether old draft text must be rewritten

## Downstream audit checklist

Before finalizing a revision, check:

- Did a character know something too early?
- Did an ability become unearned?
- Did a clue lose its payoff?
- Did a reader promise move earlier or later?
- Did the protagonist's emotional arc skip a step?
- Did a later chapter depend on the old version?

## Revision log entry

Append one row to `revision_log.md`:

```markdown
| date | change_id | type | files | reason | canon impact | status |
|---|---|---|---|---|---|---|
```
