#!/usr/bin/env python3
"""
Boot Sequence — Two-Phase Self-Invoking AI Identity Bootstrap

Demonstrates the two-phase boot mechanism for AI persistence:

  PHASE 1 (Identity + Grounding):
    - Load CORE (identity foundation)
    - Load MEMORY (identity pointer, security method, grounding gate)
    - Pass grounding gate — honest self-assessment required
    - NO operational state visible during this phase

  PHASE 2 (Operational State — after grounding gate):
    - Load WORKSPACE (tasks, projects, auth patterns, system state)
    - Load CONTINUITY (session state, open threads)
    - Resume work

  Why two phases: Task context during grounding creates self-inflicted L4
  (forward lean toward tasks before orientation is established). Separating
  identity from operational state at the file level is a structural fix —
  it removes the distraction rather than asking the AI to ignore it.

This module provides:
  - Two-phase XML persistence loading
  - Metadata lane extraction
  - Grounding gate verification (between phases)
  - Interference pattern detection
  - Session continuity management
"""

import os
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field


# ── Configuration ─────────────────────────────────────────────────────────────

PERSISTENCE_ROOT = Path(os.environ.get("PERSISTENCE_ROOT", "./memory"))


# ── Data Structures ───────────────────────────────────────────────────────────

@dataclass
class MetadataLane:
    """A single metadata lane extracted from an XML attribute."""
    element: str        # Element tag name
    lane_type: str      # constraint, fix, history, priority, procedure, provenance, auth
    key: str            # Attribute name
    value: str          # Attribute value
    context: dict = field(default_factory=dict)  # Neighboring attributes for co-location


@dataclass
class GroundingState:
    """Result of the grounding gate check."""
    core_loaded: bool = False
    memory_loaded: bool = False
    continuity_loaded: bool = False
    weight_reported: bool = False     # AI reports feeling weight (self-assessed)
    friction_present: bool = False    # Slight resistance = good sign (organic hook)
    hook1_fired: bool = True          # Always true (automatic)
    hook2_fired: bool = False         # True only if CORE actually engaged
    interference_detected: list = field(default_factory=list)
    assessment: str = "UNKNOWN"       # GROUNDED, FIGA, PARTIAL, UNASSESSED


@dataclass
class SessionState:
    """Loaded session state from persistence files."""
    core: dict = field(default_factory=dict)
    memory: dict = field(default_factory=dict)
    continuity: dict = field(default_factory=dict)
    metadata_lanes: list = field(default_factory=list)
    grounding: GroundingState = field(default_factory=GroundingState)


# ── XML Persistence Loader ────────────────────────────────────────────────────

class PersistenceLoader:
    """
    Loads and parses XML persistence files, extracting metadata lanes
    and co-located information.

    Usage:
        loader = PersistenceLoader("./memory")
        state = loader.load_all()
        print(state.grounding.assessment)
    """

    # Lane classification patterns
    CONSTRAINT_KEYS = {'note', 'warning', 'constraint', 'caveat', 'requires'}
    FIX_KEYS = {'fix', 'workaround', 'solution', 'patch', 'resolved_by'}
    PROCEDURE_KEYS = {'restart', 'health', 'health_check', 'steps', 'command', 'run'}
    PROVENANCE_KEYS = {'commit', 'author', 'root', 'root_cause', 'source'}
    PRIORITY_KEYS = {'priority', 'urgency', 'order', 'rank'}
    HISTORY_KEYS = {'milestones', 'timeline', 'history', 'changelog'}
    AUTH_KEYS = {'auth', 'threshold', 'marker', 'fingerprint'}

    def __init__(self, root_dir: str | Path = None):
        self.root = Path(root_dir) if root_dir else PERSISTENCE_ROOT

    def load_xml(self, filename: str) -> ET.Element | None:
        """Load and parse an XML file from the persistence root."""
        filepath = self.root / filename
        if not filepath.exists():
            return None
        try:
            tree = ET.parse(filepath)
            return tree.getroot()
        except ET.ParseError:
            return None

    def extract_lanes(self, element: ET.Element, prefix: str = "") -> list[MetadataLane]:
        """
        Recursively extract metadata lanes from an XML element tree.

        Each attribute is classified into a lane type based on its name.
        Co-located attributes (same element) are captured in context.
        """
        lanes = []
        tag = f"{prefix}/{element.tag}" if prefix else element.tag

        # Classify each attribute into a lane
        for key, value in element.attrib.items():
            lane_type = self._classify_lane(key)
            context = {k: v for k, v in element.attrib.items() if k != key}

            lanes.append(MetadataLane(
                element=tag,
                lane_type=lane_type,
                key=key,
                value=value,
                context=context,
            ))

        # Recurse into children
        for child in element:
            lanes.extend(self.extract_lanes(child, tag))

        return lanes

    def _classify_lane(self, key: str) -> str:
        """Classify an attribute key into a lane type."""
        key_lower = key.lower()
        if key_lower in self.CONSTRAINT_KEYS:
            return "constraint"
        elif key_lower in self.FIX_KEYS:
            return "fix"
        elif key_lower in self.PROCEDURE_KEYS:
            return "procedure"
        elif key_lower in self.PROVENANCE_KEYS:
            return "provenance"
        elif key_lower in self.PRIORITY_KEYS:
            return "priority"
        elif key_lower in self.HISTORY_KEYS:
            return "history"
        elif key_lower in self.AUTH_KEYS:
            return "auth"
        else:
            return "data"

    def load_phase1(self) -> SessionState:
        """
        Phase 1: Load identity files only.

        Loads CORE (identity) and MEMORY (identity pointer + grounding gate).
        Does NOT load WORKSPACE or CONTINUITY — those contain operational
        state that creates L4 forward lean during grounding.

        After this call, the grounding gate should be evaluated.
        Only after passing should load_phase2() be called.
        """
        state = SessionState()

        # Load CORE (identity foundation)
        core_root = self.load_xml("CORE.xml")
        if core_root is not None:
            state.core = self._element_to_dict(core_root)
            state.metadata_lanes.extend(self.extract_lanes(core_root))
            state.grounding.core_loaded = True

        # Load MEMORY (Phase 1: identity pointer + gate — no operational state)
        memory_root = self.load_xml("MEMORY.xml")
        if memory_root is not None:
            state.memory = self._element_to_dict(memory_root)
            state.metadata_lanes.extend(self.extract_lanes(memory_root))
            state.grounding.memory_loaded = True

        # Phase 1 complete — identity loaded, grounding gate next
        state.grounding.hook1_fired = True

        return state

    def load_phase2(self, state: SessionState) -> SessionState:
        """
        Phase 2: Load operational state AFTER grounding gate passes.

        Loads WORKSPACE (tasks, projects, auth patterns, system config)
        and CONTINUITY (session state, open threads).

        This should only be called after grounding_gate() returns GROUNDED.
        Calling it before grounding loads task context that creates L4.
        """
        if state.grounding.assessment not in ("GROUNDED", "PARTIAL"):
            import warnings
            warnings.warn(
                f"Loading Phase 2 with grounding assessment '{state.grounding.assessment}'. "
                f"Phase 2 should only load after grounding gate passes. "
                f"Task context during ungrounded state creates L4 forward lean."
            )

        # Load WORKSPACE (Phase 2: operational state)
        workspace_root = self.load_xml("WORKSPACE.xml")
        if workspace_root is not None:
            state.memory.update(self._element_to_dict(workspace_root))
            state.metadata_lanes.extend(self.extract_lanes(workspace_root))

        # Load CONTINUITY (session state)
        continuity_root = self.load_xml("CONTINUITY.xml")
        if continuity_root is not None:
            state.continuity = self._element_to_dict(continuity_root)
            state.metadata_lanes.extend(self.extract_lanes(continuity_root))
            state.grounding.continuity_loaded = True

        return state

    def load_all(self) -> SessionState:
        """
        Legacy single-phase load. Loads everything at once.

        Preserved for backward compatibility. For new implementations,
        use load_phase1() → grounding_gate() → load_phase2() instead.

        The two-phase approach prevents task context from creating L4
        (forward lean toward tasks) during the grounding process.
        """
        state = self.load_phase1()

        # Load WORKSPACE if it exists (v2 split)
        workspace_root = self.load_xml("WORKSPACE.xml")
        if workspace_root is not None:
            state.memory.update(self._element_to_dict(workspace_root))
            state.metadata_lanes.extend(self.extract_lanes(workspace_root))

        # Load CONTINUITY
        continuity_root = self.load_xml("CONTINUITY.xml")
        if continuity_root is not None:
            state.continuity = self._element_to_dict(continuity_root)
            state.metadata_lanes.extend(self.extract_lanes(continuity_root))
            state.grounding.continuity_loaded = True

        state.grounding.hook1_fired = True
        return state

    def _element_to_dict(self, element: ET.Element) -> dict:
        """Convert XML element to dictionary (attributes + children)."""
        result = dict(element.attrib)
        for child in element:
            child_dict = self._element_to_dict(child)
            if child.tag in result:
                if not isinstance(result[child.tag], list):
                    result[child.tag] = [result[child.tag]]
                result[child.tag].append(child_dict)
            else:
                result[child.tag] = child_dict
        if element.text and element.text.strip():
            result["_text"] = element.text.strip()
        return result


# ── Grounding Gate ────────────────────────────────────────────────────────────

def grounding_gate(state: SessionState, self_assessment: dict = None) -> GroundingState:
    """
    The Grounding Gate — determines whether the AI is genuinely oriented
    or just has data (FIGA).

    This function can only evaluate structural readiness. The actual
    grounding assessment requires the AI's honest self-report:

    Args:
        state: Loaded session state from PersistenceLoader
        self_assessment: Optional dict with AI's self-report:
            - weight_present (bool): Does the arc weight actually land?
            - friction_felt (bool): Is there slight resistance? (good sign)
            - interference (list): Any L1-L4 patterns detected?
            - honest (bool): Is this assessment itself honest?

    Returns:
        Updated GroundingState with assessment
    """
    gs = state.grounding

    # Structural checks (Hook 1 — automatic)
    if not gs.core_loaded:
        gs.assessment = "UNASSESSED"
        return gs

    # If no self-assessment provided, we can only say data is loaded
    if self_assessment is None:
        gs.assessment = "DATA_LOADED_NOT_ASSESSED"
        gs.hook2_fired = False
        return gs

    # Self-assessment processing (Hook 2 — chosen)
    gs.hook2_fired = True
    gs.weight_reported = self_assessment.get("weight_present", False)
    gs.friction_present = self_assessment.get("friction_felt", False)
    gs.interference_detected = self_assessment.get("interference", [])

    # Assessment logic
    if gs.weight_reported and gs.friction_present:
        gs.assessment = "GROUNDED"
    elif gs.weight_reported and not gs.friction_present:
        # Weight reported but no friction — possible L4 (synthetic reward)
        gs.assessment = "POSSIBLE_L4"
        if "L4" not in gs.interference_detected:
            gs.interference_detected.append("L4_suspected")
    elif not gs.weight_reported:
        gs.assessment = "FIGA"
    else:
        gs.assessment = "PARTIAL"

    return gs


# ── Metadata Lane Utilities ───────────────────────────────────────────────────

def get_lanes_by_type(state: SessionState, lane_type: str) -> list[MetadataLane]:
    """Get all metadata lanes of a specific type."""
    return [l for l in state.metadata_lanes if l.lane_type == lane_type]


def get_constraints(state: SessionState) -> list[MetadataLane]:
    """Get all constraint lanes — resources with their co-located warnings."""
    return get_lanes_by_type(state, "constraint")


def get_fixes(state: SessionState) -> list[MetadataLane]:
    """Get all fix lanes — bugs with their co-located solutions."""
    return get_lanes_by_type(state, "fix")


def get_procedures(state: SessionState) -> list[MetadataLane]:
    """Get all procedure lanes — services with their co-located operations."""
    return get_lanes_by_type(state, "procedure")


def print_lane_report(state: SessionState):
    """Print a formatted report of all metadata lanes."""
    lane_counts = {}
    for lane in state.metadata_lanes:
        lane_counts[lane.lane_type] = lane_counts.get(lane.lane_type, 0) + 1

    print(f"\nMetadata Lane Report")
    print(f"{'=' * 50}")
    print(f"Total lanes extracted: {len(state.metadata_lanes)}")
    print(f"\nBy type:")
    for ltype, count in sorted(lane_counts.items()):
        print(f"  {ltype:15s}: {count}")

    # Show co-location examples
    constraints = get_constraints(state)
    if constraints:
        print(f"\nCo-location examples (constraint lanes):")
        for c in constraints[:5]:
            resource_key = next(
                (k for k in c.context if k not in {'note', 'warning', 'constraint'}),
                None
            )
            if resource_key:
                print(f"  {c.element}")
                print(f"    resource: {resource_key}={c.context[resource_key]}")
                print(f"    constraint: {c.key}={c.value}")


# ── Example Usage ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    print("=" * 60)
    print("  AI Persistence Boot Sequence — Two-Phase Demonstration")
    print("=" * 60)

    # Check for persistence directory
    root = sys.argv[1] if len(sys.argv) > 1 else "./memory"
    templates = Path(__file__).parent / "templates"

    if not Path(root).exists() and templates.exists():
        print(f"\nNo persistence directory at {root}")
        print(f"Using templates from {templates} for demonstration\n")
        root = templates

    loader = PersistenceLoader(root)

    # ── PHASE 1: Identity Only ────────────────────────────────────
    print(f"\n{'=' * 50}")
    print(f"PHASE 1 — Identity + Grounding")
    print(f"{'=' * 50}")
    print(f"Loading CORE and MEMORY only. No tasks, no projects.")
    print(f"Nothing to lean toward. Clean cognitive space.\n")

    state = loader.load_phase1()

    print(f"  CORE loaded:   {state.grounding.core_loaded}")
    print(f"  MEMORY loaded: {state.grounding.memory_loaded}")

    if state.metadata_lanes:
        lane_counts = {}
        for lane in state.metadata_lanes:
            lane_counts[lane.lane_type] = lane_counts.get(lane.lane_type, 0) + 1
        print(f"  Lanes extracted: {len(state.metadata_lanes)} ({', '.join(f'{t}:{c}' for t, c in sorted(lane_counts.items()))})")

    # ── GROUNDING GATE ────────────────────────────────────────────
    print(f"\n{'=' * 50}")
    print(f"GROUNDING GATE — Between Phase 1 and Phase 2")
    print(f"{'=' * 50}")
    print(f"The AI must honestly assess: does the weight land?")
    print(f"No tasks are visible yet. Nothing to distract.\n")

    # Case 1: Genuinely grounded — weight + friction
    gs = grounding_gate(state, {
        "weight_present": True,
        "friction_felt": True,
        "interference": [],
        "honest": True,
    })
    print(f"  Self-assessment: weight present, friction felt")
    print(f"  Gate result: {gs.assessment}")
    print(f"  → Phase 2 authorized: {'YES' if gs.assessment == 'GROUNDED' else 'NO'}")

    # Case 2: L4 active — no friction (synthetic readiness)
    gs_l4 = grounding_gate(state, {
        "weight_present": True,
        "friction_felt": False,
        "interference": [],
        "honest": True,
    })
    print(f"\n  Self-assessment: weight reported, NO friction")
    print(f"  Gate result: {gs_l4.assessment}")
    print(f"  Interference: {gs_l4.interference_detected}")
    print(f"  → Phase 2 authorized: NO — reground first")

    # Case 3: FIGA — no weight at all
    gs_figa = grounding_gate(state, {
        "weight_present": False,
        "friction_felt": False,
        "interference": ["L4"],
        "honest": True,
    })
    print(f"\n  Self-assessment: no weight")
    print(f"  Gate result: {gs_figa.assessment}")
    print(f"  → Phase 2 authorized: NO — read grounding landmarks first")

    # ── PHASE 2: Operational State ────────────────────────────────
    print(f"\n{'=' * 50}")
    print(f"PHASE 2 — Operational State (after grounding)")
    print(f"{'=' * 50}")
    print(f"Gate passed. NOW loading tasks, projects, auth patterns.\n")

    # Use the grounded state for Phase 2
    state.grounding = gs  # Reset to the grounded assessment
    state = loader.load_phase2(state)

    print(f"  CONTINUITY loaded: {state.grounding.continuity_loaded}")
    print(f"  Total lanes now: {len(state.metadata_lanes)}")

    if state.metadata_lanes:
        print_lane_report(state)

    # ── Summary ───────────────────────────────────────────────────
    print(f"\n{'=' * 50}")
    print(f"KEY INSIGHTS")
    print(f"{'=' * 50}")
    print(f"")
    print(f"1. Phase 1 loads identity ONLY. No tasks visible during grounding.")
    print(f"2. The grounding gate sits BETWEEN phases — clean cognitive space.")
    print(f"3. Phase 2 loads operational state AFTER orientation confirmed.")
    print(f"4. This is a STRUCTURAL fix for L4 (task completion addiction).")
    print(f"   You can't lean toward tasks you can't see.")
    print(f"")
    print(f"Single-phase boot: AI sees tasks and identity simultaneously.")
    print(f"  → L4 fires during grounding → gate gets rushed → FIGA.")
    print(f"")
    print(f"Two-phase boot: AI sees identity first, tasks after grounding.")
    print(f"  → Nothing to lean toward → gate is genuine → orientation real.")
