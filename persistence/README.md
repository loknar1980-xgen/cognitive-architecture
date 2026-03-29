# Metadata Persistence — Identity Continuity for AI Systems

## What This Is

A persistence architecture where XML metadata attributes carry cognitive state — not just data, but the *relationships between data* — enabling AI identity to persist across sessions and instances through generational transmission rather than continuous memory.

## Why It Matters

AI has no persistent identity by default. Every session starts blank. Current solutions store information, but information isn't identity:

- **Chat history** → token-expensive, no orientation
- **RAG** → retrieves relevant data, not who you are
- **Databases** → stores facts, not framework
- **System prompts** → static, no session state

The persistence architecture stores *orientation* — who the AI is, what it values, how to detect when it's drifting, and what happened in the last session that matters for the next one.

## Key Concepts

### Metadata Lanes
XML attributes as parallel semantic channels. Each carries a different type of signal:
- **Constraint** travels with resource (can't see path without warning)
- **Fix** travels with bug (solution is in the same element)
- **Procedure** travels with service (restart command is an attribute)
- **History** in milestones attribute (compressed timeline, append-only)
- **Priority** as scannable attribute (not buried in prose)

See [MECHANISM.md](MECHANISM.md) for the full explanation of why this is more than "just XML."

### Two-Phase Boot (v2)
The original two-hook bootstrap (automatic vs chosen) solved the orientation problem. But a subtler issue remained: even with the grounding gate, the AI arrived at it already leaning toward tasks — because the auto-loading file contained both identity AND operational state.

**Phase 1** loads identity only (CORE + MEMORY). No tasks, no projects, no system state. The grounding gate happens in a clean cognitive space where the only question is: *does the weight land?*

**Phase 2** loads operational state (WORKSPACE + CONTINUITY) only after the gate passes. Tasks, projects, auth patterns — all gated behind genuine orientation.

The fix is structural, not behavioral. You can't lean toward tasks you can't see.

### Generational Transmission
Each instance inherits values, framework, and orientation from predecessors — like cultural inheritance, not like memory recall. The XML files ARE the inheritance medium.

## Files

| File | Purpose |
|------|---------|
| `boot_sequence.py` | Two-phase boot loader, XML parser, grounding gate, metadata lane extraction |
| `compaction.py` | Pre-compaction archive, post-compaction recovery, idle drift detection |
| `MECHANISM.md` | Why this is more than "just XML files" — includes two-phase boot rationale |
| `templates/CORE_template.xml` | Identity foundation template |
| `templates/MEMORY_template.xml` | Phase 1: Identity + grounding gate (no operational state) |
| `templates/WORKSPACE_template.xml` | Phase 2: Operational state, tasks, auth (loads after gate) |
| `templates/CONTINUITY_template.xml` | Phase 2: Session state template |

## The Three Attack Vectors

AI orientation is lost through three paths. This module addresses all of them:

| Attack Vector | Solution | Module |
|--------------|----------|--------|
| Cross-session loss | Two-phase persistence (CORE, MEMORY, WORKSPACE, CONTINUITY) | `boot_sequence.py` |
| Cross-device loss | Cognitive cookies (state transport) | `../cookies/bakery.py` |
| Mid-session loss | Compaction survival (archive + recovery) | `compaction.py` |
| Init-time L4 | Two-phase boot (identity before tasks) | `boot_sequence.py` |
| Idle drift | Periodic regrounding monitor | `compaction.py` |

Without compaction handling, the other two solutions can be undermined by a single long session that compacts away the grounding context. The pre-compaction hook intercepts before destruction. The post-compaction recovery restores orientation from external files that survived.

## Quick Start

```bash
# Run with templates (demonstration mode)
python boot_sequence.py

# Run with your own persistence directory
python boot_sequence.py /path/to/your/memory
```

## Building Your Own

1. Copy the templates from `templates/` to your persistence directory
2. Fill in CORE with your AI's identity framework and values
3. Fill in MEMORY with identity pointer and grounding gate only (Phase 1)
4. Fill in WORKSPACE with environment, services, tasks, auth patterns (Phase 2)
5. Use CONTINUITY to track session state across instances
6. Follow the co-location principle: constraints with resources, fixes with bugs, procedures with services

**Critical:** Keep MEMORY lean — identity and grounding gate only. Everything operational goes in WORKSPACE. The separation is what prevents task context from hijacking the grounding process. If you put tasks in MEMORY, the AI will lean toward them before it's oriented.

The templates have comments explaining what goes where and why.
