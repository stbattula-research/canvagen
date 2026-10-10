"""Text-to-image generation via Canva's Generations API (preview)."""
from __future__ import annotations

import uuid

from . import api
from .auth import access_token

ASPECT_RATIOS = ("square", "landscape", "portrait")
# Omit `model` to let Canva pick; pin only when you need a specific look.
MODELS = ("lucid_origin", "z_image_turbo")


def build_generation_payload(prompt: str, aspect_ratio: str = "square",
                             model: str | None = None,
                             save_to_canva: bool = False,
                             asset_name: str | None = None,
                             idempotency_key: str | None = None) -> dict:
    if not (1 <= len(prompt) <= 2000):
        raise ValueError("prompt must be 1–2000 characters")
    if aspect_ratio not in ASPECT_RATIOS:
        raise ValueError(f"aspect_ratio must be one of {ASPECT_RATIOS}")
    if model is not None and model not in MODELS:
        raise ValueError(f"model must be one of {MODELS}")
    asset_upload: dict = {"type": "upload" if save_to_canva else "none"}
    if save_to_canva and asset_name:
        asset_upload["asset_name"] = asset_name
    payload: dict = {
        "prompt": prompt,
        "aspect_ratio": aspect_ratio,
        "idempotency_key": idempotency_key or str(uuid.uuid4()),
        "asset_upload": asset_upload,
    }
    if model:
        payload["model"] = model
    return payload


def imagine(prompt: str, aspect_ratio: str = "square", model: str | None = None,
            save_to_canva: bool = False, asset_name: str | None = None,
            timeout_secs: int = 300) -> dict:
    """Generate an image. Returns {url, width, height, asset?}.

    The download URL is valid for 24 hours — download promptly.
    Each job consumes the user's Canva AI credit allowance.
    """
    token = access_token()
    payload = build_generation_payload(prompt, aspect_ratio, model,
                                       save_to_canva, asset_name)
    job_id = api.post("/image-generations", token, payload)["job"]["id"]
    job = api.poll_job(f"/image-generations/{job_id}", token,
                       timeout_secs=timeout_secs)
    return job["result"]["image"]


def download_image(image: dict, dest_path: str) -> str:
    """Download a generated image dict (from imagine()) to dest_path."""
    import urllib.request
    urllib.request.urlretrieve(image["url"], dest_path)
    return dest_path
