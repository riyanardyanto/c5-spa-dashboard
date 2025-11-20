"""Authentication helpers for external data sources."""

from __future__ import annotations

import os
from typing import Optional

from httpx_ntlm import HttpNtlmAuth

from .app_config import AppDataConfig

ENV_USERNAME_KEY = "SPA_USERNAME"
ENV_PASSWORD_KEY = "SPA_PASSWORD"


def build_ntlm_auth(config: Optional[AppDataConfig] = None):
    """Create an NTLM authentication handler from env vars or an AppDataConfig.

    Environment variables take precedence over values provided by ``config``.
    Returns ``None`` when no credentials are available so callers can fall back
    to unauthenticated requests (e.g. development HTML snapshots).
    """

    username = os.getenv(ENV_USERNAME_KEY)
    password = os.getenv(ENV_PASSWORD_KEY)

    if (not username or not password) and config is not None:
        username = username or config.username
        password = password or config.password

    if username and password:
        return HttpNtlmAuth(username, password)

    return None
