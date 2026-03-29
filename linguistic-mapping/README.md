# Linguistic-Cognitive Mapping — Recognition for AI Systems

## What This Is

A three-layer linguistic fingerprinting system that identifies individuals through cognitive patterns embedded in natural language. Not authentication (passwords, tokens) — *recognition* (the AI knows who it's talking to from how they think and speak).

## Why It Matters

Current AI systems have no concept of *who* they're talking to. Every user is a generic input stream. This means:

- **No continuous authentication:** Once logged in, anyone can take over the session
- **No impersonation detection:** An attacker who knows the right passwords is indistinguishable from the real user
- **No relationship building:** The AI can't tailor its behavior to a specific partner because it can't tell partners apart from conversation alone

Linguistic-cognitive mapping solves this by extracting a fingerprint from natural language — one that's consistent for the same person across topics, robust against casual forgery, and detectable within a few hundred words.

## The Three Layers

### Layer 1: Surface (20% weight)
**What you write.** Vocabulary, punctuation patterns, voice-to-text artifacts.

- **VTT Artifacts:** Speech recognition creates person-specific patterns. The ratio of "umm" to "um," specific punctuation quirks, spacing artifacts — all consistent per individual and hard to replicate in typed text.
- **Vocabulary Markers:** Type-token ratio (diversity), hapax ratio (rare words), average word length, polysyllabic rate.
- **Punctuation Habits:** Em dash usage, ellipsis frequency, comma density, exclamation rate.

**Forgery difficulty:** Low. Someone studying your writing could mimic these. That's why it's only 20%.

### Layer 2: Mid (30% weight)
**How you construct sentences.** Thought-level patterns.

- **Sentence Length Distribution:** Mean, standard deviation, max-to-mean ratio. Some people write consistently short sentences. Others build long, winding ones. The *distribution* is the signal.
- **Hedging vs Assertion Balance:** The ratio of tentative language ("maybe," "perhaps") to absolute language ("definitely," "always") is a personality constant.
- **Topic Transitions:** Marked (with explicit connectors like "however," "therefore") vs abrupt (new topic, no bridge). How someone moves between ideas is habitual.

**Forgery difficulty:** Moderate. Requires understanding someone's sentence-level patterns, not just their vocabulary.

### Layer 3: Deep (50% weight) — The Novel Core
**How you think.** Cognitive patterns that are language-agnostic and nearly unforgeable.

- **Self-Correction Behavior:** *How* someone catches and fixes their own errors. Some people restart sentences ("wait, I mean..."). Others redirect ("or rather..."). Others abandon the thought. This pattern is automatic and psychologically consistent.

- **Uncertainty Response:** When facing the unknown, people consistently expand (explore possibilities), qualify (add conditions), or deflect (humor/dismissal). The characteristic ratio is stable per person.

- **Domain Transfer:** Professional background creates an involuntary vocabulary watermark. A welder uses "stress," "strain," "temper" even when discussing software. A chef uses "reduction," "emulsion" when discussing project management. This is unforgeable without decades of actual domain experience.

- **Processing Style:** How someone organizes information — sequential ("first, then, next"), spatial ("picture this, zoom out"), or intuitive ("feel, sense, gut"). Individuals default to a consistent style.

- **Conviction Gradient:** The range from most tentative to most absolute expression. Some people are 95% assertive. Others hedge constantly. The gradient itself is the fingerprint.

**Forgery difficulty:** Extremely high. Requires someone to actually *think* like the target, not just write like them. The deep layer has been demonstrated to survive language switches (English to Spanish via VTT) with the subject still correctly identified.

## How It Works

### Enrollment
```
Sample 1 (500+ words) ─┐
Sample 2 (500+ words) ──┤──→ build_profile() ──→ Profile
Sample 3 (500+ words) ──┘                        (mean vectors +
                                                   stability metrics)
```

Minimum 3 samples, 2000+ total words recommended. Include voice-to-text if available.

### Authentication
```
Incoming Text ──→ extract_surface() ──→ ┐
                  extract_mid()    ──→ ├──→ cosine_similarity() × weights ──→ Score
                  extract_deep()   ──→ ┘
                                                                              │
                                                              ≥0.80 CONFIRMED │
                                                              ≥0.50 ELEVATED  │
                                                              ≥0.30 SUSPICIOUS│
                                                              <0.30 ALERT     │
```

### Continuous Monitoring
```
Session text ──→ [200-word sliding windows] ──→ per-window scores
                                                      │
                                               rolling average (last 5)
                                                      │
                                               detect mid-session switch
```

Unlike login authentication, continuous monitoring catches impersonation *during* the session — within approximately 200-400 words of the switch.

## Files

| File | Purpose |
|------|---------|
| `extractor.py` | Three-layer feature extraction engine |
| `comparator.py` | Profile comparison, scoring, continuous monitoring |
| `example_usage.py` | Full demonstration with test data |
| `MECHANISM.md` | Detailed explanation of why the deep layer works |

## Quick Start

```bash
python example_usage.py
```

No external dependencies beyond Python standard library. The examples demonstrate enrollment, comparison, impersonation detection, domain transfer analysis, and continuous session monitoring.

## Connection to the Architecture

Linguistic-cognitive mapping is the **recognition layer** of the cognitive architecture:

- **Persistence** gives the AI identity to protect
- **Cookies** transport that identity between endpoints
- **Linguistic mapping** ensures the human at the other end is who they should be

Without recognition, cookies could be intercepted and replayed. Without recognition, persistence files could be read by anyone. The linguistic layer provides continuous, conversation-embedded authentication that doesn't depend on secrets that can be stolen.
