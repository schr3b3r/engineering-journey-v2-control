#!/usr/bin/env python3
"""Evaluator adapter: wraps the deliverable's own harness.loop.run() so
coordinator/run_milestone.py can invoke it as HARNESS_EVALUATOR_CMD.

Reads the documented env var contract, gives the model a task explicitly
scoped to independently GRADING the milestone (not building it), and
requires the model's final answer to include the exact
'overall: PASS|FAIL' / 'test_runner: PASS|FAIL' lines
coordinator/run_milestone.py's parse_verdict() looks for -- printed to
stdout so the Coordinator can capture and parse it.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def main() -> int:
    role = os.environ.get("HARNESS_ROLE")
    if role != "evaluator":
        print(f"evaluator_adapter.py invoked with unexpected HARNESS_ROLE={role!r}", file=sys.stderr)
        return 1

    milestone = os.environ["HARNESS_MILESTONE"]
    spec_path = Path(os.environ["HARNESS_SPEC"])
    context = os.environ["HARNESS_CONTEXT"]
    deliverable = Path(os.environ["HARNESS_DELIVERABLE"])

    spec_text = spec_path.read_text() if spec_path.is_file() else "(spec.md not found)"

    task = (
        f"You are the Evaluator for milestone {milestone}. You did NOT write "
        f"this code -- grade it independently and skeptically.\n\n"
        f"# Full spec\n\n{spec_text}\n\n"
        f"# This milestone's scope and done criteria\n\n{context}\n\n"
        f"# Your job\n\n"
        f"1. Inspect the actual committed state of this repo (git log, git "
        f"diff, read the real files) -- grade what was actually committed, "
        f"not an uncommitted worktree.\n"
        f"2. If a test suite exists under app/tests/, RUN IT FOR REAL "
        f"(cd app && RUN_LIVE_TESTS=1 python -m pytest) using run_command "
        f"-- do not substitute reading the code for actually executing "
        f"the tests. Some tests may skip live network calls unless "
        f"RUN_LIVE_TESTS=1 is set; always set it so live-Fulcra/live-"
        f"GitHub integration tests actually run, not just mocked unit "
        f"tests -- this project's real bugs so far were only caught by "
        f"live execution, never by the mocked suite alone.\n"
        f"3. Check the milestone's 'Done when' criteria specifically -- "
        f"not just 'does code exist', but does it actually do what's "
        f"claimed (e.g. a real kill/resume demonstration, not just code "
        f"that looks resumable).\n"
        f"4. Your final answer MUST include these exact lines, each on "
        f"its own line:\n"
        f"overall: PASS\n"
        f"(or)\n"
        f"overall: FAIL\n"
        f"and, if a test runner was run:\n"
        f"test_runner: PASS\n"
        f"(or)\n"
        f"test_runner: FAIL\n"
        f"Include the real command and output/count evidence you used to "
        f"reach these lines, plus a concise summary. A permission problem "
        f"running the tests is itself a FAIL, never a reason to grade by "
        f"code-reading alone."
    )

    venv_python = deliverable / ".venv" / "bin" / "python"
    python_bin = str(venv_python) if venv_python.is_file() else sys.executable

    result = subprocess.run(
        [python_bin, "-c",
         "import sys; sys.path.insert(0, '.'); "
         "from dotenv import load_dotenv; load_dotenv(); "
         "from harness.loop import run; "
         "r = run(task=sys.stdin.read(), max_iterations=45, include_app_context=False); "
         "print(r.final_text or '')"],
        cwd=deliverable,
        input=task,
        text=True,
        capture_output=True,
    )
    # Evaluator's verdict text must reach stdout for run_milestone.py's
    # parse_verdict() to find the required lines -- pass through both the
    # child's own stdout (which already contains the model's final_text)
    # and stderr (transcript/progress) for visibility.
    print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
