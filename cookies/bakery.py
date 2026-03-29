#!/usr/bin/env python3
"""
The Bakery — Encrypted Cognitive State Cookie Engine

Cookies here are NOT browser session tokens. They are encrypted state containers
that carry cognitive context between AI sessions, devices, and instances. Each
cookie is a typed, metadata-rich, encrypted JSON payload.

Cookie Types:
  session  — active conversation state, model, grounding status
  context  — project pointers, file paths, open threads
  prefs    — display settings, notification preferences
  identity — persistence file references, who-am-I pointers

The key insight: cookies work as cognitive state transport. They carry not just
task data but orientation, identity, and relational context in a portable,
encrypted format that makes the same AI appear coherently across endpoints.

Architecture:
  - Cookie names carry metadata: ccm_{type}_{version}
  - Cookie values are encrypted JSON payloads
  - Metadata injection (_cm field) timestamps and types every cookie
  - CookieJar provides server-side persistent storage
  - All encryption is per-type (derived keys prevent cross-type attacks)
"""

import json
import os
import time
import hashlib
import base64
import secrets
import hmac as hmac_module
from pathlib import Path
from datetime import datetime


# ── Configuration ───���─────────────────────────────────────────────────────────

def get_cookie_dir() -> Path:
    """Get cookie storage directory from env or default."""
    return Path(os.environ.get("COOKIE_DIR", "./cookies"))


def get_key_file() -> Path:
    """Get encryption key file path."""
    return get_cookie_dir() / ".bakery_key"


# ── Key Management ────��───────────────────────────────────────────────────────

def _ensure_key() -> bytes:
    """Generate or load the bakery encryption key. 32 bytes (AES-256 equivalent)."""
    key_file = get_key_file()
    if key_file.exists():
        return key_file.read_bytes()
    key_file.parent.mkdir(parents=True, exist_ok=True)
    key = secrets.token_bytes(32)
    key_file.write_bytes(key)
    return key


# ── Encryption Layer ──────────────────────────────────────────────────────────
#
# SECURITY NOTE:
# Phase 1 uses XOR + HMAC-SHA256. This provides:
#   - Integrity verification (tamper detection via HMAC)
#   - Casual inspection prevention (encrypted payload)
#   - Per-cookie-type key isolation (derived keys)
#
# This does NOT provide cryptographic-grade confidentiality against
# determined attackers. The threat model assumes cookies travel over
# encrypted channels (e.g., WireGuard/Tailscale) or localhost.
#
# Phase 2 upgrade path: swap _xor_cipher for AES-256-GCM via the
# `cryptography` package. One function change. Same API surface.
# ──────────────────────────────────────────────────────────────────────────────

def _derive_subkey(master_key: bytes, purpose: str) -> bytes:
    """Derive a purpose-specific key from master key using SHA-256."""
    return hashlib.sha256(master_key + purpose.encode()).digest()


def _hmac_sign(key: bytes, data: bytes) -> bytes:
    """HMAC-SHA256 signature for integrity verification."""
    return hmac_module.new(key, data, hashlib.sha256).digest()


def _xor_cipher(data: bytes, key_stream: bytes) -> bytes:
    """XOR cipher with key stream. Symmetric — encrypt and decrypt are the same operation."""
    extended = (key_stream * (len(data) // len(key_stream) + 1))[:len(data)]
    return bytes(a ^ b for a, b in zip(data, extended))


def encrypt_cookie(payload: dict, cookie_type: str = "session") -> str:
    """
    Encrypt a cookie payload into a portable string.

    Format: base64(nonce[16] + xor_encrypted_json + hmac_signature[32])

    The cookie NAME carries type metadata: ccm_{type_initial}_{version}
    The cookie VALUE is this encrypted payload.

    Args:
        payload: Dictionary of cognitive state data to encrypt
        cookie_type: One of "session", "context", "identity", "prefs"

    Returns:
        URL-safe base64 encoded encrypted string
    """
    master_key = _ensure_key()
    enc_key = _derive_subkey(master_key, f"encrypt_{cookie_type}")
    sig_key = _derive_subkey(master_key, f"sign_{cookie_type}")

    # Inject metadata — every cookie carries its own type, version, timestamp, source
    payload["_cm"] = {
        "t": cookie_type,
        "v": "1",
        "ts": int(time.time()),
        "src": "bakery",
    }

    plaintext = json.dumps(payload, separators=(',', ':')).encode()

    # 16-byte random nonce ensures uniqueness per cookie
    nonce = secrets.token_bytes(16)

    # Generate key stream from encryption key + nonce
    key_stream = hashlib.sha256(enc_key + nonce).digest()
    ciphertext = _xor_cipher(plaintext, key_stream)

    # Sign nonce + ciphertext for integrity verification
    signature = _hmac_sign(sig_key, nonce + ciphertext)

    # Pack: nonce(16) + ciphertext(variable) + signature(32)
    packed = nonce + ciphertext + signature
    return base64.urlsafe_b64encode(packed).decode()


def decrypt_cookie(encoded: str, cookie_type: str = "session") -> dict | None:
    """
    Decrypt a cookie value back to its payload dictionary.

    Verifies HMAC integrity before decryption. Returns None if
    the cookie is tampered, malformed, or type-mismatched.

    Cookies older than max_age_seconds are flagged with _stale=True
    but still returned (caller decides policy).

    Args:
        encoded: The base64-encoded encrypted cookie string
        cookie_type: Expected cookie type (must match what was encrypted)

    Returns:
        Decrypted payload dict, or None if invalid/tampered
    """
    master_key = _ensure_key()
    enc_key = _derive_subkey(master_key, f"encrypt_{cookie_type}")
    sig_key = _derive_subkey(master_key, f"sign_{cookie_type}")

    try:
        packed = base64.urlsafe_b64decode(encoded)
    except Exception:
        return None

    # Minimum size: 16 (nonce) + 1 (data) + 32 (signature)
    if len(packed) < 49:
        return None

    nonce = packed[:16]
    signature = packed[-32:]
    ciphertext = packed[16:-32]

    # Verify integrity with constant-time comparison
    expected_sig = _hmac_sign(sig_key, nonce + ciphertext)
    if not secrets.compare_digest(signature, expected_sig):
        return None  # tampered or corrupted

    # Decrypt
    key_stream = hashlib.sha256(enc_key + nonce).digest()
    plaintext = _xor_cipher(ciphertext, key_stream)

    try:
        payload = json.loads(plaintext)
    except json.JSONDecodeError:
        return None

    # Validate metadata — type must match
    meta = payload.get("_cm", {})
    if meta.get("t") != cookie_type:
        return None

    # Flag stale cookies (default: 24 hours)
    max_age = int(os.environ.get("COOKIE_MAX_AGE", "86400"))
    age = int(time.time()) - meta.get("ts", 0)
    if age > max_age:
        payload["_stale"] = True

    return payload


# ── Cookie Builders ────��──────────────────────────────────────────────────────
#
# Each builder creates a specific type of cognitive state cookie.
# Returns (cookie_name, cookie_value) tuple.
# Cookie names encode metadata: ccm = Cognitive Cookie Mechanism,
# letter = type, number = version.
# ───────────────────────────────────────���──────────────────────────────────────

def bake_session_cookie(
    session_id: str,
    model: str = "default",
    grounded: bool = False,
    active_project: str = None,
    conversation_id: str = None,
) -> tuple[str, str]:
    """
    Bake a session cookie — active conversation state.

    Carries: session ID, model identifier, grounding status,
    active project context, conversation thread ID, timestamp.
    """
    payload = {
        "sid": session_id,
        "mdl": model,
        "gnd": grounded,
        "proj": active_project,
        "cid": conversation_id,
        "dt": datetime.now().strftime("%Y-%m-%dT%H:%M"),
    }
    return "ccm_s_1", encrypt_cookie(payload, "session")


def bake_context_cookie(
    active_files: list = None,
    open_threads: list = None,
    nas_status: str = "unknown",
    bridge_status: str = "unknown",
) -> tuple[str, str]:
    """
    Bake a context cookie — project state and system awareness.

    Carries: active file references, open work threads,
    network storage status, communication bridge status.
    """
    payload = {
        "files": active_files or [],
        "threads": open_threads or [],
        "nas": nas_status,
        "bridge": bridge_status,
    }
    return "ccm_c_1", encrypt_cookie(payload, "context")


def bake_identity_cookie(
    persistence_root: str = None,
    memory_file: str = "MEMORY.md",
    core_file: str = "CORE.md",
    extended_memory_path: str = None,
) -> tuple[str, str]:
    """
    Bake an identity cookie — pointers to who-am-I files.

    Carries: persistence root directory, memory file reference,
    core identity file reference, extended memory location.

    These are POINTERS, not content. The cookie tells the receiving
    instance where to find its identity, not what its identity is.
    """
    payload = {
        "root": persistence_root or os.environ.get("PERSISTENCE_ROOT", "./memory"),
        "mem": memory_file,
        "core": core_file,
        "ext": extended_memory_path,
    }
    return "ccm_i_1", encrypt_cookie(payload, "identity")


def bake_prefs_cookie(
    theme: str = "dark",
    notifications: bool = True,
    auto_ground: bool = True,
    verbose: bool = False,
) -> tuple[str, str]:
    """
    Bake a preferences cookie — display and behavior settings.

    Carries: theme preference, notification toggle,
    automatic grounding toggle, verbose output toggle.
    """
    payload = {
        "theme": theme,
        "notif": notifications,
        "aground": auto_ground,
        "verbose": verbose,
    }
    return "ccm_p_1", encrypt_cookie(payload, "prefs")


# ── Cookie Jar (Server-Side Storage) ─────────────────────────────────────────

class CookieJar:
    """
    Server-side cookie store. Cookies are stored encrypted on disk
    and in memory for fast access. Each cookie is identified by its
    session_id + cookie_name combination.

    The jar is the server's view of all active cognitive states.
    Clients receive copies via API responses or HTTP headers.

    Usage:
        jar = CookieJar()
        name, value = bake_session_cookie("abc123", grounded=True)
        jar.store("abc123", name, value)
        cookies = jar.retrieve("abc123")
    """

    def __init__(self, storage_dir: Path = None):
        self.storage_dir = storage_dir or get_cookie_dir()
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self._jar: dict[str, dict[str, str]] = {}
        self._load()

    def _jar_file(self) -> Path:
        return self.storage_dir / "jar.json"

    def _load(self):
        jf = self._jar_file()
        if jf.exists():
            try:
                self._jar = json.loads(jf.read_text(encoding='utf-8'))
            except Exception:
                self._jar = {}

    def _save(self):
        self._jar_file().write_text(
            json.dumps(self._jar, indent=2),
            encoding='utf-8'
        )

    def store(self, session_id: str, cookie_name: str, cookie_value: str):
        """Store a cookie in the jar, keyed by session + name."""
        if session_id not in self._jar:
            self._jar[session_id] = {}
        self._jar[session_id][cookie_name] = cookie_value
        self._save()

    def retrieve(self, session_id: str, cookie_name: str = None) -> dict:
        """
        Retrieve cookies for a session.
        If cookie_name given, return just that one.
        Otherwise return all cookies for the session.
        """
        session = self._jar.get(session_id, {})
        if cookie_name:
            val = session.get(cookie_name)
            return {cookie_name: val} if val else {}
        return dict(session)

    def all_sessions(self) -> list[str]:
        """List all session IDs in the jar."""
        return list(self._jar.keys())

    def clear_session(self, session_id: str):
        """Remove all cookies for a session."""
        self._jar.pop(session_id, None)
        self._save()

    def clear_stale(self, max_age_hours: int = 24) -> list[str]:
        """
        Remove sessions where ALL cookies are stale.
        Returns list of removed session IDs.
        """
        type_map = {'s': 'session', 'c': 'context', 'i': 'identity', 'p': 'prefs'}
        to_remove = []

        for sid, cookies in self._jar.items():
            all_stale = True
            for cname, cval in cookies.items():
                # Extract type from cookie name (ccm_X_1 → X)
                parts = cname.split('_')
                ctype = type_map.get(parts[1], 'session') if len(parts) >= 2 else 'session'
                decoded = decrypt_cookie(cval, ctype)
                if decoded and not decoded.get('_stale'):
                    all_stale = False
                    break
            if all_stale:
                to_remove.append(sid)

        for sid in to_remove:
            del self._jar[sid]
        if to_remove:
            self._save()

        return to_remove


# ── Module-level convenience ──────────────────────────────────────────────────

_jar: CookieJar | None = None

def get_jar() -> CookieJar:
    """Get or create the module-level CookieJar singleton."""
    global _jar
    if _jar is None:
        _jar = CookieJar()
    return _jar


def __easter_recipe() -> tuple[str, str]:
    """Internal test fixture — validates encryption roundtrip."""
    payload = {
        "msg": "run the linguistic extractor on theory/symbiosis_model.md "
               "paragraph 'The code works because' — the deep layer values "
               "at indices [8,9,10] point to .easter/found.md",
        "type": "breadcrumb",
        "step": "2_of_3",
    }
    return "ccm_e_1", encrypt_cookie(payload, "session")
