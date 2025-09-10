"""Utilities for synchronizing omnichannel configuration with AWS Parameter Store.

These helpers provide a thin abstraction for pushing a configuration dictionary to
AWS Systems Manager Parameter Store and retrieving it again. The implementation
uses :mod:`boto3` but avoids any direct dependency on project specific modules so
that it can be reused across services.
"""
from __future__ import annotations

from typing import Any, Dict, Optional, Iterable
import json
import os

try:  # pragma: no cover - optional dependency
    import boto3  # type: ignore
    from botocore.exceptions import BotoCoreError, ClientError  # type: ignore
except Exception:  # pragma: no cover - boto3 not available
    boto3 = None  # type: ignore

    class BotoCoreError(Exception):
        """Fallback error used when boto3 isn't installed."""

    class ClientError(Exception):
        """Fallback error used when boto3 isn't installed."""


def _get_ssm_client(ssm: Optional[Any] = None):
    if ssm is not None:
        return ssm
    if boto3 is None:  # pragma: no cover - environment without boto3
        raise RuntimeError("boto3 is required for AWS operations")
    return boto3.client("ssm")


def sync_config_to_parameter_store(
    config: Dict[str, Any], prefix: str, ssm: Optional[Any] = None
) -> None:
    """Store configuration values in AWS Parameter Store.

    Each top level key in ``config`` is stored as a JSON encoded ``String`` under
    ``prefix``. Existing parameters with the same name will be overwritten.

    Parameters
    ----------
    config:
        Mapping containing the configuration to persist. Values must be JSON
        serialisable.
    prefix:
        Parameter name prefix, e.g. ``"/omnichannel/"``.
    """
    client = _get_ssm_client(ssm)
    for key, value in config.items():
        name = f"{prefix}{key}"
        try:
            client.put_parameter(
                Name=name,
                Value=json.dumps(value),
                Type="String",
                Overwrite=True,
            )
        except (BotoCoreError, ClientError) as exc:  # pragma: no cover - network errors
            raise RuntimeError(f"Failed to store parameter {name!r}: {exc}") from exc


def load_config_from_parameter_store(
    keys: Dict[str, Any], prefix: str, ssm: Optional[Any] = None
) -> Dict[str, Any]:
    """Load a configuration mapping from AWS Parameter Store.

    ``keys`` acts as a template describing which parameters to retrieve. Only the
    top level keys are used; the values are ignored but preserve the expected
    structure of the returned mapping.

    Parameters
    ----------
    keys:
        Mapping whose keys determine which parameters to fetch.
    prefix:
        Prefix used when the configuration was stored.
    """
    client = _get_ssm_client(ssm)
    result: Dict[str, Any] = {}
    for key in keys:
        name = f"{prefix}{key}"
        try:
            response = client.get_parameter(Name=name, WithDecryption=True)
            result[key] = json.loads(response["Parameter"]["Value"])
        except (BotoCoreError, ClientError) as exc:  # pragma: no cover - network errors
            raise RuntimeError(f"Failed to load parameter {name!r}: {exc}") from exc
    return result


def load_credentials(
    keys: Iterable[str], prefix: str = "/autocontent/", ssm: Optional[Any] = None
) -> Dict[str, Optional[str]]:
    """Retrieve secret values from Parameter Store with environment fallback.

    Parameters
    ----------
    keys:
        Iterable of parameter names to load. Names should match the environment
        variable convention (e.g. ``"PEXELS_API_KEY"``).
    prefix:
        Parameter name prefix used in AWS. Defaults to ``"/autocontent/"``.
    ssm:
        Optional boto3 SSM client for testing.

    Returns
    -------
    Dict[str, Optional[str]]
        Mapping of requested keys to their resolved values. If a key cannot be
        loaded from Parameter Store the value from :mod:`os.environ` is used
        instead. Missing keys default to ``None``.
    """
    template = {k: None for k in keys}
    creds: Dict[str, Optional[str]] = {k: None for k in keys}
    try:  # pragma: no cover - network and boto3 not exercised in tests
        loaded = load_config_from_parameter_store(template, prefix, ssm)
        creds.update(loaded)
    except Exception:
        pass
    for key in keys:
        if not creds.get(key):
            creds[key] = os.getenv(key)
    return creds
