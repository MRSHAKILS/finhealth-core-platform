import hashlib


def redact_pii(value: str) -> str:
    """Replaces a personal value with a short, non-reversible token for logs."""
    digest = hashlib.sha256(value.encode("utf-8")).hexdigest()[:12]
    return f"[REDACTED:{digest}]"
