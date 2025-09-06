import json

from src.cloud.config_sync import load_config_from_parameter_store, sync_config_to_parameter_store


class DummySSMClient:
    """Minimal stand-in for the AWS SSM client used in tests."""

    def __init__(self):
        self.params: dict[str, dict[str, str]] = {}

    def put_parameter(self, *, Name: str, Value: str, Type: str, Overwrite: bool) -> None:  # noqa: D401 - method docs unnecessary
        self.params[Name] = {"Value": Value}

    def get_parameter(self, *, Name: str, WithDecryption: bool) -> dict[str, dict[str, str]]:  # noqa: D401 - method docs unnecessary
        return {"Parameter": self.params[Name]}


def test_sync_config_to_parameter_store_puts_parameters():
    config = {"alpha": {"enabled": True}}
    client = DummySSMClient()
    sync_config_to_parameter_store(config, "/test/", ssm=client)
    assert client.params["/test/alpha"]["Value"] == json.dumps(config["alpha"])


def test_load_config_from_parameter_store_reads_parameters():
    template = {"beta": {}}
    value = {"threshold": 5}
    client = DummySSMClient()
    client.params["/test/beta"] = {"Value": json.dumps(value)}
    result = load_config_from_parameter_store(template, "/test/", ssm=client)
    assert result == {"beta": value}
