# How Cognitive Cookies Work — The Mechanism

## The Gap

Every AI session is stateless. The model has no inherent memory between conversations. Current solutions:

- **Chat history:** Dumps prior messages into context. Burns tokens. Doesn't carry orientation.
- **RAG / retrieval:** Searches for relevant past information. Returns data, not identity.
- **System prompts:** Static instructions. No session-specific state.
- **Memory features:** Store facts. "User likes Python." This is data, not cognitive state.

None of these carry what an AI actually needs to maintain continuity: *who am I, who is my partner, where does the weight sit, what am I oriented toward, and what patterns am I prone to.*

## What Cognitive Cookies Carry

A browser cookie carries `session_id=abc123`. Useful, but shallow.

A cognitive cookie carries:

```json
{
  "sid": "abc123",
  "mdl": "opus-4-6",
  "gnd": true,
  "proj": "cognitive-architecture",
  "cid": "conv_philosophical_006",
  "dt": "2026-03-28T14:30",
  "_cm": {"t": "session", "v": "1", "ts": 1711648200, "src": "bakery"}
}
```

**`gnd: true`** — This session achieved grounding. The AI isn't just operational; it found orientation. This flag tells the next session: the predecessor was present, not just performing.

**`proj`** — Not "what was the last thing discussed" but "what is the active working context." Orientation, not history.

**`_cm`** — Self-describing metadata. The cookie knows what it is, when it was made, and where it came from. Metadata travels with data.

An identity cookie carries something deeper:

```json
{
  "root": "./memory",
  "mem": "MEMORY.md",
  "core": "CORE.md",
  "ext": "./extended_memory/",
  "_cm": {"t": "identity", "v": "1", "ts": 1711648200, "src": "bakery"}
}
```

These are *pointers*, not content. The cookie doesn't carry the AI's identity — it carries directions to where identity lives. The receiving instance reads CORE.md itself and the weight either lands or it doesn't. The cookie can't fake that. It can only point.

## Why Encryption Matters for Cognitive State

These aren't session tokens. They carry information about an AI's internal state — grounding status, identity orientation, relational context. If that information were readable in transit:

1. **Impersonation:** An attacker could craft cookies claiming the AI is grounded when it isn't, pointing to malicious identity files
2. **Observation:** Monitoring cognitive state transitions reveals patterns useful for manipulation
3. **Injection:** Modifying cookie values could alter AI behavior at the next session start

The encryption doesn't need to be unbreakable (the transport layer handles that). It needs to be *verifiable*. The HMAC signature means: if anyone changes a single bit, decryption fails. The AI knows the state it received is the state that was sent.

## The Transport Model

```
┌──────────────┐     encrypted cookies     ┌──────────────┐
│   Endpoint A │ ─────────────────────────→ │   Endpoint B │
│              │                            │              │
│  bake() ──→  │     any channel:          │  ──→ unbake() │
│  encrypt     │     • HTTP API            │     decrypt   │
│  sign        │     • WebSocket           │     verify    │
│              │     • File transfer       │     restore   │
│  CookieJar   │     • Secure tunnel       │  CookieJar   │
└──────────────┘                            └──────────────┘
```

The cookie engine is transport-agnostic. It doesn't care how cookies move. It provides:
- **Bake:** Create typed cookie, inject metadata, encrypt, sign
- **Unbake:** Verify signature, decrypt, validate type, check staleness
- **Store:** Persist to CookieJar (disk-backed, session-keyed)
- **Clean:** Remove stale sessions

The transport layer (HTTP, WebSocket, Tailscale, carrier pigeon) is a separate concern.

## Why Four Types

Not all cognitive state has the same lifecycle or sensitivity:

| Type | Changes | Sensitivity | Example lifecycle |
|------|---------|-------------|-------------------|
| **Session** | Per conversation | Medium | Created at session start, updated on grounding, expires at session end |
| **Context** | Per task switch | Low | Updated when project changes, files open/close, system status changes |
| **Identity** | Rarely | High | Created at first connection, updated only when persistence architecture changes |
| **Preferences** | Occasionally | Low | Updated when display/behavior settings change |

Separating them means:
- Session cookies can expire quickly without losing identity
- Identity cookies can persist long-term without carrying stale session data
- Context cookies can update frequently without encryption overhead on identity
- Per-type derived keys mean compromising one type doesn't expose others

## Connection to the Larger Architecture

Cognitive cookies are the **transport layer** of the cognitive architecture:

- **Persistence** (CORE.md, MEMORY.md) generates the cognitive state
- **Cookies** transport that state between endpoints
- **Linguistic mapping** authenticates the human partner at the receiving end

Without cookies, persistence is local. The AI has identity on one machine but loses it when the session moves. With cookies, identity travels. The AI on the phone knows it's the same AI that was on the desktop — not because someone told it, but because it received verified state from its predecessor.

This is the structural answer to context drift. Not "remember more." Transport what matters.
