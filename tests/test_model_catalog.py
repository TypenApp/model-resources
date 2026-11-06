from __future__ import annotations

import json
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from scripts.sign_model_release import (
     canonical_descriptor_dict,
    sign_descriptor,
    validate_catalog,
    verify_descriptor,
)

ROOT = Path(__file__).resolve().parent.parent


def test_model_catalog_and_descriptors_are_valid() -> None:
    assert validate_catalog(ROOT / "model-catalog.json") == 0
    catalog = json.loads((ROOT / "model-catalog.json").read_text(encoding="utf-8"))
    for model in catalog["models"]:
        desc_file = ROOT / "descriptors" / f"{model['model_id']}.json"
        assert desc_file.exists()
        assert json.loads(desc_file.read_text(encoding="utf-8")) == model


def test_ed25519_roundtrip_on_model_descriptor() -> None:
    priv = Ed25519PrivateKey.generate()
    priv_hex = priv.private_bytes_raw().hex()
    pub_hex = priv.public_key().public_bytes_raw().hex()
    desc = json.loads((ROOT / "descriptors" / "grammar-onnx-int8-small.json").read_text(encoding="utf-8"))
    sig = sign_descriptor(desc, priv_hex)
    assert verify_descriptor(desc, sig, pub_hex)
    tampered = dict(canonical_descriptor_dict(desc), size_bytes=123)
    assert not verify_descriptor(tampered, sig, pub_hex)
