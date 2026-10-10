import pytest

from canvagen.generate import build_generation_payload


def test_payload_defaults():
    p = build_generation_payload("a cat", idempotency_key="k1")
    assert p["prompt"] == "a cat"
    assert p["aspect_ratio"] == "square"
    assert p["idempotency_key"] == "k1"
    assert p["asset_upload"] == {"type": "none"}
    assert "model" not in p  # let Canva pick by default


def test_payload_model_and_upload():
    p = build_generation_payload("logo", aspect_ratio="landscape",
                                 model="lucid_origin", save_to_canva=True,
                                 asset_name="my-logo", idempotency_key="k2")
    assert p["aspect_ratio"] == "landscape"
    assert p["model"] == "lucid_origin"
    assert p["asset_upload"] == {"type": "upload", "asset_name": "my-logo"}


def test_prompt_length_guarded():
    with pytest.raises(ValueError):
        build_generation_payload("")
    with pytest.raises(ValueError):
        build_generation_payload("x" * 2001)


def test_bad_aspect_ratio_and_model():
    with pytest.raises(ValueError):
        build_generation_payload("x", aspect_ratio="circle", idempotency_key="k")
    with pytest.raises(ValueError):
        build_generation_payload("x", model="nope", idempotency_key="k")
