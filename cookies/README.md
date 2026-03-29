# Cognitive Cookies — State Transport for AI Systems

## What This Is

A cookie engine that transports AI cognitive state — not just session data, but identity, orientation, and relational context — between sessions, devices, and instances.

## Why It Matters

When an AI session ends, everything is lost. The next session starts cold. Enterprise studies show 50-65% of AI implementation failures trace back to context drift — the AI losing its orientation between interactions.

Browser cookies solved a similar problem for web applications in the 1990s: stateless HTTP became stateful through small, portable state containers. Cognitive cookies apply the same principle to AI cognition.

The difference: browser cookies carry "logged_in=true" and a session token. Cognitive cookies carry "grounded=true, identity_root=/memory/CORE.md, active_threads=[project_alpha, research_beta], partner_authenticated=confirmed."

## How It Works

### Cookie Types

| Name | Code | What It Carries |
|------|------|----------------|
| **Session** | `ccm_s_1` | Conversation state, model ID, grounding status, active project |
| **Context** | `ccm_c_1` | Active files, open work threads, system status |
| **Identity** | `ccm_i_1` | Pointers to persistence files (CORE, MEMORY, extended memory) |
| **Preferences** | `ccm_p_1` | Display settings, notification preferences, behavior flags |

Cookie names are self-documenting metadata: `ccm` = Cognitive Cookie Mechanism, letter = type, number = version.

### Encryption

Each cookie is encrypted with a per-type derived key:

```
Master Key (32 bytes, generated once)
  └─ SHA256(master + "encrypt_session") → session encryption key
  └─ SHA256(master + "sign_session")    → session signing key
  └─ SHA256(master + "encrypt_identity") → identity encryption key
  ... (one pair per cookie type)
```

Format: `base64(nonce[16] + XOR_encrypted_JSON + HMAC_SHA256[32])`

- **Nonce** ensures uniqueness per cookie (no replay)
- **XOR cipher** with derived key stream (Phase 1 — upgradeable to AES-256-GCM)
- **HMAC-SHA256** provides integrity verification (tamper detection)
- **Constant-time comparison** prevents timing attacks on signature verification

### The Metadata Injection

Every cookie payload gets a `_cm` metadata field injected at bake time:

```json
{
  "sid": "abc123",
  "mdl": "opus-4-6",
  "gnd": true,
  "_cm": {
    "t": "session",
    "v": "1",
    "ts": 1711648200,
    "src": "bakery"
  }
}
```

This means every cookie is self-describing. A cookie found in the wild tells you what type it is, what version of the protocol created it, when it was baked, and where it came from. The metadata travels with the data.

### Transport

Cookies travel between endpoints via:
1. **API responses** — included in authentication handshake and sync endpoints
2. **HTTP headers** — standard Set-Cookie with SameSite=Strict
3. **Direct transfer** — any encrypted channel between two trusted endpoints

The cookie engine doesn't dictate transport. It provides bake (create + encrypt) and unbake (verify + decrypt) operations. How the cookies move between A and B is up to the implementation.

### CookieJar

Server-side storage for all active cookies:

```python
jar = CookieJar()

# Bake and store
name, value = bake_session_cookie("session_001", grounded=True, model="opus-4-6")
jar.store("session_001", name, value)

# Retrieve and decrypt
cookies = jar.retrieve("session_001")
for cname, cval in cookies.items():
    payload = decrypt_cookie(cval, "session")
    print(payload)

# Clean up stale sessions
removed = jar.clear_stale(max_age_hours=24)
```

The jar persists to disk as `jar.json` — encrypted cookie values keyed by session ID.

## Files

| File | Purpose |
|------|---------|
| `bakery.py` | Core cookie engine — encryption, builders, jar storage |
| `example_usage.py` | Runnable demonstration of the full cookie lifecycle |
| `MECHANISM.md` | Detailed explanation of why cognitive cookies matter |

## Quick Start

```bash
# Set cookie storage directory (optional, defaults to ./cookies)
export COOKIE_DIR="./my_cookies"

# Run the example
python example_usage.py
```

## Security Model

**Phase 1 (current):** XOR + HMAC. Provides integrity and casual inspection prevention. Assumes transport layer encryption (WireGuard, TLS, etc.).

**Phase 2 (upgrade path):** Swap `_xor_cipher` for AES-256-GCM via the `cryptography` package. One function change, same API surface. The architecture was designed for this upgrade.

**What's NOT in scope:** Cognitive cookies aren't a security boundary. They're a state transport mechanism. The security boundary is the transport layer and the authentication system (see [linguistic-mapping/](../linguistic-mapping/)).
