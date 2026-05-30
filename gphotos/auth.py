import threading
import time
from typing import Optional
from urllib.parse import parse_qs, urlencode

import httpx


class AuthManager:
    def __init__(self, client: httpx.Client, language: str = "en"):
        self._client = client
        self._language = language
        self._token: str = ""
        self._expiry: int = 0
        self._lock = threading.Lock()

    def _parse_auth_string(self, auth_string: str) -> dict[str, str]:
        return {k: v[0] for k, v in parse_qs(auth_string).items()}

    def get_bearer_token(self, auth_string: str) -> str:
        # Fast path: token is valid, no lock needed
        now = int(time.time())
        if self._token and self._expiry > now:
            return self._token
        # Slow path: token expired, acquire lock and double-check
        with self._lock:
            now = int(time.time())
            if self._token and self._expiry > now:
                return self._token
            self._token, self._expiry = self._fetch_token(auth_string)
            return self._token

    def _fetch_token(self, auth_string: str) -> tuple[str, int]:
        params = self._parse_auth_string(auth_string)
        auth_data = {
            "app": "com.google.android.apps.photos",
            "callerPkg": "com.google.android.apps.photos",
            "device": params.get("androidId", ""),
        }
        for key, val in params.items():
            if key not in ("it_caveat_types", "assertion_jwt", "token_binding_alias"):
                auth_data[key] = val

        headers = {
            "app": "com.google.android.apps.photos",
            "Content-Type": "application/x-www-form-urlencoded",
            "device": params.get("androidId", ""),
            "User-Agent": "GoogleAuth/1.4 (Pixel XL PQ2A.190205.001); gzip",
        }

        resp = self._client.post(
            "https://android.googleapis.com/auth",
            content=urlencode(auth_data),
            headers=headers,
        )
        resp.raise_for_status()

        parsed: dict[str, str] = {}
        for line in resp.text.splitlines():
            line = line.strip()
            if "=" in line:
                key, val = line.split("=", 1)
                parsed[key] = val

        token = parsed.get("Auth", "")
        expiry = int(parsed.get("Expiry", "0"))
        if not token:
            raise RuntimeError("Auth response missing Auth token")
        return token, expiry
