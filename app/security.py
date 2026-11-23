"""Token-to-tenant mapping: caller cannot choose its own tenant identity.

AGENTQUAL_TENANT_TOKENS is JSON object of tenant-name => random bearer token.
Never write tokens to source control or logs. This is a demo access-control layer,
not a substitute for an identity provider, rate limiting, or token rotation.
"""
import json
import os
import secrets
from fastapi import Header, HTTPException

def _tokens():
    raw = os.environ.get("AGENTQUAL_TENANT_TOKENS", "")
    if not raw:
        return {}
    try:
        mapping = json.loads(raw)
    except (ValueError, TypeError) as exc:
        raise RuntimeError("Invalid AGENTQUAL_TENANT_TOKENS JSON") from exc
    if not isinstance(mapping, dict) or not mapping or any(
            not isinstance(t, str) or not t.strip() or
            not isinstance(v, str) or len(v) < 24 for t, v in mapping.items()):
        raise RuntimeError("Invalid tenant token configuration")
    if len(set(mapping.values())) != len(mapping):
        raise RuntimeError("Tenant API tokens must be unique")
    return mapping

def validate_security_config():
    mapping = _tokens()
    if os.environ.get("APP_ENV", "development") == "production":
        if not mapping:
            raise RuntimeError("Production needs AGENTQUAL_TENANT_TOKENS")
        if not os.environ.get("DATABASE_URL"):
            raise RuntimeError("Production needs DATABASE_URL")

def principal(x_api_key: str | None = Header(default=None)):
    mapping = _tokens()
    if not mapping and os.environ.get("APP_ENV", "development") != "production":
        return "local-demo"
    if x_api_key is None:
        raise HTTPException(status_code=401, detail="API key required")
    # Compare every configured token to avoid early break on the first match.
    matches = [tenant for tenant, token in mapping.items()
               if secrets.compare_digest(x_api_key, token)]
    if not matches:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return matches[0]

def require_owner(snapshot, tenant_id: str):
    if not snapshot.values:
        raise HTTPException(status_code=404, detail="Unknown thread")
    if snapshot.values.get("tenant_id") != tenant_id:
        # Avoid disclosing whether a foreign thread exists.
        raise HTTPException(status_code=404, detail="Unknown thread")
