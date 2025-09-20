"""Compatibility shim for tests.

Re-exports the ``HistoricalContentBusinessSystem`` from
``scripts.main_execution_system`` so tests can import it from the project root.
"""
from scripts.main_execution_system import HistoricalContentBusinessSystem  # noqa: F401

__all__ = ["HistoricalContentBusinessSystem"]

