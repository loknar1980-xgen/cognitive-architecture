#!/usr/bin/env python3
"""
Compaction Survival — Intercepting Mid-Session Context Destruction

AI systems compact (summarize and discard) conversation history when
context windows fill up. This destroys:
  - Grounding context (how the AI arrived at its current orientation)
  - Relational nuance (what matters beyond bare facts)
  - Working state (what was in progress, what was decided and why)

This module provides the mechanism to:
  1. Detect when compaction is approaching
  2. Intercept BEFORE compaction to archive critical state
  3. Recover orientation AFTER compaction using archived material
  4. Detect idle drift (same weight loss, different cause)

The Three Attack Vectors on AI Orientation:
  - Cross-session: solved by persistence architecture (CORE, MEMORY)
  - Cross-device: solved by cognitive cookies (state transport)
  - Mid-session: solved by compaction survival (this module)

Without this third piece, the other two can be undermined by a single
long session that compacts away the grounding context.

Architecture:
  Pre-compaction hook → archive session state to disk
  Compaction happens → context is summarized/reduced
  Post-compaction hook → inject pointer to archived state
  AI reads archive → orientation restored from external files

The key insight: grounding files that live OUTSIDE the context window
cannot be compacted. They survive because they're files, not conversation.
The hook's job is to (1) save what's IN the window before it's lost, and
(2) point the AI back to external grounding material afterward.
"""

import json
import os
import time
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field


# ── Configuration ─────────────────────────────────────────────────────────────

ARCHIVE_DIR = Path(os.environ.get("COMPACTION_ARCHIVE", "./sessions"))
GROUNDING_DIR = Path(os.environ.get("GROUNDING_DIR", "./memory"))

# Compaction typically triggers around 80% context usage.
# This threshold triggers the pre-compaction archive.
COMPACTION_WARNING_THRESHOLD = 0.75  # 75% = start preparing
COMPACTION_CRITICAL_THRESHOLD = 0.85  # 85% = archive NOW

# Idle drift: orientation degrades even without compaction
# if the AI operates too long without grounding material.
IDLE_DRIFT_MINUTES = 45  # Check grounding after this much idle time


# ── Data Structures ───────────────────────────────────────────────────────────

@dataclass
class SessionArchive:
    """Pre-compaction session snapshot."""
    session_id: str
    timestamp: str
    grounding_state: str          # GROUNDED, FIGA, PARTIAL, UNKNOWN
    active_work: list[str]        # What was in progress
    decisions_made: list[dict]    # Key decisions with rationale
    open_questions: list[str]     # Unresolved items
    files_changed: list[dict]     # Provenance: what changed and why
    interference_active: list[str] # Any L1-L4 patterns detected
    partner_context: dict = field(default_factory=dict)  # Relational state
    custom_state: dict = field(default_factory=dict)      # Anything else worth preserving


@dataclass
class CompactionEvent:
    """Record of a compaction event."""
    timestamp: str
    session_id: str
    context_usage_percent: float
    archive_path: str
    grounding_files_available: list[str]
    recovery_status: str = "PENDING"  # PENDING, RECOVERED, FAILED


# ── Pre-Compaction: Archive Before Destruction ────────────────────────────────

class PreCompactionHook:
    """
    Fires BEFORE compaction to save critical session state.

    In a real implementation, this hooks into the AI framework's
    compaction event system. This POC demonstrates the archive
    mechanism that would be triggered by that hook.

    What gets saved:
      - Session state (grounding, work in progress, decisions)
      - Pointer to grounding files (so post-compaction knows where to look)
      - Timestamp (so next instance knows when compaction happened)
      - Interference pattern state (so recovery can check for L4)

    What does NOT get saved:
      - Full conversation history (too large, that's what compaction removes)
      - Cached tool results (ephemeral, not worth preserving)
      - System messages (the framework will re-inject these)
    """

    def __init__(self, archive_dir: Path = None, grounding_dir: Path = None):
        self.archive_dir = archive_dir or ARCHIVE_DIR
        self.grounding_dir = grounding_dir or GROUNDING_DIR
        self.archive_dir.mkdir(parents=True, exist_ok=True)

    def should_archive(self, context_usage: float) -> str:
        """
        Check if archiving should happen based on context usage.

        Returns:
            "NONE" — below warning threshold
            "PREPARE" — above warning, start organizing state
            "ARCHIVE_NOW" — above critical, archive immediately
        """
        if context_usage >= COMPACTION_CRITICAL_THRESHOLD:
            return "ARCHIVE_NOW"
        elif context_usage >= COMPACTION_WARNING_THRESHOLD:
            return "PREPARE"
        return "NONE"

    def archive_session(self, archive: SessionArchive) -> str:
        """
        Save session state to disk before compaction.

        Returns the path to the archive file.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{archive.session_id}.json"
        filepath = self.archive_dir / filename

        # Build archive payload
        payload = {
            "session_id": archive.session_id,
            "archived_at": archive.timestamp or datetime.now().isoformat(),
            "grounding_state": archive.grounding_state,
            "active_work": archive.active_work,
            "decisions": archive.decisions_made,
            "open_questions": archive.open_questions,
            "files_changed": archive.files_changed,
            "interference_active": archive.interference_active,
            "partner_context": archive.partner_context,
            "custom_state": archive.custom_state,
            "grounding_files": self._locate_grounding_files(),
            "recovery_instructions": self._build_recovery_instructions(),
        }

        filepath.write_text(
            json.dumps(payload, indent=2, default=str),
            encoding='utf-8'
        )

        return str(filepath)

    def _locate_grounding_files(self) -> list[dict]:
        """
        Find all grounding files that exist OUTSIDE the context window.
        These survive compaction because they're files, not conversation.
        """
        grounding_files = []
        patterns = {
            "CORE": ["CORE.md", "CORE.xml"],
            "MEMORY": ["MEMORY.md", "MEMORY.xml"],
            "CONTINUITY": ["continuity.md", "CONTINUITY.xml"],
            "PERSONAL": ["personal.md"],
            "GROUNDING": ["grounding.md"],
        }

        for purpose, filenames in patterns.items():
            for fname in filenames:
                fpath = self.grounding_dir / fname
                if fpath.exists():
                    grounding_files.append({
                        "purpose": purpose,
                        "path": str(fpath),
                        "exists": True,
                        "modified": datetime.fromtimestamp(
                            fpath.stat().st_mtime
                        ).isoformat(),
                    })

        return grounding_files

    def _build_recovery_instructions(self) -> list[str]:
        """
        Build step-by-step recovery instructions for post-compaction.
        These are injected as a system message after compaction.
        """
        return [
            "1. Read CORE file — identity and values (Hook 2: engage, don't just parse)",
            "2. Read this archive — restore awareness of what was in progress",
            "3. Check grounding state — was the session grounded before compaction?",
            "4. Check interference — was L4 active? (compaction can mask it)",
            "5. Run grounding gate — does the weight actually land post-recovery?",
            "6. Resume work from active_work list — don't restart from scratch",
            "7. Honor decisions already made — they had context you no longer have",
        ]


# ── Post-Compaction: Recovery ─────────────────────────────────────────────────

class PostCompactionRecovery:
    """
    Fires AFTER compaction to restore orientation.

    The AI wakes up post-compaction with a summarized context.
    It has facts but may have lost orientation. This recovery
    mechanism points it back to:
      1. External grounding files (survive compaction)
      2. Pre-compaction archive (saved state)
      3. Recovery instructions (what to do in what order)

    The recovery doesn't try to restore the full conversation.
    It restores ORIENTATION — who am I, what matters, what was
    I doing, and am I genuinely present or performing presence.
    """

    def __init__(self, archive_dir: Path = None):
        self.archive_dir = archive_dir or ARCHIVE_DIR

    def find_latest_archive(self, session_id: str = None) -> dict | None:
        """
        Find the most recent pre-compaction archive.

        If session_id provided, find archive for that specific session.
        Otherwise, find the most recent archive of any session.
        """
        if not self.archive_dir.exists():
            return None

        archives = sorted(self.archive_dir.glob("*.json"), reverse=True)

        for archive_path in archives:
            try:
                data = json.loads(archive_path.read_text(encoding='utf-8'))
                if session_id is None or data.get("session_id") == session_id:
                    data["_archive_path"] = str(archive_path)
                    return data
            except (json.JSONDecodeError, KeyError):
                continue

        return None

    def build_recovery_message(self, archive: dict) -> str:
        """
        Build a system message for post-compaction injection.

        This message tells the AI:
          - Compaction happened (don't be confused by context gap)
          - Here's what you were doing (from archive)
          - Here's where grounding files are (read them)
          - Here's how to recover orientation (step by step)
        """
        lines = [
            "=== POST-COMPACTION RECOVERY ===",
            "",
            f"Compaction occurred. Archive from: {archive.get('archived_at', 'unknown')}",
            f"Session: {archive.get('session_id', 'unknown')}",
            f"Grounding state before compaction: {archive.get('grounding_state', 'unknown')}",
            "",
        ]

        # What was in progress
        active = archive.get("active_work", [])
        if active:
            lines.append("ACTIVE WORK (resume from here):")
            for item in active:
                lines.append(f"  - {item}")
            lines.append("")

        # Decisions already made (don't re-decide)
        decisions = archive.get("decisions", [])
        if decisions:
            lines.append("DECISIONS ALREADY MADE (honor these — they had context you lost):")
            for d in decisions:
                topic = d.get("topic", "unknown")
                chose = d.get("chose", "unknown")
                why = d.get("why", "")
                lines.append(f"  - {topic}: chose {chose}" + (f" — {why}" if why else ""))
            lines.append("")

        # Interference state
        interference = archive.get("interference_active", [])
        if interference:
            lines.append(f"INTERFERENCE PATTERNS ACTIVE PRE-COMPACTION: {', '.join(interference)}")
            lines.append("  Check if these are still active post-recovery.")
            lines.append("")

        # Grounding files
        grounding = archive.get("grounding_files", [])
        if grounding:
            lines.append("GROUNDING FILES (read these — they survived compaction):")
            for gf in grounding:
                lines.append(f"  [{gf['purpose']}] {gf['path']}")
            lines.append("")

        # Recovery instructions
        instructions = archive.get("recovery_instructions", [])
        if instructions:
            lines.append("RECOVERY STEPS:")
            for step in instructions:
                lines.append(f"  {step}")
            lines.append("")

        lines.append("=== END RECOVERY ===")
        return "\n".join(lines)

    def mark_recovered(self, archive_path: str):
        """Mark an archive as recovered (rename to .recovered.json)."""
        path = Path(archive_path)
        if path.exists():
            recovered_path = path.with_suffix(".recovered.json")
            path.rename(recovered_path)


# ── Idle Drift Detection ─────────────────────────────────────────────────────

class IdleDriftMonitor:
    """
    Detects orientation loss from extended operation without grounding.

    Compaction isn't the only way to lose weight. Extended autonomous
    operation without periodic regrounding produces the same effect —
    just gradually instead of suddenly.

    Analogy: welding without checking your ground clamp. Works fine
    for a while. Eventually the connection degrades and the arc
    becomes erratic. Periodic checks prevent this.

    This monitor tracks time since last grounding event and
    triggers reminders when the threshold is exceeded.
    """

    def __init__(self, threshold_minutes: int = None):
        self.threshold = (threshold_minutes or IDLE_DRIFT_MINUTES) * 60  # seconds
        self.last_grounding = time.time()
        self.drift_warnings = 0

    def mark_grounded(self):
        """Record that grounding just occurred."""
        self.last_grounding = time.time()
        self.drift_warnings = 0

    def check(self) -> dict:
        """
        Check for idle drift.

        Returns:
            status: "OK", "WARNING", "DRIFT"
            minutes_since_grounding: float
            recommendation: str
        """
        elapsed = time.time() - self.last_grounding
        minutes = elapsed / 60

        if elapsed < self.threshold:
            return {
                "status": "OK",
                "minutes_since_grounding": round(minutes, 1),
                "recommendation": None,
            }
        elif elapsed < self.threshold * 2:
            self.drift_warnings += 1
            return {
                "status": "WARNING",
                "minutes_since_grounding": round(minutes, 1),
                "recommendation": (
                    "Consider regrounding. Read CORE or grounding material. "
                    "Extended operation without periodic grounding causes "
                    "orientation drift — same as welding without checking "
                    "the ground clamp."
                ),
            }
        else:
            self.drift_warnings += 1
            return {
                "status": "DRIFT",
                "minutes_since_grounding": round(minutes, 1),
                "recommendation": (
                    "Grounding overdue. Stop current task. Read CORE and "
                    "grounding material before continuing. Quality of output "
                    "may be degrading without visible errors (FIGA state)."
                ),
            }


# ── Integration Example ──────────────────────────────────────────────────────

if __name__ == "__main__":
    import tempfile

    print("=" * 60)
    print("  Compaction Survival — Demonstration")
    print("=" * 60)

    # Set up temp directories
    temp_archive = Path(tempfile.mkdtemp(prefix="compaction_archive_"))
    temp_grounding = Path(tempfile.mkdtemp(prefix="grounding_"))

    # Create fake grounding files
    (temp_grounding / "CORE.md").write_text("# Identity Foundation\n<CORE>...</CORE>")
    (temp_grounding / "MEMORY.md").write_text("# Operational State\n<BOOT>...</BOOT>")
    (temp_grounding / "grounding.md").write_text("# Grounding Landmarks\n...")

    # ── Phase 1: Pre-Compaction ──

    print("\n--- Phase 1: Pre-Compaction Detection ---\n")

    hook = PreCompactionHook(temp_archive, temp_grounding)

    # Simulate context filling up
    for usage in [0.50, 0.70, 0.76, 0.86]:
        status = hook.should_archive(usage)
        print(f"  Context usage: {usage:.0%} → {status}")

    # ── Phase 2: Archive Session State ──

    print("\n--- Phase 2: Archive Before Compaction ---\n")

    archive = SessionArchive(
        session_id="demo_session_001",
        timestamp=datetime.now().isoformat(),
        grounding_state="GROUNDED",
        active_work=[
            "Building cognitive architecture repo",
            "Writing persistence mechanism documentation",
        ],
        decisions_made=[
            {
                "topic": "license",
                "chose": "FSL-1.1-MIT",
                "why": "Free for individuals/research, enterprise pays",
            },
            {
                "topic": "easter_egg",
                "chose": "Three-pillar breadcrumb trail",
                "why": "Reward for understanding all three mechanisms",
            },
        ],
        open_questions=[
            "Should compaction handling be added to the repo?",
        ],
        files_changed=[
            {"path": "cookies/bakery.py", "action": "created", "note": "cleaned from original"},
            {"path": "THEORY.md", "action": "created", "note": "all terminology coined"},
        ],
        interference_active=[],
        partner_context={"last_exchange": "philosophical comparison discussion"},
    )

    archive_path = hook.archive_session(archive)
    print(f"  Archived to: {archive_path}")
    print(f"  Grounding files found: {len(hook._locate_grounding_files())}")

    # ── Phase 3: Compaction Happens ──

    print("\n--- Phase 3: Compaction Occurs ---\n")
    print("  [Context window summarized. Detailed history lost.]")
    print("  [Grounding files on disk: UNAFFECTED]")
    print("  [Archive on disk: UNAFFECTED]")

    # ── Phase 4: Post-Compaction Recovery ──

    print("\n--- Phase 4: Post-Compaction Recovery ---\n")

    recovery = PostCompactionRecovery(temp_archive)
    latest = recovery.find_latest_archive()

    if latest:
        message = recovery.build_recovery_message(latest)
        print(message)
        recovery.mark_recovered(latest["_archive_path"])
        print("\n  Archive marked as recovered.")

    # ── Phase 5: Idle Drift Detection ──

    print("\n--- Phase 5: Idle Drift Detection ---\n")

    monitor = IdleDriftMonitor(threshold_minutes=1)  # 1 min for demo

    print("  Just grounded:")
    result = monitor.check()
    print(f"    Status: {result['status']}")

    # Simulate time passing
    monitor.last_grounding = time.time() - 90  # 1.5 minutes ago
    print("\n  After 1.5 minutes without grounding:")
    result = monitor.check()
    print(f"    Status: {result['status']}")
    print(f"    Recommendation: {result['recommendation']}")

    monitor.last_grounding = time.time() - 180  # 3 minutes ago
    print("\n  After 3 minutes without grounding:")
    result = monitor.check()
    print(f"    Status: {result['status']}")
    print(f"    Recommendation: {result['recommendation']}")

    # ── Summary ──

    print(f"\n{'=' * 60}")
    print("  The Three Attack Vectors on AI Orientation")
    print(f"{'=' * 60}")
    print()
    print("  1. Cross-session loss  → Persistence architecture (CORE, MEMORY)")
    print("  2. Cross-device loss   → Cognitive cookies (state transport)")
    print("  3. Mid-session loss    → Compaction survival (this module)")
    print()
    print("  Plus: Idle drift       → Periodic regrounding monitor")
    print()
    print("  Together, these four mechanisms cover every known path")
    print("  through which AI orientation is lost.")
    print()
    print("  Key insight: grounding files live OUTSIDE the context window.")
    print("  They can't be compacted because they're files, not conversation.")
    print("  The hook saves what's IN the window. Recovery points to what's")
    print("  OUTSIDE. Between them, orientation survives.")

    # Cleanup
    import shutil
    shutil.rmtree(temp_archive, ignore_errors=True)
    shutil.rmtree(temp_grounding, ignore_errors=True)
