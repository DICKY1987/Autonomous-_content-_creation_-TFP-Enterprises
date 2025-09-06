import os
import pathlib
import sys
import pytest
from contextlib import contextmanager

# Ensure project root is importable when tests run from this directory.
# ``parents[1]`` points to the repository root (the directory containing the
# ``tests`` folder).  The previous implementation incorrectly used
# ``parents[2]`` which resolved to ``/workspace`` in the execution environment,
# leaving the actual project code off ``sys.path`` and causing ``ModuleNotFoundError``
# for imports such as ``import src``.
ROOT_DIR = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

@pytest.fixture(autouse=True, scope="session")
def _set_env():
    os.environ.setdefault("DISABLE_REAL_UPLOADS", "1")
    os.environ.setdefault("PEXELS_API_KEY", "fake-key-for-tests")

@pytest.fixture
def tmp_project_dir(tmp_path):
    d = tmp_path / "content_project"
    d.mkdir()
    return d

@contextmanager
def does_not_raise():
    yield

@pytest.fixture
def does_not_raise_ctx():
    return does_not_raise
