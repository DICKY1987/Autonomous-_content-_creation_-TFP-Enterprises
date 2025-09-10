#!/usr/bin/env python3
"""Process monitoring and self-healing agent.

This module provides a ``ProcessGuardian`` class that launches and
monitors external commands.  If a process exits unexpectedly, the
guardian waits for a short delay and restarts it, providing simple
self‑healing behavior.

Example
-------
>>> from process_guardian import ProcessSpec, ProcessGuardian
>>> specs = [ProcessSpec(name="content", command=["python", "automated_content_system.py"])]
>>> guardian = ProcessGuardian(specs)
>>> guardian.run()

The guardian keeps the main thread alive and watches each child process
in a background thread.  Logs are emitted to both STDOUT and a file
named ``process_guardian.log``.
"""

import subprocess
import threading
import time
from dataclasses import dataclass
from typing import List, Optional

from src.core.logging_config import get_logger


@dataclass
class ProcessSpec:
    """Configuration describing a managed process."""
    name: str
    command: List[str]
    restart_delay: float = 5.0
    max_restarts: Optional[int] = None


class ProcessGuardian:
    """Starts and monitors a collection of processes."""

    def __init__(self, specs: List[ProcessSpec]):
        self.specs = specs
        self.log = get_logger(__name__)

    def _monitor(self, spec: ProcessSpec) -> None:
        restarts = 0
        while spec.max_restarts is None or restarts < spec.max_restarts:
            self.log.info("Starting %s: %s", spec.name, " ".join(spec.command))
            proc = subprocess.Popen(spec.command)
            ret = proc.wait()
            self.log.warning("%s exited with code %s", spec.name, ret)
            restarts += 1
            time.sleep(spec.restart_delay)
        self.log.error("%s reached max restarts (%s)", spec.name, spec.max_restarts)

    def run(self) -> None:
        """Launch threads for each process and keep the guardian alive."""
        for spec in self.specs:
            thread = threading.Thread(target=self._monitor, args=(spec,), daemon=True)
            thread.start()
        while True:
            time.sleep(3600)


if __name__ == "__main__":
    # Example usage: monitor the automated content system
    guardian = ProcessGuardian([
        ProcessSpec(name="content_system", command=["python", "automated_content_system.py"])
    ])
    guardian.run()
