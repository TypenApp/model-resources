"""
Sign and verify Layer 2 Local AI model descriptors (`LocalModelDescriptor`)
using Typen's canonical Ed25519 signature scheme.
"""

from __future__ import annotations

import argparse
import base64
import json
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)

ROOT_PUBLIC_KEY_HEX = "79f7c2e422116b9597ae50d9c2f9e633d2f210b89a280983b52d6bce16344f78"
CANONICAL_KEYS = ("model_id", "version", "released_at", "format", "min_ram_mb", "size_bytes", "sha256")


def canonical_descriptor_dict(raw: dict[str, object]) -> dict[str, object]:
    return {k: raw[k] for k in CANONICAL_KEYS}


def canonicalize_json_bytes(payload: dict[str, object]) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sign_descriptor(descriptor: dict[str, object], private_key_hex: str) -> str:
    priv = Ed25519PrivateKey.from_private_bytes(bytes.fromhex(private_key_hex))
    raw = canonicalize_json_bytes(canonical_descriptor_dict(descriptor))
    return base64.b64encode(priv.sign(raw)).decode("ascii")


def verify_descriptor(
    descriptor: dict[str, object],
    signature_b64: str,
    public_key_hex: str = ROOT_PUBLIC_KEY_HEX,
) -> bool:
    try:
        pub = Ed25519PublicKey.from_public_bytes(bytes.fromhex(public_key_hex))
        raw = canonicalize_json_bytes(canonical_descriptor_dict(descriptor))
        pub.verify(base64.b64decode(signature_b64), raw)
        return True
    except Exception:
        return False


def validate_catalog(catalog_path: Path) -> int:
    data = json.loads(catalog_path.read_text(encoding="utf-8"))
    assert data["schema_version"] == 1
    assert data["ed25519_public_key_hex"] == ROOT_PUBLIC_KEY_HEX
    models = data["models"]
    assert len(models) >= 2
    for m in models:
        canon = canonical_descriptor_dict(m)
        assert len(str(canon["sha256"])) == 64
        assert int(canon["min_ram_mb"]) >= 4096
    print(f"Validated {len(models)} model descriptors in {catalog_path}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path, default=Path("model-catalog.json"))
    args = parser.parse_args(argv)
    return validate_catalog(args.catalog)


if __name__ == "__main__":
    raise SystemExit(main())
