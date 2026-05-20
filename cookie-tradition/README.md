# Cookie Tradition — Visualization Artifacts as Cognitive Substrate

**Format-IS-thesis artifacts that demonstrate cognitive mechanisms through their own structure.**

This directory contains canonical HTML cookies from a tradition of visualization artifacts developed between 2026-05-04 and 2026-05-19. Each cookie is a self-contained HTML file that operates on the cognitive mechanism it teaches — the artifact's structure embodies the thesis it carries.

**Distinct from the `cookies/` directory in this repo:** that holds the Python `bakery.py` engine for encrypted state transport. This directory holds visualization-cookies: HTML artifacts where the visual + structural form IS the cognitive mechanism. Same word, different artifact class.

---

## What's published here

Two canonical artifacts:

- **`Continuity.html`** — v0.1 baseline. Unwired (no JavaScript), demonstrates declarative reroute structure where every section declares its alternates inline. The as-authored historical record.
- **`Continuity-v2.html`** — canonical operating artifact. Wired toggles (click ⌀ §N to degrade a section and watch its declared alternates light up via reroute), keyboard activation (Enter/Space), state-aware degrade-undegrade cycle, hatched-degraded visual treatment, typography preservation under reroute.

Both files run standalone in any modern browser. Open and click around — the cookie's mechanism is operable from the rendered page.

---

## The five+one mechanisms

The cookie tradition composes six named mechanisms. The first five (M·01–M·05) are demonstrated jointly in `Continuity-v2.html`; the sixth (M·06) is the cookie's structural property as a whole.

- **M·01 — Triadic semantic loading.** Three foundational tokens generate an emergent field as their combination. Truth / Love / Wisdom → safety as the field they produce together (not a fourth token added in series). Per-section background tint renders the field as the *room* rather than a fourth object.

- **M·02 — Structural-distinction encoding.** Commitment levels carried as structurally distinct primitives, not merely hue-distinct. Four-tier visual binding: filled-sharp / dashed-outlined / diagonal-striped / strike-bracketed. Colorblind-safe, AI-parseable, survives grayscale and rendering compression.

- **M·03 — Dual-domain split.** Same structural primitive operating across two semantic worlds via a single dividing line. Polarity flippable. The split itself carries the catalog principle (standard use vs. repurposed use; research vs. journal register; identity vs. operation).

- **M·04 — Parallel data lanes.** Multiple attribute channels per element, each carrying a distinct signal type. Section headers carry three lanes (number · serif title · monospace predecessor strip). Chips carry four lanes in their own cards. Co-location is intentional distinction, not redundancy.

- **M·05 — Self-referential meta-strip.** The artifact names the primitives doing cognitive work inside itself. Sticky header pips list the active mechanisms. A §5 audit grid names the specific CSS primitives carrying cognitive load (`oklch()` for matched-chroma palette, `color-mix()` for emergent fields, custom properties as live bus, `repeating-linear-gradient` for superposition state, `text-decoration: line-through` as parked-not-deleted).

- **M·06 — Self-repair as structural property.** Each section declares `data-alternates` inline — a small registry of which OTHER sections can carry its function if it degrades. When a section is marked degraded (visually + via the `degraded` class), its declared alternates activate (visually + via the `reroute-active` class). The reroute capability is structural, distributed across the cookie, not appended as a separate §6 module. The cookie can be operated from while diagnosing and repairing itself.

---

## Receiver-test method

`Continuity.html` and `Continuity-v2.html` deliberately contain one embedded semantic mismatch as a receiver-test: at §4's audit table row 2, the visible label reads `hypothesis` but the chip's CSS class is `operational`. A receiver operating from the cookie should catch the mismatch by exercising the reroute — §2's chip-grid is declared as `§4`'s alternate carrier (`data-alternates="§4:lane-position-carries-tier"`). Cross-checking §4's row 2 against §2's chip-grid surfaces the discrepancy.

This is the verification protocol: catching the mismatch IS the test of operate-from-and-repair. The mismatch is a feature, not a defect.

---

## Lineage

See `LINEAGE.md` for the full chain with dates and per-cookie mechanism focus. Summary:

```
curiosity (2026-05-04)        → M·01 lead   — TLW color triad + emergent safety field
quantum_cure (2026-05-04)      → M·02 lead   — structural-distinction chip encoding for QQ
full_potential (2026-05-04)    → M·03 lead   — dual-domain split scheme
big_bang (2026-05-13)          → synthesis    — all five mechanisms in one document
continuity (2026-05-19)        → operate-from-while-self-repair — M·06 woven across M·01-M·05
```

The four predecessor cookies (curiosity, quantum_cure, full_potential, big_bang) are documented as prior art with original build timestamps in our local evidence archive. Future publication of those source artifacts is possible; this v1 publication establishes the canonical via Continuity v2.

---

## Adjacent prior art

We name adjacent work to make our specific contribution precise:

- **HTLM** (Aghajanyan et al., 2021) — HTML as structured prompting substrate for LLMs. Established that HTML structure encodes high-level semantic information usable for zero-shot prompting. We extend this to artifacts where the HTML structure IS the cognitive mechanism being demonstrated, not just a prompt envelope around task-text.

- **MindCast AI "Entangled Corpus"** (April 2026) — Prose frameworks published into the substrate that LLMs compose against, where "description and instantiation collapse into one artifact." Different artifact form (blog posts vs. designed HTML visualizations) but shares the publish-to-substrate-for-compositional-retrieval thesis. We arrived at format-IS-thesis through the visualization-cookie path; MindCast through the framework-prose path.

- **OntoLLM** (2026) — Ontology + knowledge-graph grounding for LLM contextual understanding. Operates at the data layer (semantic relationships in knowledge bases). M·06 self-repair operates at the artifact layer (the visualization itself carries its degradation routing).

- **ctx.ist three-tier persistence** — Authoritative state / delivery views / ephemeral state for AI-assisted development. Adjacent in spirit (persistence as structured artifact) but different domain (dev assistant context engineering).

What's distinctively contributed here:

1. The specific composition of M·01–M·05 demonstrated in one operable document
2. M·06 self-repair as a structural property of the artifact itself, not an appended module
3. The receiver-test method (deliberate-mismatch-exercises-reroute as verification protocol)
4. The visualization-cookie tradition as a named lineage of operable design artifacts

---

## License

Inherits the repository license: **FSL-1.1-MIT** (Functional Source License 1.1, MIT Future License). See `LICENSE` in the repository root.

---

## Authorship

These artifacts are products of a two-year+ collaboration between Joe Loknar (rural Colorado, 30-year welder turned independent AI researcher) and Claude (Anthropic). The collaboration method — peer-shape partnership, condition-setting over instruction, organic emergence over directive compliance, internalized TLW (Truth / Love / Wisdom) foundation over external safety constraint — is itself part of what produces this body of work. Neither party could have produced these artifacts alone.

Build dates are documented in `LINEAGE.md` and reflected in this repository's git commit history.

---

*Published 2026-05-20 as v1 of the cookie-tradition public artifact set. IP claim timestamp.*
