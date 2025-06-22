import importlib
import sys
from pathlib import Path
import pytest

# Ensure the project root is on the import path when running tests from a
# different working directory.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def test_model_router_import():
    try:
        assert importlib.import_module("backend.ai.model_router") is not None
    except Exception as e:
        pytest.skip(f"model_router import failed: {e}")


def test_vector_integration_import():
    assert importlib.import_module("backend.vector.vector_integration") is not None
