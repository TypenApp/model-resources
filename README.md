# Typen Local AI Model Resources (`TypenApp/model-resources`)

Optional **Layer 2 On-Device AI** model descriptors, hardware capability profiles, and Ed25519 manifest signing tools for [**Typen**](https://github.com/TypenApp/typen).

- **Main Application**: [`TypenApp/typen`](https://github.com/TypenApp/typen)
- **Language Data**: [`TypenApp/language-data`](https://github.com/TypenApp/language-data)
- **Documentation**: [`TypenApp/docs`](https://github.com/TypenApp/docs)

---

## How Layer 2 Local AI Works in Typen

Typen separates real-time keystroke correction from heavy neural inference so typing latency never degrades:

1. **Layer 1 (Always-On, `< 0.4ms`)**: Deterministic `mmap` lexicon + SymSpell + trigram context model (ships inside `TypenApp/typen` and `TypenApp/language-data`).
2. **Layer 2 (Local AI, On-Device)**: Quantized `ONNX` / `GGUF` sentence grammar and rewrite models managed by `LocalModelManager` (`src/autocorrect/ai/local_model_manager.py`) and verified by `ModelUpdater` (`src/autocorrect/updates/model_updater.py`).
   - Triggered **only** after a `>= 400ms` pause at a sentence boundary (via a non-focus-stealing Pause Pill) or via the explicit `Ctrl+Shift+R` hotkey.
   - Automatically unloads from RAM after `300s` (`MODEL_IDLE_UNLOAD_SECONDS`) of inactivity.

---

## Model Tiers & Hardware Profiles

| Model ID | Format | Minimum RAM | Recommended Hardware | Purpose |
| --- | --- | --- | --- | --- |
| `grammar-onnx-int8-small` | `onnx-int8` | 4,096 MB (4 GB) | DirectML / CoreML / CPU-AVX2 | Fast local sentence grammar verification |
| `rewrite-gguf-q4-360m` | `gguf-q4` | 16,384 MB (16 GB), 8+ cores | DirectML / CoreML / CPU-AVX2 | Local sentence rewrite and style refinement |

---

## Cryptographic Verification

Every model download is verified by `ModelUpdater.install_model_bytes()` before installation:
1. **Ed25519 Signature Check**: Canonical JSON (`model_id`, `version`, `released_at`, `format`, `min_ram_mb`, `size_bytes`, `sha256`) is verified against the embedded root public key:
   ```text
   79f7c2e422116b9597ae50d9c2f9e633d2f210b89a280983b52d6bce16344f78
   ```
2. **SHA-256 Checksum Verification**: Model bytes are hashed and compared against `descriptor.sha256` before atomic placement into the user's models directory.

## Validating the Catalog

```bash
pip install -e ".[dev]"
python scripts/sign_model_release.py --catalog model-catalog.json
pytest
```

## Licence

MIT. See [`LICENSE`](LICENSE).
