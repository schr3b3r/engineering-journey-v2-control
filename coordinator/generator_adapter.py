#!/usr/bin/env python3
"""Generator adapter: wraps the deliverable's own harness.loop.run() so
coordinator/run_milestone.py can invoke it as HARNESS_GENERATOR_CMD.

Reads the documented env var contract (HARNESS_ROLE, HARNESS_MILESTONE,
HARNESS_SPEC, HARNESS_CONTEXT, HARNESS_DELIVERABLE) and turns it into a
real task string for the deliverable's own harness/loop.py -- the same
Gemini-backed control loop the deliverable's own smoke tests already
proved works, not a separate hand-rolled model call.

Run from the deliverable repo root (HARNESS_DELIVERABLE), since
harness.loop imports assume that cwd (per the deliverable's own
run_task.py convention).
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def main() -> int:
    role = os.environ.get("HARNESS_ROLE")
    if role != "generator":
        print(f"generator_adapter.py invoked with unexpected HARNESS_ROLE={role!r}", file=sys.stderr)
        return 1

    milestone = os.environ["HARNESS_MILESTONE"]
    spec_path = Path(os.environ["HARNESS_SPEC"])
    context = os.environ["HARNESS_CONTEXT"]
    deliverable = Path(os.environ["HARNESS_DELIVERABLE"])

    spec_text = spec_path.read_text() if spec_path.is_file() else "(spec.md not found)"

    task = (
        f"You are the Generator for milestone {milestone} of this project's "
        f"control-harness-driven build.\n\n"
        f"# Full spec (for cross-cutting invariants -- work ONLY the milestone "
        f"scope below, not the whole spec)\n\n{spec_text}\n\n"
        f"# This milestone's scope and done criteria\n\n{context}\n\n"
        f"# Your job\n\n"
        f"Build exactly this milestone's scope, following "
        f"app/ENGINEERING_STANDARDS.md. Run the real test suite (cd app "
        f"&& RUN_LIVE_TESTS=1 python -m pytest) before considering it "
        f"done -- set RUN_LIVE_TESTS=1 so any live-Fulcra/live-GitHub "
        f"integration tests actually execute rather than silently "
        f"skipping; this project's real bugs so far were only caught by "
        f"live execution. Commit your work using the git_commit tool "
        f"(this repo's test gate will refuse a commit if tests are red). "
        f"Do not merge and do not touch spec.md or decisions.md -- those are "
        f"user-owned. If you hit a genuine user-only judgment call, stop and "
        f"say so explicitly rather than guessing.\n\n"
        f"IMPORTANT: you have a bounded number of tool-call round-trips. "
        f"Commit your work as soon as it is real and tested -- do not save "
        f"the commit for last if you are running low on remaining "
        f"iterations, since uncommitted work cannot be evaluated or "
        f"merged. It is far better to commit working code for a slightly "
        f"reduced scope than to run out of iterations with excellent but "
        f"uncommitted work."
    )

    # Use the deliverable's own venv Python (where its dependencies are
    # actually installed), not sys.executable (this adapter script's own
    # interpreter, which has no reason to have the deliverable's deps).
    venv_python = deliverable / ".venv" / "bin" / "python"
    python_bin = str(venv_python) if venv_python.is_file() else sys.executable

    result = subprocess.run(
        [python_bin, "-c",
         "import sys; sys.path.insert(0, '.'); "
         "from dotenv import load_dotenv; load_dotenv(); "
         "from harness.loop import run; "
         "import json; "
         "r = run(task=sys.stdin.read(), max_iterations=80); "
         "print('\\n=== FINAL TEXT ===\\n', r.final_text); "
         "print('\\nstopped_reason:', r.stopped_reason)"],
        cwd=deliverable,
        input=task,
        text=True,
    )
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
