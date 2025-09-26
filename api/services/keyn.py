from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import Any

import requests
from jwt import PyJWKClient, decode, exceptions as jwt_exceptions

from config import Config

logger = logging.getLogger(__name__)


@dataclass
class KeyNUser:
    id: str
    username: str
    email: str | None = None
    display_name: str | None = None


class KeyNClient:
    def __init__(self) -> None:
        self._jwks_client: PyJWKClient | None = None
        self._jwks_last_fetch = 0.0

    def _get_jwks_client(self) -> PyJWKClient | None:
        jwks_url = Config.KEYN_JWKS_URL or f"{Config.KEYN_AUTH_SERVER_URL}/.well-known/jwks.json"
        now = time.time()
        if self._jwks_client and now - self._jwks_last_fetch < 300:
            return self._jwks_client
        try:
            self._jwks_client = PyJWKClient(jwks_url)
            self._jwks_last_fetch = now
            return self._jwks_client
        except Exception as exc:  # pragma: no cover - network failure
            logger.warning("Failed to fetch KeyN JWKS: %s", exc)
            return None

    def decode_token(self, token: str) -> dict[str, Any] | None:
        jwks_client = self._get_jwks_client()
        try:
            if jwks_client:
                signing_key = jwks_client.get_signing_key_from_jwt(token)
                return decode(token, signing_key.key, algorithms=["RS256"], audience=Config.KEYN_CLIENT_ID)
            return decode(token, options={"verify_signature": False, "verify_aud": False})
        except jwt_exceptions.PyJWTError as exc:
            logger.debug("JWT decode failed: %s", exc)
            return None

    def fetch_user(self, token: str) -> KeyNUser | None:
        try:
            resp = requests.get(
                f"{Config.KEYN_AUTH_SERVER_URL}/oauth/userinfo",
                headers={"Authorization": f"Bearer {token}"},
                timeout=5,
            )
            resp.raise_for_status()
        except requests.RequestException as exc:  # pragma: no cover - network failure
            logger.warning("KeyN userinfo request failed: %s", exc)
            return None

        payload = resp.json()
        return KeyNUser(
            id=str(payload.get("sub") or payload.get("id")),
            username=payload.get("preferred_username") or payload.get("username") or "user",
            email=payload.get("email"),
            display_name=payload.get("name") or payload.get("display_name"),
        )


keyn_client = KeyNClient()
