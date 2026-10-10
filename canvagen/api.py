"""Thin HTTP client for the Canva Connect REST API."""
from __future__ import annotations

import json
import time
import urllib.request
import urllib.error

BASE = "https://api.canva.com/rest/v1"


class CanvaError(Exception):
    def __init__(self, message: str, status: int | None = None, code: str | None = None):
        super().__init__(message)
        self.status = status
        self.code = code


def _request(method: str, path: str, token: str, body: dict | None = None,
             timeout: int = 60) -> dict:
    req = urllib.request.Request(
        BASE + path,
        data=json.dumps(body).encode() if body is not None else None,
        method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode()
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        code = None
        try:
            payload = json.loads(e.read().decode() or "{}")
            code = payload.get("code")
            message = payload.get("message", str(payload))
        except Exception:
            message = f"HTTP {e.code}"
        raise CanvaError(f"Canva API error: {message}", status=e.code, code=code)


def get(path: str, token: str) -> dict:
    return _request("GET", path, token)


def post(path: str, token: str, body: dict) -> dict:
    return _request("POST", path, token, body)


def poll_job(path: str, token: str, timeout_secs: int = 300,
             interval_secs: int = 5) -> dict:
    """Poll an async job (image-generations, autofills, exports) until done."""
    deadline = time.time() + timeout_secs
    while True:
        job = get(path, token).get("job", {})
        status = job.get("status")
        if status == "success":
            return job
        if status == "failed":
            err = job.get("error", {})
            raise CanvaError(
                f"Job failed: {err.get('code', 'unknown')}",
                code=err.get("code"),
            )
        if time.time() > deadline:
            raise CanvaError(f"Timed out waiting for {path}")
        time.sleep(interval_secs)
