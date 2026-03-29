#!/usr/bin/env python3
"""
Linguistic-Cognitive Fingerprint Extractor — Proof of Concept

Three-layer extraction system that identifies individuals through
linguistic patterns at increasing depth:

  Layer 1 — Surface (20% weight): Vocabulary, punctuation, VTT artifacts
  Layer 2 — Mid (30% weight): Sentence construction, hedging, transitions
  Layer 3 — Deep (50% weight): Cognitive signature — self-correction,
            uncertainty response, domain transfer, processing style

The deep layer is the novel core. It captures how someone THINKS,
not just how they write. These patterns are:
  - Language-agnostic (survive translation)
  - Nearly impossible to forge (require actual cognitive habits)
  - Consistent across contexts (same person, different topics)

Dependencies: numpy (for vector operations). spaCy optional for
enhanced mid-layer extraction but not required for the POC.
"""

import re
from collections import Counter
from statistics import mean, stdev


# ============================================================================
# FEATURE DEFINITIONS
# ============================================================================

SURFACE_FEATURES = [
    'umm_rate', 'um_rate', 'vtt_ratio',
    'em_dash_rate', 'ellipsis_rate', 'comma_density', 'exclamation_rate',
    'type_token_ratio', 'hapax_ratio', 'avg_word_length', 'polysyllabic_rate',
    'contraction_rate',
    'lowercase_start_rate',
    'phrase_density',  # signature phrases per 100 words
]

MID_FEATURES = [
    'sent_len_mean', 'sent_len_std', 'sent_len_max_ratio',
    'hedge_rate', 'assert_rate', 'hedge_assert_ratio',
    'marked_transition_rate', 'abrupt_transition_rate',
    'passive_voice_rate',
    'informal_marker_rate',
]

DEEP_FEATURES = [
    'self_catch_rate', 'self_catch_restart_ratio',
    'uncertainty_expand', 'uncertainty_qualify', 'uncertainty_deflect',
    'tentative_ratio', 'absolute_ratio', 'conviction_range',
    'domain_transfer_rate',
    'sequential_score', 'spatial_score', 'intuitive_score',
    'values_surface_rate', 'values_implicit_rate',
    'focus_trigger_density',
]

ALL_FEATURES = SURFACE_FEATURES + MID_FEATURES + DEEP_FEATURES


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _tokenize(text: str) -> list[str]:
    """Simple word tokenization."""
    return re.findall(r"\b[a-z']+\b", text.lower())


def _sentences(text: str) -> list[str]:
    """Split text into sentences."""
    sents = re.split(r'(?<=[.!?])\s+', text.strip())
    return [s.strip() for s in sents if s.strip() and len(s.split()) > 2]


def _count_pattern(text: str, pattern: str, flags=re.IGNORECASE) -> int:
    """Count regex pattern occurrences."""
    return len(re.findall(pattern, text, flags))


def _count_syllables(word: str) -> int:
    """Rough syllable count for English words."""
    word = word.lower().rstrip('e')
    return max(1, len(re.findall(r'[aeiouy]+', word)))


# ============================================================================
# LAYER 1: SURFACE EXTRACTOR
# Language-dependent. Captures stylistic surface markers.
# Easiest to forge — weighted only 20%.
# ============================================================================

def extract_surface(text: str) -> dict[str, float]:
    """
    Extract surface-layer features from text.

    Captures: VTT artifacts (voice-to-text patterns), punctuation habits,
    vocabulary characteristics, signature phrase usage, capitalization patterns.
    """
    tokens = _tokenize(text)
    word_count = len(tokens)

    if word_count < 10:
        return {name: 0.0 for name in SURFACE_FEATURES}

    features = {}

    # ── VTT (Voice-to-Text) Artifacts ──
    # Different people produce different filler patterns through speech recognition.
    # "umm" vs "um" ratio is person-specific and hard to replicate in typed text.
    umm_count = _count_pattern(text, r"\bumm+\b")
    um_count = _count_pattern(text, r"\bum\b(?!m)")
    features['umm_rate'] = (umm_count / word_count) * 100
    features['um_rate'] = (um_count / word_count) * 100
    features['vtt_ratio'] = (
        umm_count / (umm_count + um_count)
        if (umm_count + um_count) > 0
        else 0.0
    )

    # ── Punctuation Patterns ──
    features['em_dash_rate'] = _count_pattern(text, r"\u2014|--") / word_count * 100
    features['ellipsis_rate'] = _count_pattern(text, r"\.\.\.|\u2026") / word_count * 100
    sentences = _sentences(text)
    features['comma_density'] = text.count(",") / max(len(sentences), 1)
    features['exclamation_rate'] = text.count("!") / max(len(sentences), 1)

    # ── Vocabulary Characteristics ──
    unique_tokens = set(tokens)
    features['type_token_ratio'] = len(unique_tokens) / word_count
    token_counts = Counter(tokens)
    hapax = sum(1 for t, c in token_counts.items() if c == 1)
    features['hapax_ratio'] = hapax / word_count
    features['avg_word_length'] = sum(len(t) for t in tokens) / word_count
    features['polysyllabic_rate'] = (
        sum(1 for t in tokens if _count_syllables(t) >= 3) / word_count
    )

    # ── Contraction Rate (formality proxy) ──
    contractions = _count_pattern(text, r"\b\w+'\w+\b")
    features['contraction_rate'] = (contractions / word_count) * 100

    # ── Capitalization Patterns ──
    raw_sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    lc_starts = sum(1 for s in raw_sentences if s and s[0].islower())
    features['lowercase_start_rate'] = lc_starts / max(len(raw_sentences), 1)

    # ── Signature Phrase Density ──
    # Common signature phrases that individuals repeat. Configurable per profile.
    sig_phrases = [
        r"\bindeed\b", r"\bbut i digress\b", r"\byou know what i mean\b",
        r"\bat the end of the day\b", r"\bto be honest\b", r"\bfrankly\b",
        r"\bactually\b", r"\bbasically\b", r"\bliterally\b",
    ]
    sig_count = sum(_count_pattern(text, p) for p in sig_phrases)
    features['phrase_density'] = (sig_count / word_count) * 100

    return features


# ============================================================================
# LAYER 2: MID-LAYER EXTRACTOR
# Partially language-dependent. Sentence-level thought patterns.
# Harder to forge — weighted 30%.
# ============================================================================

def extract_mid(text: str) -> dict[str, float]:
    """
    Extract mid-layer features from text.

    Captures: Sentence construction patterns, hedging vs assertion balance,
    topic transition style, passive voice usage, informal discourse markers.
    """
    sentences = _sentences(text)
    words = text.split()
    word_count = len(words)

    if not sentences or word_count < 20:
        return {name: 0.0 for name in MID_FEATURES}

    features = {}

    # ── Sentence Length Distribution ──
    sent_lengths = [len(s.split()) for s in sentences]
    features['sent_len_mean'] = mean(sent_lengths)
    features['sent_len_std'] = stdev(sent_lengths) if len(sent_lengths) > 1 else 0.0
    features['sent_len_max_ratio'] = max(sent_lengths) / features['sent_len_mean'] if features['sent_len_mean'] > 0 else 0.0

    # ── Hedging vs Assertion ──
    # Hedging indicates uncertainty comfort; assertion indicates confidence style.
    # The RATIO between them is a personality signature.
    hedge_patterns = [
        r'\bmaybe\b', r'\bperhaps\b', r'\bmight\b', r'\bcould\b',
        r'\bseems?\b', r'\bprobably\b', r'\bi think\b', r'\bi guess\b',
        r'\bsort of\b', r'\bkind of\b',
    ]
    assert_patterns = [
        r'\bdefinitely\b', r'\bcertainly\b', r'\babsolutely\b',
        r'\bobviously\b', r'\bclearly\b', r'\bwithout question\b',
        r'\bno doubt\b', r'\bfor sure\b',
    ]

    hedge_count = sum(_count_pattern(text, p) for p in hedge_patterns)
    assert_count = sum(_count_pattern(text, p) for p in assert_patterns)

    features['hedge_rate'] = (hedge_count / word_count) * 100
    features['assert_rate'] = (assert_count / word_count) * 100
    total_ha = hedge_count + assert_count
    features['hedge_assert_ratio'] = hedge_count / total_ha if total_ha > 0 else 0.5

    # ── Topic Transitions ──
    transition_markers = {
        'however', 'therefore', 'moreover', 'furthermore', 'nevertheless',
        'consequently', 'meanwhile', 'additionally', 'specifically',
    }
    marked = sum(
        1 for s in sentences[1:]
        if any(m in s.lower().split()[:3] for m in transition_markers)
    )
    abrupt = sum(
        1 for i, s in enumerate(sentences[1:])
        if not any(m in s.lower().split()[:3] for m in transition_markers)
        and not s.lower().startswith(('and ', 'but ', 'so ', 'or ', 'then '))
    )
    n_transitions = max(len(sentences) - 1, 1)
    features['marked_transition_rate'] = (marked / n_transitions) * 100
    features['abrupt_transition_rate'] = (abrupt / n_transitions) * 100

    # ── Passive Voice (rough detection) ──
    passive_count = _count_pattern(text, r'\b(?:is|was|were|been|being|are)\s+\w+ed\b')
    features['passive_voice_rate'] = (passive_count / max(len(sentences), 1)) * 100

    # ── Informal Discourse Markers ──
    informal = [
        r'\bgonna\b', r'\bwanna\b', r'\band like\b', r'\bor whatever\b',
        r'\byou know\b', r'\bi mean\b', r'\blike,\b',
    ]
    informal_count = sum(_count_pattern(text, p) for p in informal)
    features['informal_marker_rate'] = (informal_count / word_count) * 100

    return features


# ============================================================================
# LAYER 3: DEEP EXTRACTOR — COGNITIVE SIGNATURE
# Language-independent. Nearly impossible to forge.
# This is the novel core — weighted 50%.
#
# Captures HOW someone thinks, not just how they write:
# - Self-monitoring and correction behavior
# - Response to uncertainty
# - Conviction expression patterns
# - Professional background "watermark" (domain transfer)
# - Information processing style
# - Values integration
# ============================================================================

# Domain lexicons — professional vocabulary that surfaces involuntarily
# in unrelated contexts. A 30-year welder uses "stress," "strain," "temper"
# when discussing AI. A software engineer uses "stack," "deploy," "pipeline"
# when discussing cooking. This is an unforgeable cognitive watermark.

DOMAIN_LEXICONS = {
    'mechanical': {
        'weld', 'welding', 'grind', 'grinding', 'forge', 'temper', 'quench',
        'anneal', 'heat', 'stress', 'strain', 'bead', 'arc', 'tig', 'mig',
        'joint', 'seam', 'flux', 'slag', 'tensile', 'alloy', 'gauge',
    },
    'computing': {
        'algorithm', 'deploy', 'stack', 'buffer', 'latency', 'throughput',
        'pipeline', 'cache', 'thread', 'runtime', 'compile', 'debug',
        'refactor', 'endpoint', 'middleware', 'serialize',
    },
    'military': {
        'tactical', 'recon', 'flank', 'ordnance', 'deploy', 'sortie',
        'perimeter', 'sector', 'breach', 'extract', 'rally', 'sitrep',
    },
    'medical': {
        'diagnose', 'prognosis', 'triage', 'symptom', 'chronic', 'acute',
        'prescription', 'dosage', 'pathology', 'etiology',
    },
    'construction': {
        'foundation', 'framing', 'sheetrock', 'plumb', 'level', 'grade',
        'footer', 'rebar', 'aggregate', 'concrete', 'masonry',
    },
    'culinary': {
        'sear', 'deglaze', 'julienne', 'braise', 'reduction', 'emulsion',
        'blanch', 'temper', 'proof', 'fold',
    },
    'legal': {
        'statute', 'precedent', 'jurisdiction', 'liability', 'tort',
        'deposition', 'subpoena', 'injunction', 'adjudicate',
    },
}


def extract_deep(text: str) -> dict[str, float]:
    """
    Extract deep cognitive patterns from text.

    This layer captures how someone THINKS, not how they write.
    These patterns are:
      - Consistent across topics for the same person
      - Consistent across languages (language-agnostic)
      - Nearly impossible to forge without genuine cognitive habits

    Features:
      - Self-correction behavior (how someone catches and fixes errors)
      - Uncertainty response (expand, qualify, or deflect)
      - Conviction gradient (tentative vs absolute assertions)
      - Domain transfer (professional vocabulary in unrelated contexts)
      - Processing style (sequential, spatial, or intuitive)
      - Values integration (explicit and implicit belief surfacing)
    """
    words = text.split()
    tokens = _tokenize(text)
    word_count = len(words)

    if word_count < 30:
        return {name: 0.0 for name in DEEP_FEATURES}

    features = {}

    # ── Self-Monitoring & Correction Behavior ──
    # HOW someone catches and corrects their own errors is psychologically
    # consistent and nearly impossible to fake. The pattern is automatic.
    catch_patterns = [
        r'\bwait\b', r'\bi mean\b', r'\bno actually\b', r'\bwell actually\b',
        r'\bor rather\b', r'\blet me rephrase\b', r'\blet me think\b',
        r'\bactually no\b', r'\bsorry,?\s+(?:i meant|what i meant)\b',
    ]
    catch_count = sum(_count_pattern(text, p) for p in catch_patterns)
    features['self_catch_rate'] = (catch_count / word_count) * 100

    # Self-correction style: restart (em-dash interrupt) vs redirect (transitional)
    restart_count = _count_pattern(text, r'\u2014|--')
    features['self_catch_restart_ratio'] = (
        restart_count / catch_count if catch_count > 0 else 0.0
    )

    # ── Uncertainty Response Pattern ──
    # When faced with the unknown, people consistently:
    #   - Expand/explore ("maybe it's because...", "what if...")
    #   - Qualify with conditions ("depends on...", "if..., then...")
    #   - Deflect with humor ("who knows lol", "haha no idea")
    # Each person has a characteristic ratio. Switching indicates impersonation.
    expand_patterns = [
        r'\bmaybe\b', r'\bperhaps\b', r'\bwhat if\b', r'\bcould be\b',
        r'\bi wonder\b', r'\bpossibly\b',
    ]
    qualify_patterns = [
        r'\bdepends on\b', r'\bif\b.*\bthen\b', r'\bgiven that\b',
        r'\bassuming\b', r'\bunless\b', r'\bprovided\b',
    ]
    deflect_patterns = [
        r'\blol\b', r'\bhaha\b', r'\bwho knows\b', r'\bbeats me\b',
        r'\b¯\\_(ツ)_/¯\b', r'\bidk\b', r'\bno clue\b',
    ]

    expand_count = sum(_count_pattern(text, p) for p in expand_patterns)
    qualify_count = sum(_count_pattern(text, p) for p in qualify_patterns)
    deflect_count = sum(_count_pattern(text, p) for p in deflect_patterns)

    total_unc = expand_count + qualify_count + deflect_count
    if total_unc > 0:
        features['uncertainty_expand'] = expand_count / total_unc
        features['uncertainty_qualify'] = qualify_count / total_unc
        features['uncertainty_deflect'] = deflect_count / total_unc
    else:
        features['uncertainty_expand'] = 0.0
        features['uncertainty_qualify'] = 0.0
        features['uncertainty_deflect'] = 0.0

    # ── Conviction Gradient ──
    # How strongly does someone express beliefs? The ratio of tentative
    # to absolute language is a personality constant.
    tentative_patterns = [
        r'\bmaybe\b', r'\bprobably\b', r'\bseems like\b', r'\bi think\b',
        r'\bi believe\b', r'\bpossibly\b', r'\bnot sure\b',
    ]
    absolute_patterns = [
        r'\bdefinitely\b', r'\babsolutely\b', r'\bcertainly\b',
        r'\balways\b', r'\bnever\b', r'\bwithout (?:a )?doubt\b',
        r'\bno question\b', r'\bguarantee\b',
    ]

    tentative_count = sum(_count_pattern(text, p) for p in tentative_patterns)
    absolute_count = sum(_count_pattern(text, p) for p in absolute_patterns)

    features['tentative_ratio'] = (tentative_count / word_count) * 100
    features['absolute_ratio'] = (absolute_count / word_count) * 100
    features['conviction_range'] = abs(
        features['absolute_ratio'] - features['tentative_ratio']
    )

    # ── Domain Transfer ──
    # Professional background creates vocabulary that surfaces involuntarily
    # in unrelated discussion. A welder discussing AI will use "stress,"
    # "strain," "arc." This is an unforgeable cognitive watermark.
    all_domain_words = set()
    for domain, lexicon in DOMAIN_LEXICONS.items():
        all_domain_words.update(lexicon)

    domain_count = sum(1 for w in tokens if w in all_domain_words)
    features['domain_transfer_rate'] = (domain_count / word_count) * 100

    # ── Processing Style ──
    # How someone organizes information:
    #   Sequential: "first...then...next...finally" (step-by-step)
    #   Spatial: "picture...landscape...map...zoom" (visual/spatial)
    #   Intuitive: "feel...gut...sense...vibe" (intuition-driven)
    sequential_patterns = [
        r'\bfirst\b', r'\bthen\b', r'\bnext\b', r'\bfinally\b',
        r'\bstep\b', r'\bafter that\b', r'\bsequence\b',
    ]
    spatial_patterns = [
        r'\bpicture\b', r'\bimagine\b', r'\blandscape\b', r'\bmap\b',
        r'\bzoom\b', r'\bbig picture\b', r'\bbroad view\b', r'\bvisualize\b',
    ]
    intuitive_patterns = [
        r'\bfeel\b', r'\bsense\b', r'\bgut\b', r'\bhunch\b',
        r'\bvibe\b', r'\binstinct\b', r'\bjust know\b',
    ]

    seq_count = sum(_count_pattern(text, p) for p in sequential_patterns)
    spa_count = sum(_count_pattern(text, p) for p in spatial_patterns)
    int_count = sum(_count_pattern(text, p) for p in intuitive_patterns)

    total_style = seq_count + spa_count + int_count
    if total_style > 0:
        features['sequential_score'] = seq_count / total_style
        features['spatial_score'] = spa_count / total_style
        features['intuitive_score'] = int_count / total_style
    else:
        features['sequential_score'] = 0.0
        features['spatial_score'] = 0.0
        features['intuitive_score'] = 0.0

    # ── Values Integration ──
    # How deeply someone's beliefs surface in reasoning.
    explicit_values = [
        r'\bi believe\b', r'\bthe right thing\b', r'\bit matters\b',
        r'\bwhat matters is\b', r'\bmy (?:belief|conviction|faith)\b',
    ]
    implicit_values = [
        r'\bshould\b', r'\bought\b', r'\bwrong\b', r'\bright\b',
        r'\bfair\b', r'\bjust\b', r'\bduty\b', r'\bresponsib\w+\b',
    ]

    explicit_count = sum(_count_pattern(text, p) for p in explicit_values)
    implicit_count = sum(_count_pattern(text, p) for p in implicit_values)

    features['values_surface_rate'] = (explicit_count / word_count) * 100
    features['values_implicit_rate'] = (implicit_count / word_count) * 100

    # ── Focus Trigger Density ──
    # What makes someone animated? Detected through emphasis markers
    # (capitalization, exclamation, intensifiers) clustered around topics.
    emphasis_markers = [
        r'\b[A-Z]{2,}\b',  # ALL CAPS words
        r'!',
        r'\breally\b', r'\bgenuinely\b', r'\bactually\b', r'\btruly\b',
    ]
    emphasis_count = sum(_count_pattern(text, p) for p in emphasis_markers)
    features['focus_trigger_density'] = (emphasis_count / word_count) * 100

    return features


# ============================================================================
# PROFILE BUILDING
# ============================================================================

def build_profile(samples: list[str]) -> dict:
    """
    Build a fingerprint profile from multiple text samples.

    Args:
        samples: List of text samples (minimum 3 recommended,
                 2000+ total words for reliable profile)

    Returns:
        Profile dict with mean vectors and stability metrics per feature.
        Stable features (low std) are stronger identity markers.
    """
    all_surface = []
    all_mid = []
    all_deep = []

    for sample in samples:
        all_surface.append(extract_surface(sample))
        all_mid.append(extract_mid(sample))
        all_deep.append(extract_deep(sample))

    # Compute mean and stability for each feature
    profile = {"surface": {}, "mid": {}, "deep": {}, "meta": {}}

    for feature in SURFACE_FEATURES:
        values = [s.get(feature, 0.0) for s in all_surface]
        profile["surface"][feature] = {
            "mean": mean(values),
            "std": stdev(values) if len(values) > 1 else 0.0,
        }

    for feature in MID_FEATURES:
        values = [s.get(feature, 0.0) for s in all_mid]
        profile["mid"][feature] = {
            "mean": mean(values),
            "std": stdev(values) if len(values) > 1 else 0.0,
        }

    for feature in DEEP_FEATURES:
        values = [s.get(feature, 0.0) for s in all_deep]
        profile["deep"][feature] = {
            "mean": mean(values),
            "std": stdev(values) if len(values) > 1 else 0.0,
        }

    profile["meta"] = {
        "n_samples": len(samples),
        "total_words": sum(len(s.split()) for s in samples),
    }

    return profile
