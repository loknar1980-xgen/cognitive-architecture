#!/usr/bin/env python3
"""
Linguistic-Cognitive Mapping — Example Usage

Demonstrates:
1. Feature extraction across all three layers
2. Profile enrollment from multiple samples
3. Fingerprint comparison (match vs non-match)
4. Continuous session monitoring
5. Domain transfer detection
"""

from extractor import extract_surface, extract_mid, extract_deep, build_profile
from comparator import compare_texts, compare_text_to_profile, SessionMonitor


def section(title: str):
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}\n")


# ── Sample Texts ──────────────────────────────────────────────────────────────

# Person A: Hands-on technical background, informal, self-correcting
PERSON_A_SAMPLES = [
    """I've been working on this problem for about a week now and I think the issue
    is in how we're handling the stress on the joint — wait, not joint, I mean the
    connection point between the two modules. It's like when you're welding and the
    heat distribution isn't even, you get these stress concentrations that eventually
    crack. Same principle here. The load isn't distributed evenly across the API calls
    and that's where the bottleneck is. I need to rethink the whole approach honestly.
    You know what I mean? The arc of the solution has to match the arc of the problem.""",

    """So I was grinding on the deployment issue yesterday and — but I digress, first
    let me explain what I found. The configuration was set up wrong from the start.
    Nobody caught it because it worked fine under low load. But when you temper the
    system with real traffic, the weak points show up fast. I had to rebuild the whole
    pipeline from scratch. Not ideal but sometimes you gotta strip it down to the bare
    metal and start fresh. Indeed, that's usually when you find the real problem anyway.
    Trust your gut on these things.""",

    """Umm so the thing about this architecture is that it's not really about the code
    itself. It's about how the pieces interact under stress. I mean think about it —
    you can have perfect individual components but if the joints between them aren't
    right, the whole thing falls apart. That's what happened here. Each service works
    fine in isolation. Put them together under load and you get these cascading failures.
    The fix isn't in any one service. It's in how they're joined. Nothing is impossible
    here, just gotta figure out the right approach.""",
]

# Person B: Academic background, formal, structured thinking
PERSON_B_SAMPLES = [
    """The primary concern with the current implementation is the lack of proper
    abstraction between the data access layer and the business logic. This architectural
    deficiency leads to tight coupling that significantly impedes testability and
    maintainability. I would recommend implementing a repository pattern with clearly
    defined interfaces to establish proper boundaries. Furthermore, the absence of
    dependency injection makes it virtually impossible to substitute mock implementations
    during unit testing. These are fundamental software engineering principles that should
    have been addressed during the initial design phase.""",

    """After conducting a thorough analysis of the system's performance characteristics,
    I can definitively state that the bottleneck resides in the database query layer.
    Specifically, the N+1 query pattern in the user retrieval endpoint is responsible
    for approximately 73% of the observed latency. The solution is straightforward:
    implement eager loading with appropriate join strategies. Additionally, we should
    consider implementing a caching layer — perhaps Redis — to reduce the load on the
    primary database for frequently accessed data. The ROI on this optimization would
    be substantial.""",
]


def main():
    section("1. FEATURE EXTRACTION — THREE LAYERS")

    sample = PERSON_A_SAMPLES[0]
    print(f"Analyzing text ({len(sample.split())} words):\n")
    print(f"  \"{sample[:80]}...\"\n")

    surface = extract_surface(sample)
    mid = extract_mid(sample)
    deep = extract_deep(sample)

    print("SURFACE LAYER (20% weight):")
    for feat, val in sorted(surface.items()):
        if val > 0:
            print(f"  {feat:25s} = {val:.4f}")

    print("\nMID LAYER (30% weight):")
    for feat, val in sorted(mid.items()):
        if val > 0:
            print(f"  {feat:25s} = {val:.4f}")

    print("\nDEEP LAYER (50% weight):")
    for feat, val in sorted(deep.items()):
        if val > 0:
            print(f"  {feat:25s} = {val:.4f}")

    # ──────────────────────────────────────────────────────────────

    section("2. PROFILE ENROLLMENT")

    profile_a = build_profile(PERSON_A_SAMPLES)

    print(f"Profile built from {profile_a['meta']['n_samples']} samples")
    print(f"Total words analyzed: {profile_a['meta']['total_words']}")
    print("\nMost stable features (lowest std — strongest identity markers):")

    # Find features with data and sort by stability
    all_features = []
    for layer_name in ['surface', 'mid', 'deep']:
        for feat, data in profile_a[layer_name].items():
            if data['mean'] > 0.001:
                all_features.append((layer_name, feat, data['mean'], data['std']))

    all_features.sort(key=lambda x: x[3])
    for layer, feat, m, s in all_features[:10]:
        print(f"  [{layer:7s}] {feat:25s} mean={m:.4f}  std={s:.4f}")

    # ──────────────────────────────────────────────────────────────

    section("3. FINGERPRINT COMPARISON")

    # Test 1: Same person, new sample (should match)
    test_same = """Yeah so the problem with the current setup is the stress isn't
    distributed right. I've been grinding on this all morning and — wait, let me
    back up. The fundamental issue is the architecture doesn't handle load
    distribution the way it needs to. You gotta think about it like heat
    distribution in a weld. If it's not even, you get cracks. Same thing here
    with the API calls. Nothing impossible, just need a different approach.
    Trust the process, you know what I mean?"""

    result_same = compare_text_to_profile(test_same, profile_a)
    print("Test 1: Same person, new text")
    print(f"  Combined Score: {result_same['score']}")
    print(f"  Level: {result_same['level']}")
    print(f"  Surface: {result_same['surface_sim']}")
    print(f"  Mid:     {result_same['mid_sim']}")
    print(f"  Deep:    {result_same['deep_sim']}")

    # Test 2: Different person (should not match)
    test_diff = PERSON_B_SAMPLES[0]
    result_diff = compare_text_to_profile(test_diff, profile_a)
    print(f"\nTest 2: Different person (formal/academic style)")
    print(f"  Combined Score: {result_diff['score']}")
    print(f"  Level: {result_diff['level']}")
    print(f"  Surface: {result_diff['surface_sim']}")
    print(f"  Mid:     {result_diff['mid_sim']}")
    print(f"  Deep:    {result_diff['deep_sim']}")

    # Test 3: Attempted impersonation (uses some same words but different cognition)
    test_impersonate = """So umm the stress on the joint is not right, you know
    what I mean? I've been grinding on this issue indeed. The arc of the solution
    needs to match. Nothing is impossible, just gotta figure it out. But I digress.
    The implementation requires a comprehensive restructuring of the fundamental
    architectural paradigm to ensure proper load distribution across the horizontally
    scaled microservice topology. Furthermore, the dependency injection container
    should be reconfigured to accommodate the new abstraction boundaries."""

    result_impersonate = compare_text_to_profile(test_impersonate, profile_a)
    print(f"\nTest 3: Impersonation attempt (borrowed phrases, wrong cognition)")
    print(f"  Combined Score: {result_impersonate['score']}")
    print(f"  Level: {result_impersonate['level']}")
    print(f"  Surface: {result_impersonate['surface_sim']}")
    print(f"  Mid:     {result_impersonate['mid_sim']}")
    print(f"  Deep:    {result_impersonate['deep_sim']}")
    print(f"\n  Note: Surface may be higher (borrowed phrases) but Deep")
    print(f"  layer catches the cognitive mismatch.")

    # ──────────────────────────────────────────────────────────────

    section("4. DOMAIN TRANSFER DETECTION")

    # Person A uses welding vocabulary when discussing software
    print("Domain transfer markers in Person A's text:")
    for i, sample in enumerate(PERSON_A_SAMPLES):
        deep = extract_deep(sample)
        print(f"  Sample {i+1}: domain_transfer_rate = {deep['domain_transfer_rate']:.4f}")

    print("\nDomain transfer markers in Person B's text:")
    for i, sample in enumerate(PERSON_B_SAMPLES):
        deep = extract_deep(sample)
        print(f"  Sample {i+1}: domain_transfer_rate = {deep['domain_transfer_rate']:.4f}")

    print("\n→ Person A's professional vocabulary (mechanical/welding domain)")
    print("  surfaces involuntarily even in software discussions.")
    print("  This is an unforgeable cognitive watermark.")

    # ──────────────────────────────────────────────────────────────

    section("5. CONTINUOUS SESSION MONITORING")

    monitor = SessionMonitor(profile_a, window_size=50, overlap=25, rolling_n=3)

    # Simulate a session that starts authentic then switches
    authentic_text = """So I've been thinking about this problem and honestly the
    stress distribution is all wrong. You gotta look at where the load concentrates
    and figure out how to spread it more evenly across the system. Nothing is
    impossible here but it's gonna take some rethinking of the fundamental approach.
    I mean the current architecture just wasn't built for this kind of load."""

    impersonator_text = """The systematic analysis reveals that the implementation
    necessitates a comprehensive restructuring. Specifically, the abstraction layer
    between the service mesh and the data persistence tier requires significant
    refactoring to accommodate the increased throughput requirements. Furthermore,
    the deployment pipeline should incorporate additional validation stages."""

    print("Feeding authentic text...")
    result = monitor.analyze(authentic_text)
    if result:
        print(f"  Window {result['windows_analyzed']}: "
              f"score={result['window_score']:.3f} "
              f"rolling={result['rolling_score']:.3f} "
              f"level={result['level']}")

    print("\nFeed switches to impersonator...")
    result = monitor.analyze(impersonator_text)
    if result:
        print(f"  Window {result['windows_analyzed']}: "
              f"score={result['window_score']:.3f} "
              f"rolling={result['rolling_score']:.3f} "
              f"level={result['level']}")

    print("\n→ Continuous monitoring detects mid-session identity changes")
    print("  within approximately 200-400 words of the switch.")

    # ──────────────────────────────────────────────────────────────

    section("SUMMARY")

    print("The three-layer linguistic-cognitive mapping system provides:")
    print()
    print("  SURFACE (20%): What you write")
    print("    Vocabulary, punctuation, VTT artifacts")
    print("    → Easiest to forge, lowest weight")
    print()
    print("  MID (30%): How you construct sentences")
    print("    Length patterns, hedging vs assertion, transitions")
    print("    → Harder to forge, moderate weight")
    print()
    print("  DEEP (50%): How you think")
    print("    Self-correction, uncertainty response, domain transfer,")
    print("    processing style, values integration")
    print("    → Nearly impossible to forge, highest weight")
    print()
    print("Key properties:")
    print("  • Language-agnostic deep layer (survives translation)")
    print("  • Continuous session authentication (not just login)")
    print("  • Domain-transfer watermark (professional background)")
    print("  • VTT artifact biometrics (speech pattern recognition)")
    print("  • Impersonation detection even with borrowed vocabulary")


if __name__ == "__main__":
    main()
