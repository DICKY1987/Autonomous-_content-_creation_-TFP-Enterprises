# Automated Content Creation System — Testing Suite

This package provides a **complete, modular testing system** for your automated content creation stack.
It includes **unit, integration, end‑to‑end (E2E), and non‑functional** tests, plus a YAML‑driven scenario runner,
local commands, and a GitHub Actions workflow.

## What’s inside
```
automated_content_testing_system/
├─ README_TESTING.md
├─ pyproject.toml
├─ requirements-dev.txt
├─ pytest.ini
├─ Makefile
├─ .env.example
├─ qa_scenarios/
│  ├─ smoke_short.yaml
│  ├─ history_harriet_tubman.yaml
│  ├─ performance_batch_10.yaml
│  └─ e2e_daily_production.yaml
├─ qa_runner/
│  ├─ __init__.py
│  ├─ scenario_models.py
│  └─ run_suite.py
├─ tests/
│  ├─ conftest.py
│  ├─ unit/
│  │  ├─ test_research_engine.py
│  │  ├─ test_content_system.py
│  │  ├─ test_upload_system.py
│  │  └─ test_platform_specs.py
│  ├─ integration/
│  │  ├─ test_research_to_script.py
│  │  ├─ test_video_assembly_flow.py
│  │  └─ test_upload_flow_mocked.py
│  ├─ e2e/
│  │  └─ test_daily_production_e2e.py
│  └─ nonfunctional/
│     ├─ test_performance_timings.py
│     ├─ test_scalability_stub.py
│     └─ test_copyright_safety_stub.py
└─ .github/workflows/
   └─ tests.yml
```

## Quick start
```bash
# From the repo root (where your system files live), copy this folder in:
# Or unzip the zip you downloaded.

cd automated_content_testing_system

# Install dev deps (in a venv recommended)
pip install -r requirements-dev.txt

# Configure environment for tests (optional)
cp .env.example .env

# Run all tests
pytest -q

# Or run the YAML scenario runner (reads qa_scenarios/*.yaml)
python -m qa_runner.run_suite --suite qa_scenarios/smoke_short.yaml
```

## Notes
- Tests are written to **avoid hitting live external APIs**. We use mocking for HTTP and SDK calls.
- E2E tests are **safe-mode by default** (no public uploads). You can enable real uploads by setting env flags.
- The suite discovers your modules by their expected filenames:
  - `automated_content_system.py` (AutomatedContentSystem, ContentConfig)
  - `upload_system.py` (MultiPlatformUploader, MetadataGenerator, ThumbnailGenerator, YouTubeUploader)
  - `main_execution_system.py` (HistoricalContentBusinessSystem or your main orchestrator)
  - `omnichannel_implementation.py` (PlatformSpecsManager, ContentAdapter) — optional
  - `platform_apis.py` (YouTubeAPIClient, TikTokAPIClient, FacebookAPIClient) — optional

If your filenames differ, update the imports at the top of test files accordingly.
