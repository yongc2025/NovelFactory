# Longform Project System Design

## Design goal

This system turns long-form novel creation into a Git-backed project management workflow.

The central rule is:

```text
A novel project is evolving state, not isolated prose.
```

Every AI-assisted writing session must either:

1. create project state,
2. read project state,
3. produce one stage artifact,
4. audit project state,
5. update project state,
6. or create a handoff package for the next session.

## Components

### 1. Workflow specifications

Located in `workflow/`.

These files define how to run the project:

- project startup
- state lifecycle
- chapter production
- revision and retcon
- resume after interruption

### 2. Templates

Located in `templates/`.

These files define stable project records:

- project bible
- latest state
- 12-layer ledger
- character bible
- world bible
- chapter card
- scene cards
- continuity ledger
- knowledge-state ledger
- foreshadowing ledger
- reader-promise ledger
- revision log
- handoff package

### 3. Project instances

A real novel project should live outside this system directory, for example:

```text
projects/project-001/
```

Each project copies and fills the templates.

## Recommended project structure

```text
projects/<project-id>/
├── 00_manifest/
│   ├── project_manifest.md
│   └── latest_state.md
├── 01_foundation/
│   ├── project_bible.md
│   ├── twelve_layer_ledger.md
│   └── reader_promise_ledger.md
├── 02_world/
│   ├── world_bible.md
│   ├── factions.md
│   ├── rules.md
│   └── information_release.md
├── 03_characters/
│   ├── character_bible.md
│   ├── relationship_map.md
│   ├── knowledge_state.md
│   └── emotion_arc.md
├── 04_outline/
│   ├── full_outline.md
│   ├── volume_01_outline.md
│   └── chapter_table.md
├── 05_chapters/
│   └── ch001/
│       ├── chapter_card.md
│       ├── scene_cards.md
│       ├── draft.md
│       ├── audit.md
│       └── handoff.md
├── 06_ledgers/
│   ├── continuity_ledger.md
│   ├── foreshadowing_ledger.md
│   ├── revision_log.md
│   ├── retcon_log.md
│   └── unresolved_questions.md
└── 07_exports/
    ├── volume_01_clean.md
    └── synopsis.md
```

## Minimum viable state

Before drafting a chapter, the project should have at least:

1. `project_bible.md`
2. `twelve_layer_ledger.md`
3. `character_bible.md`
4. `chapter_table.md`
5. `knowledge_state.md`
6. latest chapter `handoff.md`

If any file is missing, reconstruct temporary state and mark uncertain items as `待确认`.

## Change policy

Never silently change canon.

Classify every modification as one of:

1. prose polish
2. chapter structure revision
3. canon update
4. retcon

Any canon update or retcon must update affected ledgers and `revision_log.md`.

## Git policy

Recommended branches:

```text
master                  stable project state
feature/longform-*      system development
project/<id>-draft      active novel drafting
revision/<id>-topic     risky structural edits
experiment/<id>-topic   non-canon trial versions
```

Commit messages should identify the affected layer:

```text
foundation: define project bible v0.1
outline: add volume 01 chapter table
chapter: draft ch003
ledger: update knowledge state after ch003
revision: retcon magic discovery timing
```
