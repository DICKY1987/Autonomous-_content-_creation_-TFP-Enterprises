import os
import pathlib
import pytest
from contextlib import contextmanager

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
