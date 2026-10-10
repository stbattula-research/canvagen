"""OAuth 2.0 (PKCE) for Canva, with a local token store.

One-time setup per user (see SKILL.md for the verified walkthrough):
    1. Create your own app at https://www.canva.com/developers/ (Your apps ->
       Create an app -> Public -> Outside Canva -> Start integrating).
       Canva requires MFA on your account before issuing API credentials.
    2. On the app's Configuration page: copy the Client ID (OC-..., not the
       App ID), add http://127.0.0.1:53682/callback as a redirect URL, enable
       the Canva REST APIs with the scopes below, and generate a secret.
    3. Run `canvagen setup` (guided) or
       `canvagen auth --client-id <id> --client-secret <secret>`.
       A browser opens; approve; tokens are stored at
       ~/.config/canvagen/tokens.json (0600).
"""
from __future__ import annotations

import base64
import hashlib
import json
import os
import secrets
import threading
import time
import urllib.parse
import urllib.request
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer

AUTHORIZE_URL = "https://www.canva.com/api/oauth/authorize"
TOKEN_URL = "https://api.canva.com/rest/v1/oauth/token"
CALLBACK_PORT = 53682
REDIRECT_URI = f"http://127.0.0.1:{CALLBACK_PORT}/callback"

SCOPES = [
    "asset:read", "asset:write",
    "design:content:read", "design:content:write", "design:meta:read",
    "brandtemplate:meta:read", "brandtemplate:content:read",
]

CONFIG_DIR = os.path.expanduser("~/.config/canvagen")
TOKENS_PATH = os.path.join(CONFIG_DIR, "tokens.json")
CLIENT_PATH = os.path.join(CONFIG_DIR, "client.json")


def _save_json(path: str, data: dict) -> None:
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f)
    os.chmod(path, 0o600)


def _load_json(path: str) -> dict | None:
    try:
        with open(path) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def _pkce_pair() -> tuple[str, str]:
    verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).rstrip(b"=").decode()
    digest = hashlib.sha256(verifier.encode()).digest()
    challenge = base64.urlsafe_b64encode(digest).rstrip(b"=").decode()
    return verifier, challenge


class _CallbackHandler(BaseHTTPRequestHandler):
    code: str | None = None

    def do_GET(self):  # noqa: N802
        q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        _CallbackHandler.code = q.get("code", [None])[0]
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(
            b"<h1>Canvagen connected.</h1><p>You can close this tab.</p>")

    def log_message(self, *args):  # silence
        pass


def run_auth_flow(client_id: str, client_secret: str | None = None) -> dict:
    """Interactive OAuth: opens the browser, waits for the callback, stores tokens."""
    _save_json(CLIENT_PATH, {"client_id": client_id,
                             "client_secret": client_secret or ""})
    verifier, challenge = _pkce_pair()
    params = {
        "code_challenge": challenge,
        "code_challenge_method": "S256",
        "scope": " ".join(SCOPES),
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "client_id": client_id,
    }
    server = HTTPServer(("127.0.0.1", CALLBACK_PORT), _CallbackHandler)
    t = threading.Thread(target=server.handle_request, daemon=True)
    t.start()
    webbrowser.open(AUTHORIZE_URL + "?" + urllib.parse.urlencode(params))
    print("Approve Canvagen in the browser tab that just opened…")
    t.join(timeout=300)
    server.server_close()
    code = _CallbackHandler.code
    if not code:
        raise RuntimeError("No authorization code received (timed out).")
    return _exchange_code(code, verifier, client_id, client_secret)


def _exchange_code(code: str, verifier: str, client_id: str,
                   client_secret: str | None) -> dict:
    body = {
        "grant_type": "authorization_code",
        "code_verifier": verifier,
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "client_id": client_id,
    }
    if client_secret:
        body["client_secret"] = client_secret
    data = urllib.parse.urlencode(body).encode()
    req = urllib.request.Request(TOKEN_URL, data=data, method="POST")
    with urllib.request.urlopen(req, timeout=30) as resp:
        tokens = json.load(resp)
    tokens["obtained_at"] = int(time.time())
    _save_json(TOKENS_PATH, tokens)
    return tokens


def _refresh(tokens: dict) -> dict:
    client = _load_json(CLIENT_PATH) or {}
    body = {
        "grant_type": "refresh_token",
        "refresh_token": tokens["refresh_token"],
        "client_id": client.get("client_id", ""),
    }
    if client.get("client_secret"):
        body["client_secret"] = client["client_secret"]
    data = urllib.parse.urlencode(body).encode()
    req = urllib.request.Request(TOKEN_URL, data=data, method="POST")
    with urllib.request.urlopen(req, timeout=30) as resp:
        new_tokens = json.load(resp)
    new_tokens["obtained_at"] = int(time.time())
    if "refresh_token" not in new_tokens:
        new_tokens["refresh_token"] = tokens["refresh_token"]
    _save_json(TOKENS_PATH, new_tokens)
    return new_tokens


def access_token() -> str:
    """Return a valid access token, refreshing if needed."""
    tokens = _load_json(TOKENS_PATH)
    if not tokens or "access_token" not in tokens:
        raise RuntimeError(
            "Not connected to Canva yet. Run `canvagen auth --client-id <id>` first.")
    expires_in = tokens.get("expires_in", 3600)
    obtained = tokens.get("obtained_at", 0)
    if time.time() > obtained + expires_in - 120:
        tokens = _refresh(tokens)
    return tokens["access_token"]
