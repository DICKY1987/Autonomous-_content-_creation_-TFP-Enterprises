"""Canonical content system entry point.

This module provides a stable import surface for the project by re-exporting
the lightweight, test-friendly implementation from ``src.core.automated_content_system``.

Usage
-----
- from content_system import AutomatedContentSystem, ContentConfig
- from content_system import QualityReport

The heavy implementation in ``src/core/content_system.py`` remains available for
local experimentation, while CI and tests rely on this deterministic variant.
"""

from src.core.automated_content_system import (
    AutomatedContentSystem,
    ContentConfig,
    QualityReport,
    ContentResearchEngine,
    QualityAssuranceModule,
)

__all__ = [
    "AutomatedContentSystem",
    "ContentConfig",
    "QualityReport",
    "ContentResearchEngine",
    "QualityAssuranceModule",
]

