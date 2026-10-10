"""Design workflows: create, autofill brand templates, export, upload assets."""
from __future__ import annotations

import mimetypes
import os
import urllib.request

from . import api
from .auth import access_token

EXPORT_FORMATS = ("png", "jpg", "pdf")


def create_design(title: str, design_type: str = "doc") -> dict:
    """Create a blank design. design_type e.g. doc, presentation, instagram_post."""
    token = access_token()
    return api.post("/designs", token,
                    {"title": title, "design_type": {"type": design_type}})


def template_dataset(brand_template_id: str) -> dict:
    """List the autofillable fields (name + type) of a brand template."""
    token = access_token()
    return api.get(f"/brand-templates/{brand_template_id}/dataset", token)


def autofill(brand_template_id: str, data: dict,
             timeout_secs: int = 300) -> dict:
    """Fill a brand template's data fields; returns the new design.

    data maps field names (from template_dataset()) to values:
    text fields take strings, image fields take asset IDs or upload URLs.
    """
    token = access_token()
    job_id = api.post("/autofills", token,
                      {"brand_template_id": brand_template_id,
                       "data": data})["job"]["id"]
    job = api.poll_job(f"/autofills/{job_id}", token, timeout_secs=timeout_secs)
    return job["result"]["design"]


def export_design(design_id: str, fmt: str = "png",
                  timeout_secs: int = 300) -> list[dict]:
    """Export a design; returns a list of {url, ...} (one per page)."""
    if fmt not in EXPORT_FORMATS:
        raise ValueError(f"fmt must be one of {EXPORT_FORMATS}")
    token = access_token()
    job_id = api.post("/exports", token,
                      {"design_id": design_id, "format": {"type": fmt}})["job"]["id"]
    job = api.poll_job(f"/exports/{job_id}", token, timeout_secs=timeout_secs)
    return job["result"]["exports"] if "exports" in job["result"] else [job["result"]]


def download_export(export: dict, dest_path: str) -> str:
    urllib.request.urlretrieve(export["url"], dest_path)
    return dest_path


def upload_asset(file_path: str, name: str | None = None) -> dict:
    """Upload a local image to the user's Canva library; returns the asset."""
    token = access_token()
    name = name or os.path.basename(file_path)
    mime, _ = mimetypes.guess_type(file_path)
    boundary = "canvagen-boundary"
    with open(file_path, "rb") as f:
        file_bytes = f.read()
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="asset"; filename="{name}"\r\n'
        f"Content-Type: {mime or 'application/octet-stream'}\r\n\r\n"
    ).encode() + file_bytes + f"\r\n--{boundary}--\r\n".encode()
    req = urllib.request.Request(
        api.BASE + "/asset-uploads", data=body, method="POST",
        headers={"Authorization": f"Bearer {token}",
                 "Content-Type": f"multipart/form-data; boundary={boundary}"})
    with urllib.request.urlopen(req, timeout=120) as resp:
        import json
        return json.load(resp)["asset"]
