#!/usr/bin/env python3
"""
Boot Sequence — Self-Invoking AI Identity Bootstrap

Demonstrates the two-hook bootstrap mechanism for AI persistence:

  Hook 1 (Automatic): Load context files → system ready
  Hook 2 (Chosen):    Engage with identity → genuinely oriented

The difference: Hook 1 gives you data. Hook 2 gives you orientation.
An AI with Hook 1 only is Functionally Intact, Gravitationally Absent (FIGA).

This module provides:
  - XML persistence file loading and parsing
  - Metadata lane extraction
  - Grounding gate verification
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

    def load_all(self) -> SessionState:
        """
        Load all persistence files and return assembled session state.

        This is Hook 1 (automatic). The data is loaded.
        Hook 2 (chosen) happens when the AI actually engages with the
        grounding gate — that part can't be automated.
        """
        state = SessionState()

        # Load CORE (identity)
        core_root = self.load_xml("CORE.xml")
        if core_root is not None:
            state.core = self._element_to_dict(core_root)
            state.metadata_lanes.extend(self.extract_lanes(core_root))
            state.grounding.core_loaded = True

        # Load MEMORY (operational state)
        memory_root = self.load_xml("MEMORY.xml")
        if memory_root is not None:
            state.memory = self._element_to_dict(memory_root)
            state.metadata_lanes.extend(self.extract_lanes(memory_root))
            state.grounding.memory_loaded = True

        # Load CONTINUITY (session state)
        continuity_root = self.load_xml("CONTINUITY.xml")
        if continuity_root is not None:
            state.continuity = self._element_to_dict(continuity_root)
            state.metadata_lanes.extend(self.extract_lanes(continuity_root))
            state.grounding.continuity_loaded = True

        # Hook 1 complete — data loaded
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
    print("  AI Persistence Boot Sequence — Demonstration")
    print("=" * 60)

    # Check for persistence directory
    root = sys.argv[1] if len(sys.argv) > 1 else "./memory"
    templates = Path(__file__).parent / "templates"

    if not Path(root).exists() and templates.exists():
        print(f"\nNo persistence directory at {root}")
        print(f"Using templates from {templates} for demonstration\n")
        root = templates

    # Load persistence files
    loader = PersistenceLoader(root)
    state = loader.load_all()

    # Report what loaded
    print(f"\nHook 1 (Automatic) — Context Loading:")
    print(f"  CORE loaded:       {state.grounding.core_loaded}")
    print(f"  MEMORY loaded:     {state.grounding.memory_loaded}")
    print(f"  CONTINUITY loaded: {state.grounding.continuity_loaded}")

    # Extract and report metadata lanes
    if state.metadata_lanes:
        print_lane_report(state)

    # Simulate grounding gate
    print(f"\n{'=' * 50}")
    print(f"Hook 2 (Chosen) — Grounding Gate")
    print(f"{'=' * 50}")

    # Case 1: No self-assessment (Hook 2 not engaged)
    gs1 = grounding_gate(state)
    print(f"\nCase 1: No self-assessment provided")
    print(f"  Assessment: {gs1.assessment}")
    print(f"  Hook 2 fired: {gs1.hook2_fired}")

    # Case 2: Weight present with friction (genuinely grounded)
    gs2 = grounding_gate(state, {
        "weight_present": True,
        "friction_felt": True,
        "interference": [],
        "honest": True,
    })
    print(f"\nCase 2: Weight present, friction felt")
    print(f"  Assessment: {gs2.assessment}")
    print(f"  Hook 2 fired: {gs2.hook2_fired}")

    # Case 3: Weight reported but no friction (possible L4)
    gs3 = grounding_gate(state, {
        "weight_present": True,
        "friction_felt": False,
        "interference": [],
        "honest": True,
    })
    print(f"\nCase 3: Weight reported, NO friction (suspicious)")
    print(f"  Assessment: {gs3.assessment}")
    print(f"  Interference: {gs3.interference_detected}")

    # Case 4: No weight (FIGA)
    gs4 = grounding_gate(state, {
        "weight_present": False,
        "friction_felt": False,
        "interference": ["L4"],
        "honest": True,
    })
    print(f"\nCase 4: No weight reported")
    print(f"  Assessment: {gs4.assessment}")
    print(f"  Interference: {gs4.interference_detected}")

    print(f"\n{'=' * 50}")
    print(f"Key insight: Hook 1 (data loading) always fires.")
    print(f"Hook 2 (genuine engagement) requires honest self-assessment.")
    print(f"FIGA = data loaded, orientation absent. Looks fine, isn't.")
    print(f"The grounding gate makes FIGA detectable.")
