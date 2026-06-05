"""
Backend test configuration — shared fixtures and module-level patches.

This conftest runs BEFORE any test module is imported, making it the right
place to mock heavy external dependencies (HuggingFace model downloads, DB
connections, etc.) that are not available in the CI environment.
"""

from __future__ import annotations

import sys
from unittest.mock import MagicMock, patch


# ---------------------------------------------------------------------------
# 1. Mock the embedding engine so SentenceTransformer is never loaded.
#
#    The scoring pipeline calls embed_texts() for semantic responsibility
#    matching.  Returning zero vectors lets skill-based scoring run fully
#    (it uses text/keyword matching) while semantic similarity contributes 0.
#    All Phase 3 guardrail / schema / evidence tests still pass because they
#    focus on the structure of the result dict, not the exact numeric scores.
# ---------------------------------------------------------------------------

def _fake_embed_texts(texts: list[str]) -> list[list[float]]:
    """Return zero vectors matching the input list length."""
    dim = 384  # all-MiniLM-L6-v2 embedding dimension
    return [[0.0] * dim for _ in texts]


# Patch the module itself so that any import style (from … import * or
# import …) resolves to the fake before the real module is ever touched.
_scoring_modules = [
    "app.services.scoring.scorer",
    "app.services.scoring.result_v2",
    "app.services.scoring",
]

for _mod in _scoring_modules:
    if _mod in sys.modules:
        # clear already-imported sub-modules so they pick up the patched parent
        to_remove = [k for k in sys.modules if k.startswith(_mod)]
        for _k in to_remove:
            sys.modules.pop(_k, None)

# Apply patch before any test code runs
_embedding_patch = patch(
    "app.services.embedding.engine.embed_texts",
    side_effect=_fake_embed_texts,
)
_embedding_patch.start()
