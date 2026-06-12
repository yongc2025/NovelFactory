# Longform Project System

`longform-project-system` is an independent long-form novel project management layer for NovelFactory.

It is designed to work with an AI editorial skill such as `ai-novel-editorial-team`, while GitHub stores the durable project state.

## Purpose

A long-form novel should not be managed as isolated chapter drafts. It should be managed as evolving project state:

```text
read project state -> produce current artifact -> audit consistency -> update state files -> write handoff package
```

## What this module manages

- project bible and 12-layer foundation
- world, character, and continuity records
- chapter planning and scene cards
- draft, audit, and revision records
- character knowledge state
- information release
- foreshadowing and payoff tracking
- reader promise tracking
- handoff packages between writing sessions

## Repository role

This directory is intentionally isolated from the current NovelFactory application code. It can be used as:

1. a documentation system for the long-form workflow,
2. a template library for novel projects,
3. a state model for future automation,
4. a Git-backed project memory for AI-assisted serial writing.

## Suggested project directory

```text
projects/<project-id>/
├── 00_manifest/
├── 01_foundation/
├── 02_world/
├── 03_characters/
├── 04_outline/
├── 05_chapters/
├── 06_ledgers/
└── 07_exports/
```

## Default operating rule

Never draft prose before the current project state, chapter card, and scene cards are established or reconstructed.
