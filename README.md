# Autonomous Content Creation - TFP Enterprises

This project uses [Poetry](https://python-poetry.org/) for dependency management.
Libraries across the codebase (e.g., `moviepy`, `wikipedia-api`, `gTTS`) are declared in `pyproject.toml`
and pinned via the `poetry.lock` file for repeatable installs.

## Installation

1. Install Poetry.
   ```bash
   pip install poetry
   ```
2. Install the locked dependencies.
   ```bash
   poetry install --no-root
   ```
3. Run the test suite to verify the setup.
   ```bash
   poetry run pytest
   ```

When dependencies change, regenerate the lock file:
```bash
poetry lock
```
