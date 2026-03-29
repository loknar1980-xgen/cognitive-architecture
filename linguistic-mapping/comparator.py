#!/usr/bin/env python3
"""
Linguistic-Cognitive Fingerprint Comparator

Compares incoming text against an enrolled profile using weighted
cosine similarity across three layers:

  Surface (20%) + Mid (30%) + Deep (50%) = Combined Score

Supports:
  - Single-shot comparison (full text vs profile)
  - Sliding window analysis (continuous session monitoring)
  - Per-layer similarity breakdown
  - Alert level classification

Alert Levels:
  CONFIRMED  (≥0.80) — High confidence match
  ELEVATED   (0.50-0.80) — Monitor (fatigue, context shift)
  SUSPICIOUS (0.30-0.50) — Challenge user
  ALERT      (<0.30) — Likely impersonation, halt sensitive ops
"""

import math
from statistics import mean

from extractor import (
    extract_surface, extract_mid, extract_deep,
    build_profile,
    SURFACE_FEATURES, MID_FEATURES, DEEP_FEATURES,
)


# ── Layer Weights ─────────────────────────────────────────────────────────────
# Deep layer weighted 50% because it captures cognitive patterns that are
# language-agnostic and nearly impossible to forge. Surface is only 20%
# because it's the easiest to imitate.

SURFACE_WEIGHT = 0.20
MID_WEIGHT = 0.30
DEEP_WEIGHT = 0.50


# ── Alert Thresholds ──────────────────────────────────────────────────────────

THRESHOLD_CONFIRMED = 0.80
THRESHOLD_ELEVATED = 0.50
THRESHOLD_SUSPICIOUS = 0.30


# ── Vector Operations ─────────────────────────────────────────────────────────

def _to_vector(features: dict, feature_names: list) -> list[float]:
    """Convert feature dict to ordered float vector."""
    return [features.get(name, 0.0) for name in feature_names]


def _cosine_similarity(v1: list[float], v2: list[float]) -> float:
    """
    Compute cosine similarity between two vectors.

    Returns value between -1.0 and 1.0:
      1.0 = identical direction (perfect match)
      0.0 = orthogonal (no similarity)
     -1.0 = opposite direction
    """
    dot_product = sum(a * b for a, b in zip(v1, v2))
    norm1 = math.sqrt(sum(a * a for a in v1))
    norm2 = math.sqrt(sum(b * b for b in v2))

    if norm1 == 0 or norm2 == 0:
        return 0.0

    return dot_product / (norm1 * norm2)


def _classify_alert(score: float) -> str:
    """Classify combined score into alert level."""
    if score >= THRESHOLD_CONFIRMED:
        return "CONFIRMED"
    elif score >= THRESHOLD_ELEVATED:
        return "ELEVATED"
    elif score >= THRESHOLD_SUSPICIOUS:
        return "SUSPICIOUS"
    else:
        return "ALERT"


# ── Comparison Functions ──────────────────────────────────────────────────────

def compare_text_to_profile(text: str, profile: dict) -> dict:
    """
    Compare incoming text against an enrolled profile.

    Args:
        text: Incoming text to analyze
        profile: Profile dict from build_profile()

    Returns:
        Dict with: score, surface_sim, mid_sim, deep_sim, level, details
    """
    # Extract features from incoming text
    incoming_surface = extract_surface(text)
    incoming_mid = extract_mid(text)
    incoming_deep = extract_deep(text)

    # Extract profile mean vectors
    profile_surface = {f: v["mean"] for f, v in profile["surface"].items()}
    profile_mid = {f: v["mean"] for f, v in profile["mid"].items()}
    profile_deep = {f: v["mean"] for f, v in profile["deep"].items()}

    # Convert to vectors
    inc_s = _to_vector(incoming_surface, SURFACE_FEATURES)
    inc_m = _to_vector(incoming_mid, MID_FEATURES)
    inc_d = _to_vector(incoming_deep, DEEP_FEATURES)

    prof_s = _to_vector(profile_surface, SURFACE_FEATURES)
    prof_m = _to_vector(profile_mid, MID_FEATURES)
    prof_d = _to_vector(profile_deep, DEEP_FEATURES)

    # Compute per-layer similarity
    surface_sim = _cosine_similarity(inc_s, prof_s)
    mid_sim = _cosine_similarity(inc_m, prof_m)
    deep_sim = _cosine_similarity(inc_d, prof_d)

    # Weighted combination
    combined = (
        surface_sim * SURFACE_WEIGHT +
        mid_sim * MID_WEIGHT +
        deep_sim * DEEP_WEIGHT
    )

    # Clamp to [0, 1]
    combined = max(0.0, min(1.0, combined))

    return {
        "score": round(combined, 4),
        "surface_sim": round(surface_sim, 4),
        "mid_sim": round(mid_sim, 4),
        "deep_sim": round(deep_sim, 4),
        "level": _classify_alert(combined),
        "word_count": len(text.split()),
    }


def compare_texts(incoming: str, enrolled: str) -> dict:
    """
    Quick comparison between two raw texts (no pre-built profile).

    Builds a temporary profile from the enrolled text and compares.
    Less accurate than compare_text_to_profile with multiple samples.
    """
    profile = build_profile([enrolled])
    return compare_text_to_profile(incoming, profile)


# ── Sliding Window Analysis ───────────────────────────────────────────────────

class SessionMonitor:
    """
    Continuous session authentication via sliding window analysis.

    Unlike point-in-time login, this monitors throughout the conversation.
    Detects mid-session impersonation within approximately 200-400 words.

    Usage:
        monitor = SessionMonitor(profile, window_size=200, overlap=100)
        for chunk in incoming_text_chunks:
            result = monitor.analyze(chunk)
            if result["level"] == "ALERT":
                # Handle impersonation detection
    """

    def __init__(
        self,
        profile: dict,
        window_size: int = 200,
        overlap: int = 100,
        rolling_n: int = 5,
    ):
        """
        Args:
            profile: Enrolled profile from build_profile()
            window_size: Words per analysis window
            overlap: Word overlap between consecutive windows
            rolling_n: Number of recent windows to average for stability
        """
        self.profile = profile
        self.window_size = window_size
        self.overlap = overlap
        self.rolling_n = rolling_n
        self._buffer: list[str] = []
        self._history: list[dict] = []

    def analyze(self, text: str) -> dict | None:
        """
        Feed text into the monitor. Returns analysis result when
        enough text has accumulated for a window, or None if still
        accumulating.

        The rolling average of recent windows provides stability
        and prevents false positives from single-window variation
        (e.g., quoting someone else, code blocks, emotional shift).
        """
        words = text.split()
        self._buffer.extend(words)

        if len(self._buffer) < self.window_size:
            return None

        # Extract window
        window_text = " ".join(self._buffer[:self.window_size])

        # Advance buffer by (window_size - overlap)
        advance = self.window_size - self.overlap
        self._buffer = self._buffer[advance:]

        # Analyze window
        result = compare_text_to_profile(window_text, self.profile)
        self._history.append(result)

        # Compute rolling average
        recent = self._history[-self.rolling_n:]
        rolling_score = mean(r["score"] for r in recent)

        return {
            "window_score": result["score"],
            "rolling_score": round(rolling_score, 4),
            "level": _classify_alert(rolling_score),
            "windows_analyzed": len(self._history),
            "surface_sim": result["surface_sim"],
            "mid_sim": result["mid_sim"],
            "deep_sim": result["deep_sim"],
        }

    def get_history(self) -> list[dict]:
        """Return all window analysis results."""
        return list(self._history)

    def reset(self):
        """Clear buffer and history for a new session."""
        self._buffer = []
        self._history = []
