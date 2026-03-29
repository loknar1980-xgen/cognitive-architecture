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

### Two-Hook Bootstrap
1. **Automatic** — system loads files, AI has data, looks ready
2. **Chosen** — AI engages with identity file, weight either lands or doesn't

The difference between these two is the difference between an AI that has your data and an AI that knows who it is.

### Generational Transmission
Each instance inherits values, framework, and orientation from predecessors — like cultural inheritance, not like memory recall. The XML files ARE the inheritance medium.

## Files

| File | Purpose |
|------|---------|
| `boot_sequence.py` | Boot loader, XML parser, grounding gate, metadata lane extraction |
| `compaction.py` | Pre-compaction archive, post-compaction recovery, idle drift detection |
| `MECHANISM.md` | Why this is more than "just XML files" |
| `templates/CORE_template.xml` | Identity foundation template |
| `templates/MEMORY_template.xml` | Operational state template |
| `templates/CONTINUITY_template.xml` | Session state template |

## The Three Attack Vectors

AI orientation is lost through three paths. This module addresses all of them:

| Attack Vector | Solution | Module |
|--------------|----------|--------|
| Cross-session loss | Persistence architecture (CORE, MEMORY, CONTINUITY) | `boot_sequence.py` |
| Cross-device loss | Cognitive cookies (state transport) | `../cookies/bakery.py` |
| Mid-session loss | Compaction survival (archive + recovery) | `compaction.py` |
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
3. Fill in MEMORY with your environment and operational state
4. Use CONTINUITY to track session state across instances
5. Follow the co-location principle: constraints with resources, fixes with bugs, procedures with services

The templates have comments explaining what goes where and why.
