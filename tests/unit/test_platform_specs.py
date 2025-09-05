import importlib
import pytest

@pytest.mark.skip(reason="Optional module")
def test_platform_specs_manager_exists():
    m = importlib.import_module("omnichannel_implementation")
    Manager = getattr(m, "PlatformSpecsManager")
    manager = Manager()
    yt = manager.get_spec("youtube")
    assert yt.aspect_ratio == "9:16"
