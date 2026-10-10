import json
import os

import canvagen.auth as auth


def test_token_store_roundtrip_and_perms(tmp_path, monkeypatch):
    monkeypatch.setattr(auth, "CONFIG_DIR", str(tmp_path))
    monkeypatch.setattr(auth, "TOKENS_PATH", str(tmp_path / "tokens.json"))
    auth._save_json(auth.TOKENS_PATH, {"access_token": "abc"})
    assert auth._load_json(auth.TOKENS_PATH)["access_token"] == "abc"
    assert oct(os.stat(auth.TOKENS_PATH).st_mode & 0o777) == "0o600"


def test_missing_store_returns_none(tmp_path, monkeypatch):
    monkeypatch.setattr(auth, "TOKENS_PATH", str(tmp_path / "nope.json"))
    assert auth._load_json(auth.TOKENS_PATH) is None
